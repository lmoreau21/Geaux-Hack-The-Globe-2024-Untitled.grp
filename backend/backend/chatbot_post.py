from django.utils import timezone
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
import json  
from rest_framework.decorators import api_view
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import os
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from .chat_chain import get_chat_chain
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['POST'])
def chatbot_post(request):
    '''
    This function is a view that handles POST requests to the /chatbot/ endpoint.
    It takes a question and chat history as input, and returns a response from the chatbot.

    input:
    - question: A string containing the question to be asked.
    - chat_history: A list of dictionaries containing the chat history.
    - isMedicaid: A boolean indicating whether the question is related to Medicaid.

    output:
    - chat_history: A list of dictionaries containing the updated chat history.
    - latest_response: A string containing the latest response from the chatbot.
    '''   
    print(request.data)
    question = request.data.get('question', '')
    data_source = request.data.get('data_source', 'la_medicaid')
    
    print(data_source)
    chat_history = request.data.get('chat_history', [])
        
    response = get_chat_chain(data_source=data_source).invoke({"question": question, "chat_history": chat_history})
    
    chat_history.append({"role": "human", "content": question})
    chat_history.append({"role": "ai", "content": response})
    
    return JsonResponse({
        'chat_history': chat_history,
        'latest_response': response
    })