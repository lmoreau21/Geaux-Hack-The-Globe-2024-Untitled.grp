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

    def pull_data(self, data_source="la_medicaid"):
        # Retrieve the data from the NOLA.com website
        folder_path = "./backend/" + data_source
        count = 0
        self.docs = []
        
        for filename in os.listdir(folder_path):
            print(filename)
            count += 1
        print(count)
        loader = PyPDFDirectoryLoader(folder_path)
        self.docs = loader.load()
        pickle.dump(self.docs, open(f"docs_{data_source}.pkl", "wb"))
        
        return self.docs