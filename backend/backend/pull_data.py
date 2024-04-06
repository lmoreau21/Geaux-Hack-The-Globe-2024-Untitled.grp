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
import os
from langchain_community.document_loaders import PyPDFDirectoryLoader

class RetrieveData:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=50, separators=['.', '\n'])
        self.prepared_docs = []

    def pull_data(self):
        # Retrieve the data from the NOLA.com website
        folder_path = "./backend/la_medicaid"
        count = 0
        try:
            self.docs = pickle.load(open("docs.pkl", "rb"))
        except:
            self.docs = []
        
        for filename in os.listdir(folder_path):
            print(filename)
            count += 1
        print(count)
        loader = PyPDFDirectoryLoader(folder_path)
        self.docs = loader.load()
        pickle.dump(self.docs, open("docs.pkl", "wb"))
        
        return self.docs