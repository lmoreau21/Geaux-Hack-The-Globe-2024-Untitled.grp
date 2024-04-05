import pickle
import os
import requests
import json
import re

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema.document import Document

from dotenv import load_dotenv

class RetrieveRecent:
    def __init__(self):
        self.recent_docs = []
        self.recent_chromas = []

        self.recent_titles = []
        #2025 Parade Dates will be given by Lilly's Cleaned Json code
        self.recent_titles.append("The Ultimate Mardi Gras Survival Guide")
        self.recent_titles.append("No costume? No problem! Dress for Mardi Gras success with these last-minute tips")
        self.recent_titles.append("Have a Safe Mardi Gras")
        self.recent_titles.append("10 Tips & Things to Remember at Mardi Gras")
        self.recent_titles.append("Essential tips for your Mardi Gras quick-change")

    #get recent retriever should be removed. this doesn't work any more for producing a
    #chroma from filtering the docs, since the 2025 parade docs are cleaned in a different
    #way, algorithmically
    def get_recent_retriever(self, chroma):
        filter = {
        "title": {
            "$in": self.recent_titles
        }}

        return chroma.as_retriever(k=7, where = filter)
    
    def get_parade_doc(self, parade_json, parade_title):
        #description
        description = parade_json[parade_title]["description"]
        #
        #parade name
        name = parade_json[parade_title]["parade_name"]
        #date
        date = parade_json[parade_title]["date"]
        #location
        location = parade_json[parade_title]["location"]
        #parade_route
        parade_route = parade_json[parade_title]["parade_route"]
        #website
        website = parade_json[parade_title]["website"]

        doc = Document(page_content="\""+name+"\" Parade Information : "+description, metadata= {
            "name": name,
            "date": date,
            "location": location,
            "parade_route": parade_route,
            "website": website
        })

        #Ask Ghawaly about Chroma DB and if it understands dates and what their semantic meaning is
        #Semantic Search of Documents is for suggesting parades that are similar to what the user is
        #asking about

        #practice is 3 weeks from tonight (slide deck, videos, etc)

        return doc

    #this will be used in recent chat chain as the docs that will be the input of the
    #recent chroma DB
    def get_recent_docs(self, docs):
        parade_file = open("parade_info.json")
        parade_json = json.load(parade_file)

        parade_names = list(parade_json.keys())

        for parade_name in parade_names:
            parade_doc = parade_json[parade_name]
            recent.get_parade_doc(parade_json, parade_doc)
            self.recent_docs.append(doc)

        doc = parade_names[0]

        recent = RetrieveRecent()
        print(recent.get_parade_doc(parade_json,doc))

        for doc in docs:
            if doc.metadata["title"] in self.recent_titles:
                self.recent_docs.append(doc)

if __name__ == "__main__":
    load_dotenv()
    my_openai_api_key = os.getenv("OPENAI_API_KEY")

    docs = pickle.load(open("../docs.pkl", "rb"))

    recent = RetrieveRecent()
    recent.get_recent_docs(docs)

    # embeddings = OpenAIEmbeddings(openai_api_key=my_openai_api_key)
    # db = Chroma(persist_directory="../chroma_db", embedding_function=embeddings)

    print("Goober Genius!")