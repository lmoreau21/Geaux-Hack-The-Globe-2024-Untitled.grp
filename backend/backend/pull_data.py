import time
import requests
import json
import re
from datetime import datetime, timezone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

import datetime
import pickle
import os

import urllib3

class RetrieveData:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=50, separators=['.', '\n'])
        self.prepared_docs = []

    def add_prepared_doc(self, article):
        #This function converts the article retrieved as json article from the get request and converts it into an article, 
        #and stores it along with the other articles in the local class list "prepared_docs"

        # Extract necessary fields from each article
        uid = article.get("uuid", "")
        starttime = article.get("starttime", {}).get("utc", "") or "N/A"  # Use "N/A" if None
        title = article.get("title", "")
        url = article.get("url", "") or "N/A"
        updatetime = article.get("lastupdated", {}).get("utc", "") or "N/A"  # Use "N/A" if None
        page_content = article.get("content") or "N/A"
        
        if starttime == "N/A":
            starttime = 1    
        d2 = int((int(starttime) - 10)/1000)

        readable_starttime = 1
        if starttime == "N/A":
            readable_starttime = "N/A"
        else:
            readable_starttime = datetime.datetime.fromtimestamp(int(starttime)/1000).strftime("%A, %B %#d %Y")
        
        readable_updatetime = 1
        if updatetime == "N/A":
            readable_updatetime = "N/A"
        else:
            readable_updatetime = datetime.datetime.fromtimestamp(int(updatetime)/1000).strftime("%A, %B %#d %Y")

        if page_content != "N/A":
            cleaned_content = self.clean_html(page_content) 
            # Create a Document object with metadata
            doc = Document(page_content=cleaned_content, metadata={
                "uid": uid,
                "url": url,
                "utc_starttime": starttime,
                "readable_starttime": readable_starttime,
                "title": title,
                "utc_updatetime": updatetime,
                "readable_updatetime": readable_updatetime
            })
            self.prepared_docs.append(doc)
        
        return d2

        
    def rss_get_request(self, url):
       
        r = urllib3.request("GET",url)
        
        while(r.status == 429):
            print("Too many requests. Delaying.")
            
            pickle.dump(self.prepared_docs, open("docs_temp.pkl", "wb"))
            time.sleep(200)
            r = urllib3.request("GET",url)

        return r



    def update_advocate_data(self):
        #go through the RSS feed and add docs (with their metadatas) until you hit the most recent doc you have seen
        #   -get the title of the first/most recent doc in the current list of docs (the doc at the front)
        #   -make a new Temporary list of docs to contain the new ones
        #   -add the docs in order as you create them, adding to the end of the temporary list (also be sure to add metadata)
        #   -split the docs using the textsplitter defined above
        #   -add the temp docs list to the front of the current list of docs, to maintain chronology
        #
        #   -for the whole list of the temporary docs, add each doc to the chroma DB as a new doc, using the embeddings for Chroma
        #   -change the old system so that it would get the ID of every doc that had too-old dates for the metadata, and delete them all one by one
        #       -(This prunes the data from the existing doc instead of re-vectorizing it. should be faster.)
        #       -Specifically, make a method beside get_chat_chain that filters the docs by date, and collects the undesirable IDs for deletion from
        #        the copy of the database to be returned
        print("update_advocate_data")
        
        docs = pickle.load(open("docs.pkl", "rb"))

        self.prepared_docs = []
        d1 = docs[0].metadata["utc_starttime"]
        d1 = int((int(d1) - 10)/1000) + 80000
        d1 = (datetime.datetime.fromtimestamp(d1, tz=datetime.timezone.utc)).isoformat()[:-6]
        sections = ["entertainment_life","entertainment_life/mardi_gras"]
        docUIDToStopAt = docs[0].metadata["uid"]

        #First we get the new raw documents via the RSS feed, to add them to our serialized "docs" file
        count = 0
        keepAdding = True
        for section in sections:
            while keepAdding:
                url = "https://www.nola.com/search/?t=article&f=json&c%5b%5d="+section+"&q=Mardi+Gras&s=start_time&sd=desc&l=100&d1="+str(d1)
                
                print("URL: ", url )
                
                r = self.rss_get_request(url)
            
                json_data = r.json()
                
                rows = json_data['rows']

                if rows == []:
                    keepAdding = False
                    print("No more articles found.")
                    print("Total articles found: ", count)
                    break
                
                for article in rows:                
                    if article.get("uuid", "") == docUIDToStopAt:
                        keepAdding = False
                        break
                    count += 1
                    d1 = self.add_prepared_doc(article)
                    d1 += 86400
                    d1 = (datetime.datetime.fromtimestamp(d1, tz=datetime.timezone.utc)).isoformat()[:-6] 
                

        if self.prepared_docs == []:
            print("No new articles found.")
            return

        new_docs = self.text_splitter.split_documents(self.prepared_docs)
        docs = new_docs + docs

        my_openai_api_key = os.getenv("OPENAI_API_KEY")

        # Using the OpenAI embedding model to create vector embeddings for each chunk
        embeddings = OpenAIEmbeddings(openai_api_key=my_openai_api_key)
        # Storing chunks along with their vector embeddings into a Chroma database
        if (os.path.exists("./chroma_db")):
            db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

            print("     (CHROMA) (NEW) Newest Document in Chromadb", new_docs[-1].metadata)

            #after loading, we also add the new documents to the ChromaDB
            db.add_documents(new_docs)

            print("     (CHROMA) (NEW) Newest Document in Chromadb", new_docs[-1].metadata)
        else:
            db = Chroma.from_documents(docs, embeddings, persist_directory="./chroma_db")

        pickle.dump(docs, open("docs_new.pkl", "wb"))
       

    def add_metadata(self):
        docs = pickle.load(open("docs.pkl", "rb"))
        #print(datetime.datetime.fromtimestamp(int(docs[0].metadata["starttime"])/1000,tz=datetime.timezone.utc).isoformat())
        
        for doc_number, doc in enumerate(docs):
            starttime = docs[doc_number].metadata["starttime"]
            updatetime = docs[doc_number].metadata["updatetime"]

            if starttime != "N/A":
                docs[doc_number].metadata["readable_starttime"] = datetime.datetime.fromtimestamp(int(starttime)/1000).strftime("%A, %B %#d %Y")
            else:
                docs[doc_number].metadata["readable_starttime"] = "N/A"
            
            docs[doc_number].metadata["utc_starttime"] = starttime
            del docs[doc_number].metadata["starttime"]

            if updatetime != "N/A":
                docs[doc_number].metadata["readable_updatetime"] = datetime.datetime.fromtimestamp(int(updatetime)/1000).strftime("%A, %B %#d %Y")
            else:
                docs[doc_number].metadata["readable_updatetime"] = "N/A"
            
            docs[doc_number].metadata["utc_updatetime"] = updatetime
            del docs[doc_number].metadata["updatetime"]

        pickle.dump(docs, open("docs.pkl", "wb"))

    def pull_data(self):
        # Retrieve the data from the NOLA.com website
        d2 = ' '
        count = 0
        try: 
            
            self.prepared_docs = pickle.load(open("docs.pkl", "rb"))
            
            d2 = self.prepared_docs[-1].metadata['utc_starttime']
            
            d2 = int((int(d2) - 10)/1000)
            d2 = (datetime.datetime.fromtimestamp(d2, tz=datetime.timezone.utc)).isoformat()[:-6]
            
        except:
            print("No data")
        sections = ["entertainment_life","entertainment_life/mardi_gras"]
        for section in sections:
            d2 = ' '
            while True:
                
                url = "https://www.nola.com/search/?t=article&f=json&c%5b%5d="+section+"&q=Mardi+Gras&s=start_time&sd=desc&l=100&d2="+str(d2)
                
                print("URL: ", url )
                
                r = self.rss_get_request(url)
            
                json_data = r.json()
                
                rows = json_data['rows']
                total = json_data['total']
                if rows == [] or d2 == "1993-02-06T11:19:18":
                    print("No more articles found.")
                    print("Total articles found: ", count)
                    break

                for article in rows:
                    count += 1
                    if section == "entertainment_life/mardi_gras" and article.get("sections", "")[0] == "entertainment_life":
                        starttime = article.get("starttime", {}).get("utc", "") or "N/A"  # Use "N/A" if None 
                        d2 = int((int(starttime) - 10)/1000)
                    else: 
                        d2 = self.add_prepared_doc(article)
                
                if total < 100 and section == "entertainment_life/mardi_gras":
                    print("No more articles found.")
                    break
                d2 = (datetime.datetime.fromtimestamp(d2, tz=datetime.timezone.utc)).isoformat()[:-6]

                

        docs = self.text_splitter.split_documents(self.prepared_docs)
        return docs

    #Paul: maybe we should have to change this if we want to get more relevant images
    def clean_html(self, raw_html):
        """
        Remove HTML tags and unwanted content from a string or list of strings.
        :param raw_html: A string or list of strings containing HTML content.
        :return: Cleaned string or list of cleaned strings.
        """
        for line in raw_html:
            if "inline-asset inline-editorial-image" in line:
                try:
                    image_link = line[line.index("https://bloximages.newyork1.vip.townnews.com/nola.com/content"):line.index(".image.jpg")+10]
                    description = line[line.index("<p>"):line.index("</p>")]
                    new_line = "JPG Image URL: " + image_link + " " + description
                    raw_html.remove(line)
                    raw_html.append(new_line)
                except:
                    pass
            elif "<figure" in line:
                raw_html.remove(line)

        if isinstance(raw_html, list):
            raw_html = ' '.join(raw_html)

        clean_text = re.sub(r'<[^>]+>', '', raw_html)  # Remove all remaining HTML tags

        return clean_text
       

