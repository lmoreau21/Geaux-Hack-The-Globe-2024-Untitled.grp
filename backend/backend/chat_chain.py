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

def get_chat_chain(start_time=None, end_time=None):
    
    if not my_openai_api_key:
        return Response({"error": "OpenAI API key not configured."}, status=500)
    elif not my_cohere_api_key:
        return Response({"error": "Cohere API key not configured."}, status=500)
    
    if (os.path.exists("docs.pkl")):
        docs = pickle.load(open("docs.pkl", "rb"))
    else:
        data = RetrieveData() #the "data" here is an object of the "pull_data" class (kind of odd but alright)
        docs = data.pull_data() #"pull_data" gets the advocate data in a formatted way
       

    # Now, all of the docs from the advocate is in the "docs" object
    print("Pulling docs for vanilla Chat Chain ...")

    # Using the OpenAI embedding model to create vector embeddings for each chunk
    embeddings = OpenAIEmbeddings(openai_api_key=my_openai_api_key)
    # Storing chunks along with their vector embeddings into a Chroma database
    if (os.path.exists("chroma_db")):
        db = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
    else:
        db = Chroma.from_documents(docs, embeddings, persist_directory="chroma_db")

    semantic_retriever = db.as_retriever(k=7)
    # Defining our lexical retriever, which uses the BM25 algorithm, to retrieve the top-7 most
    # lexically similar chunks
    bm25_retriever = BM25Retriever.from_documents(docs, k=7)
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
    rag_template = """
    {context}
    You are a Medicaid eligibility analyst for the state of Louisiana. You have been asked to provide information on the topic of Medicaid eligibility.

    You will use the above context to respond to the user's prompt in plain English. Your writing, while not being condescending, should be easy to
    understand and should present the details of the documents in a concise and simple way. Your response must fully address all parts of the user's 
    questiopn as best as possible by incorporating and synthesizing any relevant details from the context. Remember to be helpful and courteous, to
    try and help the user answer the questions about their Medicaid eligibility as easily as you possibly can

    Format the response as markdown with the following guidelines: 
    1. Use markdown headers, lists, and links to format the response when necessary. Only one Type of header (###) should be used for formatting section
        headings, and simple paragraph text should be used for the body of your response.
    3. Ensure the response is concise, preferably no more than 3000 characters.
    4. Use #cc66ff as the link color or other accents in the response
    
    Consider that one unit of your context - a single json object containing page content and metadata - is a "Document"

    You will cite the "source" of the information at the bottom of the response as a footnote.
    The "source" should include the title(s) of the document(s) that provided the information used to synthesize your response, as well as the page numbers
    listed alongside these documents. Only cite articles that exist within your context, and that you specifically used to synthesize your response.
    
    Here is the user's question: {question}
    """

    rag_prompt = ChatPromptTemplate.from_template(rag_template)
    print("Rag created")

    #Paul: Every llm chain has an input handler first to adjust the info the 
    #chain gets. IN this case...
    def input_handler(input: dict):
        """
        Modifies the input dictionary to include the last 10 chat history responses and the latest question as context.
        """
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