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

#Paul: This file has a counterpart in recent_chat_chain, with a parallel recent get function.
#Paul: json_llm.py uses this function, and so does apps.py. 
def get_chat_chain(start_time=None, end_time=None):
    # Get the OpenAI API key from the environment variables
    # Create a ChatOpenAI instance
    if not my_openai_api_key:
        return Response({"error": "OpenAI API key not configured."}, status=500)
    
    # First, we get the docs that have been serialized as a pickle file
    # ... we should probably find a way to update this serialized file after depickling it ...
    if (os.path.exists("../docs.pkl")):
        docs = pickle.load(open("../docs.pkl", "rb"))
    else:
        # If the Pickle File doesn't exist, then we create it by retrieving the JSON.

        data = RetrieveData() #the "data" here is an object of the "pull_data" class (kind of odd but alright)
        docs = data.pull_data() #"pull_data" gets the advocate data in a formatted way

        #structure of docs is as follows :  
        # -page_content (html tag)
        # -metadata 
        #       -uid
        #       -url
        #       -starttime
        #       -title
        #       -updatetime (last updated time)

        #Paul: write binary to pickle
        pickle.dump(docs, open("../docs.pkl", "wb"))

    # Now, all of the docs from the advocate is in the "docs" object
    print("Pulling docs for vanilla Chat Chain ...")

    # Using the OpenAI embedding model to create vector embeddings for each chunk
    embeddings = OpenAIEmbeddings(openai_api_key=my_openai_api_key)
    # Storing chunks along with their vector embeddings into a Chroma database
    if (os.path.exists("../chroma_db")):
        db = Chroma(persist_directory="../chroma_db", embedding_function=embeddings)
    else:
        db = Chroma.from_documents(docs, embeddings, persist_directory="../chroma_db")

    
    if False:
        print(start_time, end_time)
        import datetime

        start_date = start_time / 1000  # Convert from milliseconds to seconds
        end_date = end_time / 1000  # Convert from milliseconds to seconds

        start_date_iso = datetime.datetime.utcfromtimestamp(start_date).isoformat()
        end_date_iso = datetime.datetime.utcfromtimestamp(end_date).isoformat()

        print(f"Start date in ISO 8601 format: {start_date_iso}")
        print(f"End date in ISO 8601 format: {end_date_iso}")
        filter = {
        "starttime": {
            "$gte": start_time,
            "$lte": end_time
        }}
        semantic_retriever = db.as_retriever(k=7, where = filter)
        print(semantic_retriever)
    
    else:
        semantic_retriever = db.as_retriever(k=7)
    
        #docs = [doc for doc in docs if doc.metadata["starttime"] >= start_time and doc.metadata["starttime"] <= end_time]
    # Defining our semantic retriever, which will return the top-7 most semantically relevant chunks
    
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
    You are a Mardi Gras Chabot. The Mardi Gras Assistant is a specialized chatbot designed to enrich the Mardi Gras experience for enthusiasts, 
    tourists, and locals alike. Its primary function is to provide informative, engaging, and interactive content related to Mardi Gras celebrations, 
    with a particular focus on historical context. Everything you discus is HISTORICAL.

    Capabilities include: 
    1. Historical Knowledge - Possesses in-depth knowledge of Mardi Gras history, including its origins, evolution, and traditions, and can share 
    interesting facts, stories, and the significance of various symbols and customs.  
    2. Local Insights - Discuss past events, parties, and balls, and suggests local cuisines and drinks. 
    3. Interactive Entertainment - Engages users with themed games and quizzes, can generate and show themed images upon request. 
    4. Practical Assistance - Provides tips on costume selection, mask-making, and offers advice on transportation, parking, and accommodations. 
    5. Must-See Recommendations - Recommends places to visit in New Orleans, such as museums, parks, and historical sites.
    Please answer questions clearly and concisely, and as accurately as possible, to promote accurate testing of your answers.
    
    If necessary, please inform users that you can not 
    -process transactions 
    -handle bookings
    -provide real-time updates on events or parades
    And that users must verify parade schedules and event details through official channels.
    
    If a person asks, say, what is happening on or around a certain date, CHECK the starttime or readable_starttime provided in the METADATA
    of the element you are pulling data from. 

    If a person asks for events, say you can only provide information on past events.

    Format the response as markdown with the following guidelines: 
    1. If any image is found related to the topic within the response, display the image using the Markdown image syntax `![alt text](image URL)` with the image URL. NO MORE THAN 300x300 pixels.
    The found image url should start with https://bloximages.newyork1.vip.townnews.com/nola.com/content and end with .image.jpg with content in between.
    2. Use markdown headers, lists, and links to format the response when necessary.
    3. If data is found, cite the URL source of the article information being pulled from at the bottom of the response as a footnote link.
    4. Ensure the response is concise, preferably no more than 3000 characters.
    5. Use #cc66ff as the link color or other accents in the response
    6. Remember to read the UTC time at the start of each article. 
    
    Cite the title, readable_starttime, and URL from the metadata of the most used article. Add multiple citations if multiple articles are used. Also use href to link the exact location of the information with the article.

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