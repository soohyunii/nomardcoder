import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import StructuredTool, Tool, BaseTool
from pydantic import BaseModel, Field
from typing import Type
from langchain.tools.ddg_search import DuckDuckGoSearchRun
import os, requests
# from langchain_core.messages.system import SystemMessage - 로컬에서 LangChain 버전 조합이 꼬였을 때는 core 경로가 pydantic 호환 문제를 더 잘 드러냄
from langchain.schema import SystemMessage





llm = ChatOpenAI(temperature=0.1)



alpha_vantage_api_key = os.environ.get("ALPHAVANTAGE_API_KEY")


class StockMarketSymbolSearchToolArgsSchema(BaseModel):
    query: str = Field(description="The query you will search for")


class StockMarketSymbolSearchTool(BaseTool):
    name = "StockMarketSymbolSearchTool"
    description = """
    Use this tool to find the stock market symbol for a company in ENGLISH.
    It takes a query as an argument.
    Example query: Stock Market Symbol for Apple Company
    """
    args_schema: Type[StockMarketSymbolSearchToolArgsSchema] = StockMarketSymbolSearchToolArgsSchema
    def _run(self, query):
        # ddg = DuckDuckGoSearchAPIWrapper()
        # ddg = DuckDuckGoSearchResults()
        ddg = DuckDuckGoSearchRun()
        return ddg.run(query)
        



class CompanyOverviewArgsSchema(BaseModel):
    
    symbol: str = Field(description="Stock Symbol of the company. Example: AAPL, TSLA")

class CompanyOverviewTool(BaseTool):
    name = "CompanyOverviewTool"
    description = """
    Use this to get an overview of the financials of the company.
    You should enter a stock symbol.
    """
    
    args_schema: Type[CompanyOverviewArgsSchema] = CompanyOverviewArgsSchema
    
    def _run(self, symbol):
        r = requests.get(f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={alpha_vantage_api_key}")
        return r.json()
    
    
class CompanyIncomeStatementTool(BaseTool):
    name = "CompanyIncomeStatementTool"
    description = """
    Use this to get income statement the company.
    You should enter a stock symbol.
    """
    
    args_schema: Type[CompanyOverviewArgsSchema] = CompanyOverviewArgsSchema
    
    def _run(self, symbol):
        r = requests.get(f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={alpha_vantage_api_key}")
        return r.json()
    
    
class CompanyStockDailyTool(BaseTool):
    name = "CompanyStockDailyTool"
    description = """
    Use this to get Daily performance of a company stock.
    You should enter a stock symbol.
    """
    
    args_schema: Type[CompanyOverviewArgsSchema] = CompanyOverviewArgsSchema
    
    def _run(self, symbol):
        r = requests.get(f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={alpha_vantage_api_key}")
        return r.json()
    
    
agent = initialize_agent(
    llm=llm,
    verbose=True,
    agent=AgentType.OPENAI_FUNCTIONS, 
    tools=[
        StockMarketSymbolSearchTool(),
        CompanyOverviewTool(),
        CompanyIncomeStatementTool(),
        CompanyStockDailyTool()
    ],
    agent_kwargs={
        "system_message": SystemMessage(content="""
            You are a hedge fund manager.
            
            You evaluate a company and provide your opinion and reason why the stock is a buy or not.
            
            Consider the performance of a stock, the company overview and the income statement.
            
            Be assertive in your judgement and recommend the stock or advise the user against it.         
        """)
    }
)





st.markdown(
    """
    # InvestorGPT
    
    Welcome to InvestorGPT.
    
    Write down the name of a company and our Agent will do the research for you.
    """
)


company = st.text_input("Write the name of the company you are interested on.")

if company:
    result = agent.invoke(company)
    
    st.write(result["output"])