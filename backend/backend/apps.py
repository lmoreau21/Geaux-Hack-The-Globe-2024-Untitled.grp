from django.apps import AppConfig

from .pull_data import RetrieveData
from .chat_chain import get_chat_chain
from .recent_chat_chain import get_recent_chat_chain

class BackendConfig(AppConfig):
    name = 'backend'

    def ready(self):
        # This method runs once when the app is ready.
        # You can initialize your chain here.
       
        # Assuming get_chat_chain is a function that initializes and returns the chain

        self.chain = get_chat_chain() #i will add my recent_chain here so it can be used by chatbot.py ...

        # then, we pull the recent chat chain from its file, for answering Recent and Future Events 
        # questions
        
        self.recent_chain = get_recent_chat_chain()
        
        #update the advocate data
        RetrieveData().update_advocate_data()
        
        #####################################
