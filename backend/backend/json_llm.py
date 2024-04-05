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
from .recent_chat_chain import get_recent_chat_chain

#Paul: lily said:
# The user will ask a question
# That is sent to json llm
# Json llm will call historical or recent based on the json response
# Returns mark down for frontend

#dangerouslyset html, soon to be changed to markdown  in the chatinterface.jsx comes from here. You can find a post
#request in chatinterface.jsx that comes back to here. 

def pull_parade_data():
    parade_data_list = ""
    with open('backend/parade_info.json') as f:
        parade_data = json.load(f)

    for parade in parade_data:
        data = parade_data[parade]
        name = parade
        try :
            parade_date = data['date']
            parade_data_list += " " + name + ":" + parade_date + " "
        except:
            pass
        
    
    return parade_data_list



def get_json(request):
    # Get the OpenAI API key from the environment variable
    my_openai_api_key = os.getenv("OPENAI_API_KEY")
    
    # Create an instance of the ChatOpenAI class
    llm = ChatOpenAI(openai_api_key=my_openai_api_key, model="gpt-3.5-turbo", temperature=0.0)
    
    # Get the question from the request data
    question = request.data.get('question', '')
    parade_data = pull_parade_data()
    
    # Create a RAG template for the response
    rag_template = f"""

        You are an analyst of questions for a New Orleans Mardi Gras themed chatbot. 
        Analyze the following question and provide a structured JSON response that includes: 
        - Whether the question is historical (true/false), Historical questions are anything that happened in the past. If the question is about the future, it is not historical.
            Example: "Show me a photo of a float?" would be historical.
            Example: "When is the next parade?" would be NOT historical.
            Example: "What are the most popular parades to attend?" would be historical.
            Example: "What parades should I attend?" would be NOT historical. 
        - Whether this question would benefit from receiving weather information (true/false), Any questions that relates to doing an activity would benefit from weather information.
            Example: "What should I do this weekend?" would benefit from weather information.
        - Whether this question would benefit from receiving photos (true/false),
            Example: "What does the French Quarter look like?" would benefit from photos.
        - Whether this question would benefit from receiving a parade map route (true/false),
            Example: "Where does the Krewe of Bacchus parade start?" would benefit from a parade map route.
            Example: "Where is the best place to watch the parades?" would benefit from a parade map route.
        - Whether this question could involve hotel, car, or trip booking (true/false),
            Example: "What are the best hotels to stay at during Mardi Gras?" would involve hotel booking.
        - The reason for the historical or non-historical classification (historical means anything that happened in the past beyond a month),
        - The relevant time period of the question. If the question asks about the future, estimate that future date based on the question's context.
        - Start date and end date if the question is historical in UTC Format (1642166400000 is 2022-01-15). THE RANGE MUST BE 60 DAYS OR MORE. Use the following dates for Mardi Gras to estimate the time period for the question:
            Example for Mardi Gras 2022: Start date: 1642166400000 (2022-01-15), End date: 1647264000000 (2022-03-15).
            Example for Mardi Gras 2023: Start date: 1673712000000 (2023-01-15), End date: 1678809600000 (2023-03-15).
            Example for Mardi Gras 2024: Start date: 1705238400000 (2024-01-15), End date: 1710422400000 (2024-03-15).
        - Use prompt engineering to ONLY write a detailed QUESTION that is a better version of the asked question. DO NOT ANSWER THE QUESTION. You may need to add specific details like dates, names, etc., to make the question more specific.
        - Here is parade names and dates for the next or current mardi gras: {parade_data}  If the question is not historical, use this data to come up with an array of parade names that the user could be asking about.
            Example: "When is the next parade?" use the current date and find out what the next parade is. Response should be ['Joan of Arc'], if there is multiple parades on the same day, return all of them as a list.

        The question is: "{question}"
        This is the current date: "{timezone.now()}"

        Here's a template for your response (respond only in JSON format):
        "isHistorical": True/False, 
        "needsWeather": True/False,
        "addPhotos": True/False",
        "needsMap": True/False,
        "isExpedia": True/False,
        "original_question": "{question}",
        "reason_for_historical_choice": "Provide your reasoning here.",
        "time_period": "Always provide the relevant time period here, using dates as much as possible, even if it is a range.",
        "start_date": UTC time (int) or None,
        "end_date": UTC time (int) or None, # THE DATE CAN NOT BE PAST THE CURRENT DATE
        "detailed_prompt": "Craft a detailed prompt for a more exact inquiry based on the question and what topics the chatbot should look for in providing an answer. Add a time period as month day, year if necessary.",
        "parade_list": ['parade1', 'parade2', 'parade3'] # If the question is not historical, use this data to come up with an array of parade names that the user could be asking about.
        """
    
    # Create a ChatPromptTemplate from the RAG template
    rag_prompt = ChatPromptTemplate.from_template(rag_template)
    
    # Define an input handler function
    def input_handler(input: dict):
        return input
    
    # Create the chain of runnables
    chain = (
        input_handler
        | RunnablePassthrough().assign(context=itemgetter("question"))
        | rag_prompt
        | llm
        | StrOutputParser()
    )
    
    # Invoke the chain with the question as input
    response = chain.invoke({"question": question})
    
    return response


@api_view(['POST'])
def json_chatbot_post(request):
    '''
    This function is a view that handles POST requests to the /json_chatbot/ endpoint.
    It takes a question and chat history as input, and returns a response from the chatbot.

    input:
    - question: A string containing the question to be asked.
    - chat_history: A list of dictionaries containing the chat history.

    output:
    - chat_history: A list of dictionaries containing the updated chat history.
    - latest_response: A string containing the latest response from the chatbot.
    '''
    #Paul: The main chatbot.py does not create an llm. It doesn't need to because the 
    #request is intended to go here first. 

    response = get_json(request)

    # Get the question from the request data
    question = request.data.get('question', '')
    
    # Get the chat history from the request data
    chat_history = request.data.get('chat_history', [])

    try:
        llm_response_data = json.loads(response)
        print("llm_response_data_json: ",llm_response_data)
        
        isHistorical = llm_response_data['isHistorical']
        needsWeather = llm_response_data['needsWeather']
        addPhotos = llm_response_data['addPhotos']
        needsMap = llm_response_data['needsMap']
        isExpedia = llm_response_data['isExpedia']
        startDate = llm_response_data['start_date']
        endDate = llm_response_data['end_date']
        detailedPrompt = llm_response_data['detailed_prompt']
        parade_list = llm_response_data['parade_list']
        
        if isHistorical:
            print('isHistorical is true')
            
            # Invoke the chat chain with the detailed prompt
            # Paul: find documentation in chat_chain.py
            response = get_chat_chain(start_time=startDate,end_time=endDate).invoke({"question": question, "chat_history": chat_history})
            
            # Append the question and response to the chat history
            chat_history.append({"role": "human", "content": question})
            chat_history.append({"role": "ai", "content": response})
            
            return JsonResponse({
                'chat_history': chat_history,
                'latest_response': response
            })
        elif not isHistorical:
            print('isHistorical is false')
            
            # Invoke the recent chat chain with the detailed prompt
            response = get_recent_chat_chain(weather=needsWeather,parade_list=parade_list).invoke({"question": question, "chat_history": chat_history})
            chat_history.append({"role": "human", "content": question})
            chat_history.append({"role": "ai", "content": response})
            
            return JsonResponse({
                'chat_history': chat_history,
                'latest_response': response
            })
            
    except Exception as e:
        print("Backup plan: ",e)
        
        # Invoke the recent chat chain with the original question
        response = get_recent_chat_chain().invoke({"question": question, "chat_history": chat_history})
        chat_history.append({"role": "human", "content": question})
        chat_history.append({"role": "ai", "content": response})
        
        #Paul: return the response ot the JSON data parsed from llm just earlier. 
        return JsonResponse({
            'chat_history': chat_history,
            'latest_response': response
        })