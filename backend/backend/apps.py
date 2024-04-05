from django.apps import AppConfig

from .pull_data import RetrieveData
from .chat_chain import get_chat_chain

class BackendConfig(AppConfig):
    name = 'backend'

    def ready(self):

        self.chain = get_chat_chain() 
        
        #####################################
