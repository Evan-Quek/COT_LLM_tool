import os, json
import pandas as pd

from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

embedding_function = HuggingFaceEmbeddings(model_name="C:/Users/evanq/Documents/EAS_Work/CTIA/git/main/models/thenlper_gte-large/")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)


FILE_PATH = "market_data/c_year.xlsx"
MARKET_LIST = ["WHEAT", "CORN", "OATS", "SOYBEANS", "SOYBEAN OIL", "CRUDE OIL, LIGHT SWEET", "LEAN HOGS", "LIVE CATTLE", "FEEDER CATTLE"]

if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists("vectors_db"):
    os.makedirs("vectors_db")


def get_data(query, llm):
    market = routing_agent(query, llm)
    if os.path.exists(f"vectors_db/{market}"):
        print(f"{market} vector db already exists!")
        return Chroma(persist_directory=f"vectors_db/{market}", embedding_function=embedding_function), market

    else:
        data = pd.read_excel(FILE_PATH)
        data['Date'] = data['Date'].astype(str)
        data["Market"] = data["Market"].str.strip()
        
        data = data[data["Market"] == market].reset_index(drop=True)
        data.to_csv(f"data/{market}.csv", index=False)
        json_data = data.to_json()
        with open(f"data/{market}.txt", "w") as f:
            f.write(json.dumps(json_data, indent=4))
    
        loader = TextLoader(f"data/{market}.txt")
        docs = loader.load()
        return Chroma.from_documents(documents=docs,
                                     embedding=embedding_function,
                                     persist_directory=f"vectors_db/{market}"), market

def get_response(query, llm):
    db, market = get_data(query, llm)
    retriever = db.as_retriever(search_type="similarity")
    qa_chain = RetrievalQA.from_chain_type(llm=llm,
                                           chain_type="stuff",
                                           retriever=retriever,
                                           return_source_documents=True)
    prompt = get_analyst_prompt(query)
    llm_response = qa_chain.invoke(prompt)
    return llm_response['result'], market

def routing_agent(query, llm):
    '''
    Classifies the query to determine the market.
    '''
    prompt = PromptTemplate.from_template("""Given the user query below, perform a classification task. Classify which market does the query belongs to.
    Do not respond with more than the category name.
    
    <categories>
    {market_list}                                                                        
    </categories>    
    
    <question>
    {question}
    </question>
    
    Market:""")
    
    chain = prompt | llm | StrOutputParser()
    
    return chain.invoke({"question": query, "market_list": MARKET_LIST})

def get_analyst_prompt(query):
    prompt = f"""Act as a professional futures market analyst. You are given a JSON data from COT.
    The data is arranged in descending order, starting from the latest entry.
    You must analyze the trends before answering.
    Explain the trends in detail.

    Question: {query}
    Answer:"""
    return prompt

