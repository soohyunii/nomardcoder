import streamlit as st
import time
from langchain.prompts import ChatPromptTemplate
from langchain.storage import LocalFileStore
from langchain.embeddings import CacheBackedEmbeddings, OllamaEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema.runnable import RunnableLambda
from langchain.schema.runnable import RunnablePassthrough
# from langchain.chat_models import ChatOpenAI
from langchain.chat_models import ChatOllama
from langchain.callbacks.base import BaseCallbackHandler
from pathlib import Path


# if "messages" not in st.session_state:
#     st.session_state["messages"] = []
    

class ChatCallbackHandler(BaseCallbackHandler):
    message = ""
    
    def on_llm_start(self, *args, **kwargs):
        self.message_box = st.empty()
            
    def on_llm_end(self, *args, **kwargs):
        save_message(self.message, "ai")
            
    def on_llm_new_token(self, token, *args, **kwargs):
        self.message += token
        self.message_box.markdown(self.message)

    


# llm = ChatOpenAI(
llm = ChatOllama(
    model="mistral:latest",
    temperature=0.1,
    streaming=True,
    callbacks=[
        ChatCallbackHandler(),
    ]
)


# how to !cache! like this heavy function?
@st.cache_data(show_spinner="Embedding file....")
def embed_file(file):
    file_content = file.read()
    file_path = f"./.cache/private_files/{file.name}"
    # p = Path(file_path)
    # st.write("Saved:", file_path, "size:", p.stat().st_size)
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    cache_dir = LocalFileStore(f"./.cache/private_embeddings/{file.name}")
    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=600,
        chunk_overlap=100,
    )
    # real_path = (Path(__file__).resolve().parent.parent / ".cache" / "files")
    loader = UnstructuredFileLoader(file_path)
    docs = loader.load_and_split(text_splitter=splitter)
    # embeddings = OpenAIEmbeddings()
    embeddings = OllamaEmbeddings(
        model="mistral:latest"
    )
    cached_embeddings = CacheBackedEmbeddings.from_bytes_store(
        embeddings, cache_dir
    )
    vectorstore = FAISS.from_documents(docs, cached_embeddings)
    # 260127 : retriver에 대한 복습 필요
    retriver = vectorstore.as_retriever()
    
    return retriver


def save_message(message, role):
    st.session_state["messages"].append({"message": message, "role": role})

def send_message(message, role, save=True):
    with st.chat_message(role):
        st.markdown(message)
    if save:
        save_message(message, role)

# show message already done
def paint_history():
    for message in st.session_state["messages"]:
        send_message(
            message["message"],
            message["role"],
            save=False
        )



def format_docs(docs):
    return "\n\n".join(document.page_content for document in docs)


prompt = ChatPromptTemplate.from_template(
"""
    Answer the question using ONLY the following context and not your training data. If you don't know the answer,
    just say you don't know. DON'T make anything up.
     
    Context: {context}
    Question: {question}
"""
)


st.title("PrivateGPT")


st.markdown("""
Welcome!

Use this chatbot to ask questions to an AI about your files!

Upload your files on the sidebar.
""")

with st.sidebar:
    file = st.file_uploader(
        "Upload a .txt .pdf or .docx file", 
        type=["pdf", "txt", "docx"]
    )


if file:
    retriever = embed_file(file)
    send_message("I'm ready! Ask away!", "ai", save=False)
    paint_history()
    message = st.chat_input("Ask anything about your file...")
    
    if message:
        send_message(message, "human")
        chain = ({
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough()
        } | prompt | llm)
        
        # We are not using chain
        with st.chat_message("ai"):
            chain.invoke(message)
        
        
else:
    # at first, initialize
    st.session_state["messages"] = []