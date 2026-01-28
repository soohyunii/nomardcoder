import streamlit as st
from langchain.prompts import PromptTemplate
from datetime import datetime

today = datetime.today().strftime("%H:%M:%S")

st.title(today)

# there is sooooo many function(==widget) using streamlit! Let's see
# st.title("Hello world!")

# st.subheader("Welcome to Streamlit")

# st.markdown(""" 
#     #### I love it!

# """)

# st.write("hello")
# st.write([1,2,3,4,5])
# st.write({"x":1})

a = [1,2,3,4]

d = {"y":2}

# also, streamlit can show class type like this
# st.write(PromptTemplate)
# or just write PromptTemplate

p = PromptTemplate.from_template("xxxx")

# st.write(p)
# or just write variable
# a
# d
# p

model = st.selectbox("Choose yout model", ("GPT-3", "GPT-4"))

if model == "GPT-3":
    st.write("cheap")
else:
    st.write("not cheap")

    # streamlit's data flow : whole page refresh!!!
    name = st.text_input("What is your name?")
    name



value = st.slider("temperature", min_value=0.1, max_value=1.0)
value


import streamlit as st

st.title("title")

with st.sidebar:
    st.title("sidebar title")
    st.text_input("somthing")

tab_one, tab_two, tab_three = st.tabs(["A","B","C"])

with tab_one:
    st.write('a')

with tab_two:
    st.write('b')


with tab_three:
    st.write("c")


import streamlit as st
import time

st.title("DocumentGPT")

with st.chat_message("human"):
    st.write("Hellooooooooo")

with st.chat_message("ai"):
    st.write("how are you")

st.chat_input("Send a message to the ai")

with st.status("Embedding file...", expanded=True) as status:
    time.sleep(2)
    st.write("Getting the file")
    time.sleep(2)
    st.write("Embedding the file")
    time.sleep(2)
    st.write("Caching the file")
    status.update(label="Error", state="error")







if "messages" not in st.session_state:
    # session state : it helps not to refresh data
    st.session_state["messages"] = []


def send_message(message, role, save=True):
    with st.chat_message(role):
        st.write(message)
    if save:
        st.session_state["messages"].append({"message":message, "role":role})

for message in st.session_state["messages"]:
    send_message(message["message"], message["role"], save=False)


message = st.chat_input("Send a message to the ai")

if message:
    send_message(message, "human")
    time.sleep(1)
    send_message(f"You said {message}", "ai")

    with st.sidebar:
        st.write(st.session_state)
