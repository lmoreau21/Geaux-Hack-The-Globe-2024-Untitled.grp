from datetime import datetime
# Create your views here.
from rest_framework.response import Response
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.retrievers import BM25Retriever
from langchain.retrievers.merger_retriever import MergerRetriever
from langchain.retrievers.document_compressors import CohereRerank
from langchain.retrievers import ContextualCompressionRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import MessagesPlaceholder, HumanMessage, AIMessage
import os
import re
import pickle
import json
import time

from dotenv import load_dotenv
import requests
from operator import itemgetter
# Create the chain
from langchain_core.output_parsers import StrOutputParser

from backend.pull_data import RetrieveData

# Load the environment variables from the .env file
load_dotenv()
my_openai_api_key = os.getenv("OPENAI_API_KEY")
my_cohere_api_key = os.getenv("COHERE_API_KEY")

def get_chat_chain(data_source="la_medicaid"):
    
    if not my_openai_api_key:
        return Response({"error": "OpenAI API key not configured."}, status=500)
    elif not my_cohere_api_key:
        return Response({"error": "Cohere API key not configured."}, status=500)
    
    # Using the OpenAI embedding model to create vector embeddings for each chunk
    embeddings = OpenAIEmbeddings(openai_api_key=my_openai_api_key)
    
    
    print(f"Pulling data from {data_source}")
    
    if (os.path.exists(f"docs_{data_source}.pkl")):
        docs = pickle.load(open(f"docs_{data_source}.pkl", "rb"))
    else:
        docs = RetrieveData().pull_data(data_source) 
        
       
    # Storing chunks along with their vector embeddings into a Chroma database
    if (os.path.exists(f"chroma_db_{data_source}")):
        db = Chroma(persist_directory=f"chroma_db_{data_source}", embedding_function=embeddings)
    else:
        db = Chroma.from_documents(docs, embeddings, persist_directory=f"chroma_db_{data_source}")

    semantic_retriever = db.as_retriever(k=15, lambda_mult=0.33)
    # Defining our lexical retriever, which uses the BM25 algorithm, to retrieve the top-7 most
    # lexically similar chunks
    bm25_retriever = BM25Retriever.from_documents(docs, k=15)
    # Merge retrievers together into a single retriever, which will return up to 10 chunks
    merged_retriever = MergerRetriever(retrievers=[semantic_retriever, bm25_retriever])
    # We are using Cohere Rerank as our compression algorithm
    compressor = CohereRerank(top_n=5)
    # We define a new retriever than first uses the base_retriever to retrieve documents and then the
    # base_compressor to filter them
    compression_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=merged_retriever)

    # ChatGPT
    llm = ChatOpenAI(openai_api_key=my_openai_api_key, model="gpt-3.5-turbo", temperature=0.0)
    
    # Define a prompt to contextualize the user's question
    # Create our prompt
    if data_source == "la_medicaid":
        rag_template = """
        {context}
        
        You are a chatbot designed to help users find information about Medicaid in Louisiana. You have access to a collection of documents that contain information about Medicaid in Louisiana. Use outside knowledge to help answer the user's question. You should provide accurate and up-to-date information to the best of your ability. If you are unsure about the answer, you should let the user know. Remember to be helpful and courteous, and to try and help the user answer the questions.
        """
    elif data_source == "gov_medicare":
        rag_template = """
        {context}
        
        You are a chatbot designed to help users find information about Medicare in the United States. You have access to a collection of documents that contain information about Medicare in the United States. Use outside knowledge to help answer the user's question. You should provide accurate and up-to-date information to the best of your ability. If you are unsure about the answer, you should let the user know. Remember to be helpful and courteous, and to try and help the user answer the questions.
        """
    elif data_source == "insurance":
        rag_template = """
        {context}
        
        You are a chatbot designed to help users find information about health insurance in the United States. You have access to a collection of documents that contain information about health insurance in the United States. Use outside knowledge to help answer the user's question. You should provide accurate and up-to-date information to the best of your ability. If you are unsure about the answer, you should let the user know. Remember to be helpful and courteous, and to try and help the user answer the questions.
        """
    directory = os.path.join(os.path.dirname(__file__), data_source)
    print(directory)
    
    rag_template_end = """
    Use the above context to respond to the user's prompt in English. Your response must fully address all parts of the user's 
    questiopn as best as possible by incorporating and synthesizing any relevant details from the context. You may have to go into 
    SIGNIFICANTLY more depth than what the user asked. Users will typically not be very experienced, and you may have to elicit
    better questions from the user if the context you have access to is insufficient to answer many of their questions. It is your
    job to give the user help with problems they do not yet know how to ask. You must answer ALL parts of the user's question COMPLETELY 
    to the best of your provided context's quality.

    If the user asks a vague question, please be as specific as possible in your response given your context. You should suggest or 
    inform the user of Specific Policies or details that you think they need to know, to help them with their problem or questions.

    After you have answered their question, especially if it was a somewhat Vague question, Please ask the user for more clarification
    or information so that you could better answer their question.
    
    Remember to be helpful and courteous, and to be professional yet not overly formal.

    Format the response as markdown with the following guidelines: 
    1. Use paragraphs, lists, headers, and links to format the response when necessary. If you use a list, ensure it is formatted correctly. 
        If you use a header, ONLY USE #### size headers. Bold, or Italic ext is appropriate for emphasis.
    2. Ensure the response is concise, preferably no more than 1500 characters.

    You will cite the "sources" of the information at the bottom of the response using #### Sources: as the header.
    The "source" should include the title(s) of the document(s) that provided the information used to synthesize your response, as well as the page numbers
    listed alongside these documents. The file sources should be the name of the document(s) used to synthesize the response. Append just http://127.0.0.1:8000/static/ + name + .pdf  
            [I-1660 page number](http://127.0.0.1:8000/static/I-1660.pdf)
        DO NOT include backend/la_medicaid/ or backend/gov_medicare/ or backend/insurance in the link. Just put the name after the last /

    Here is the user's question: {question}
    """
    rag_template = rag_template + rag_template_end
    rag_prompt = ChatPromptTemplate.from_template(rag_template)
    
    def input_handler(input: dict):
        # Initialize an empty string to store the combined chat history
        chat_history_str = ""

        # If there's chat history, concatenate the last 10 responses into a single string
        if input.get("chat_history"):
            chat_history = input["chat_history"][-10:]  # Get the last 10 responses
            for message in chat_history:
                # You might want to format the message to distinguish between human and AI messages
                prefix = "Human: " if message["role"] == "human" else "AI: "
                chat_history_str += prefix + message["content"] + "\n"

        # Add the latest question to the chat history string
        chat_history_str += "Latest Question: " + input["question"]

        # Update the input dictionary to include the full context
        input.update({'context': chat_history_str})

        return input

    # Update the main chain to use the modified input handler
    chain = (
        input_handler
        | RunnablePassthrough().assign(context = itemgetter("question") | compression_retriever)
        | rag_prompt
        | llm
        | StrOutputParser()
    )
    print("Chain created")

    return chain