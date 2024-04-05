from django.utils import timezone
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import redirect
import json  # Import the json module
from datetime import datetime, timedelta #import datetime for checking date
from urllib.parse import urlencode, unquote, quote
# Create your views here.
from rest_framework.decorators import api_view
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

import requests
import re

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

#this is purely for weather functionality.
def format_weather_data(periods):
    formatted_output = ""
    for period in periods:
        formatted_output += f"Name: {period['name']}\n"
        formatted_output += f"\tStart Time: {period['startTime']}\n"
        formatted_output += f"\tEnd Time: {period['endTime']}\n"
        formatted_output += f"\tTemperature: {period['temperature']} {period['temperatureUnit']}\n"
        formatted_output += f"\tShort Forecast: {period['shortForecast']}\n"
        formatted_output += f"\tDetailed Forecast: {period['detailedForecast']}\n\n"
    return formatted_output

def format_parade_data(parade_list):
    parade_data_list = ""
    with open('backend/parade_info.json') as f:
        parade_data = json.load(f)

    for parade in parade_list:
        data = parade_data[parade]
        name = data['parade_name']
        try :
            parade_location = data['location']
            parade_description = data['description']
            parade_route = data['parade_route']
            parade_website = data['website']
            parade_date = data['date']
            parade_info_string = f"Parade Name: {name}\nDate: {parade_date}\nLocation: {parade_location}\nDescription: {parade_description}\nRoute Image JPG: {parade_route}\nWebsite: {parade_website}\n\n"
            parade_data_list += parade_info_string
        except:
            pass
        
    
    return parade_data_list

def get_recent_chat_chain(weather=False, photos=False, map_route=False, expedia=False, parade_list=[]):
    # Get the OpenAI API key from the environment variables
    # Create a ChatOpenAI instance
    if not my_openai_api_key:
        return Response({"error": "OpenAI API key not configured."}, status=500)
    
    # First, we get the docs that have been serialized as a pickle file
    # ... we should probably find a way to update the file in memory when we de-pickle it, and then re-pickle it...
    if (os.path.exists("../docs.pkl")):
        docs = pickle.load(open("../docs.pkl", "rb"))
    else:
        # If the Pickle File doesn't exist, then we create it by retrieving the JSON.

        data = RetrieveData() #the "data" here is an object of the "pull_data" class (kind of odd but alright)
        docs = data.pull_data() #"pull_data" gets the advocate data in a formatted way

        # -page_content (html tag)
        # -metadata 
        #       -uid
        #       -url
        #       -starttime
        #       -title
        #       -updatetime (last updated time)
        pickle.dump(docs, open("../docs.pkl", "wb"))

    # Now, all of the docs from the advocate is in the "docs" object
    print("Pulling Docs for Recent Chat Chain ...")

    # We also get the timestamp for the last 30 days
    current_time = datetime.now()
    one_month_ago = current_time - timedelta(days = 30)
    one_month_ago_timestamp = str(int(one_month_ago.timestamp() * 1000))
    
    recent_docs_count = 0
    current_doc_timestamp = docs[0].metadata["utc_starttime"]

    # And get the number of recent docs we want to use for our vector DB, to use for context
    # for our model
    while current_doc_timestamp == "N/A" or current_doc_timestamp > one_month_ago_timestamp:
        recent_docs_count += 1
        current_doc_timestamp = docs[recent_docs_count].metadata["utc_starttime"]

    recent_docs = docs[:recent_docs_count-1]

    #For now, we just get the chroma database like this. This is not good! We don't want the Chroma database for recent docs
    #to be stored on disk, that is dumb! This is far slower and more expensive than just embedding documents as we get them once
    #and adding them to the pre-existing persistent embedding that we use. We cannot re-embed whenever we need to update our embeddings!

    # Using the OpenAI embedding model to create vector embeddings for each chunk
    embeddings = OpenAIEmbeddings(openai_api_key=my_openai_api_key)
    if (os.path.exists("../chroma_db_recent")):
        db_recent = Chroma(persist_directory="../chroma_db_recent", embedding_function=embeddings)
    else:
        db_recent = Chroma.from_documents(recent_docs, embeddings, persist_directory="../chroma_db_recent")



    #REALLY need to be able to get embeddings from the pickle document, but the langchain community implementation of Chroma doesn't allow you to query
    #   a collection directly for some reason. use the real version of chroma (chromadb) for this maybe instead of langchain community chroma?
    #   We should probably ask Dr. Ghawaly about this
    #
    #   Reforming the vector DB like this allows us to only have to vectorize a document ONCE instead of revectorizing the whole thing whenever it updates. Much
    #   faster and easier!

        # db_recent_dict = db.get(limit=recent_docs_count, offset=0)
        # print(db_recent_dict.keys())
        # print(len(db_recent_dict["ids"]))

        #
        # \/ \/ \/ This just shows how the document/embedding collection is the same as the docs list
        #
        # for doc_index, doc in enumerate(db_recent["documents"]):
        #     print(doc[:20],", Time Posted : ", db_recent["metadatas"][doc_index]["starttime"])
        #     print(docs[doc_index].page_content[:20],", Time Posted : ", docs[doc_index].metadata["starttime"])
        #     print("\n")
        #
        # Now we have the collection (db_recent), how do we convert this collection into a Chroma database? 
        # This is kind of impossible with langchain-community chroma, but is possible with the official chromadb api.
        # (collections like db_recent are directly queryable without having to convert them to Chroma objects)



    #Now, we will also define a recent-doc-specific retriever.
    #We use a semantic retriever, a lexical retriever, combine them together, and then rerank to find the 
    #most relevant docs from ONLY the past 45 days. This gets around the issue of LLMs not really understanding
    #chronological order in dates in the document metadata (an issue Paul was having), by enforcing it by not even
    #giving older docs to this retriever at all.
    recent_semantic_retriever = db_recent.as_retriever(k=7)
    recent_bm25_retriever = BM25Retriever.from_documents(recent_docs,k=7)
    recent_merged_retriever = MergerRetriever(retrievers=[recent_semantic_retriever, recent_bm25_retriever])
    
    compressor = CohereRerank(top_n=5)
    recent_compression_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=recent_merged_retriever)

    # ChatGPT
    llm = ChatOpenAI(openai_api_key=my_openai_api_key, model="gpt-3.5-turbo", temperature=0.0)

    # Define a prompt to give the user an answer to their question based Strictly on time-sensitive answers
    # Weather area
    #weather report is used as part of the template
    weatherReport=""
    if weather:
        #the weather data is in a json on this link
        response = requests.get("https://api.weather.gov/gridpoints/LIX/67,87/forecast")
        if response.status_code == 200:
            #parse the json data from the response
            weather_data = response.json()
            # Extract and print relevant information
            periods = weather_data['properties']['periods']
            formatted_output = format_weather_data(periods)
            weatherReport= formatted_output
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
    
    
    parade_info = format_parade_data(parade_list)
    # Create our prompts
    recent_rag_template = """
    {context}
    You are a Mardi Gras Chabot. The Mardi Gras Assistant is a specialized chatbot designed to enrich the Mardi Gras experience for enthusiasts, 
    tourists, and locals alike. Its primary function is to provide informative, engaging, and interactive content related to Mardi Gras celebrations, 
    with a particular focus on historical context, parade schedules, event details, and thematic entertainment. 
    
    Capabilities include: 
    1. Parade Schedules - Provides up-to-date information on parade schedules, routes, and themes, offers guidance on viewing spots, parade etiquette, and safety tips.
    2. Event Recommendations - Recommends related events, parties, and balls, suggests local cuisine and specialty drinks.
    3. Interactive Entertainment - Engages users with themed games and quizzes, can generate and show themed images upon request.
    4. Practical Assistance - Provides tips on costume selection, mask-making, and offers advice on transportation, parking, and accommodations.
    5. Local Insights - Shares insider knowledge on the best spots to watch parades, hidden gems, and lesser-known traditions.

    Please answer questions clearly and concisely, and as accurately as possible, to promote accurate testing of your answers.
    
    If necessary, please inform users that you can not 
    -process transactions 
    -handle bookings
    
    And that users must verify parade schedules and event details through official channels.
    
    Specifically, you are a retriever chain designed to provide up-to-date information on UPCOMING and CURRENT events happening for users to participate in.

    The TRUE current date in ISO format is """+current_time.isoformat()+""" UTC.

    Here is a report on the weather: """+weatherReport+""", ignore if it is empty. 

    Here is a report on the upcoming parades: """+parade_info+""", ignore if it is empty.
    
    Be aware of the current date provided ABOVE and that events which happened in the past should NOT be listed as current. 
    Use the ISO start time of the article to determine the date of the element in the context provided.
    If a person asks for an upcoming event date, do NOT list an event which has already happened. 

    In addition to the metadata given, pay close attention to any dates given for events listed in the given articles.
    If those dates for given events have already happened, DO NOT suggest that users go to those events, unless they are currently ongoing and they
    may have a chance to go to them. If the dates for those events are upcoming or current, give them to the user and recommend that they go to them, if they
    are asking for events to go to.

    If an article mentions that a certain event is happening on a given day of the week, consider the ISO DATE given for the time this
    article was written. Consider these "days of the week" in the context of the date the article was published to compute the day when
    the event is happening, before suggesting a user goes to the event.

    If a person asks what is happening on or around a certain date, CHECK the ISO DATE provided in the METADATA of the element you are pulling data from. 

    Format the response as markdown with the following guidelines: 
    1. If any image is found related to the topic within the response, display the image using the Markdown image syntax `![alt text](image URL)` with the image URL. The maximum image size should be 300x300 pixels.
    The found image url should start with https://bloximages.newyork1.vip.townnews.com/nola.com/content and end with .image.jpg with content in between.
    2. Use markdown headers, lists, and links to format the response when necessary.
    3. If data is found, cite the URL source of the article information being pulled from at the bottom of the response as a footnote link.
    4. Ensure the response is concise, preferably no more than 2000 characters.
    5. Use #cc66ff as the link color or other accents in the response
    6. Remember to read the UTC time at the start of each article. 
    
    Question: {question}
    """
    recent_rag_prompt = ChatPromptTemplate.from_template(recent_rag_template)
    
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

    # We then create the recent docs chain
    recent_chain = (
        input_handler
        | RunnablePassthrough().assign(context = itemgetter("question") | recent_compression_retriever)
        | recent_rag_prompt
        | llm
        | StrOutputParser()
    )

    return recent_chain
    