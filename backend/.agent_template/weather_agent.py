import os

#os.environ["GOOGLE_CSE_ID"] = "31455a027435744e8"
#os.environ["GOOGLE_API_KEY"] = "AIzaSyDMVMGnKvDAXvO4N9R8iyimvuRR2XkZMxo"

#Paul:this next import may not be necessary due to change in usage but I don't know.
#there are only a few things in this template that are google weather specific though. 

from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_core.tools import Tool

#Paul 3/26/2024: As of today there are only a few things to do with this:
#- chain it to the new chain, I don't know what the new chains lily is making are going to look like
#- add API keys from the Advocate
#- remove unit tests for actual deployment
#- make frontend accept API JSON? 
#- remove OWM functionality and use weather.gov stuff instead

#not necessary of course
'''
search = GoogleSearchAPIWrapper(k=1)

google_search_tool = Tool(
    name="google_search",
    description="Search Google for recent results.",
    func=search.run,
)
'''
#google_search_tool.run(tool_input="current news in New Orleans")

#Paul: this has been removed of the google search ability
planning_prompt_template = """
System: You are an assistant with the main Mardis Gras Template meant to answer questions about local weather.

Instructions:
Your task is to answer a question. You will do so by either (1) directly answering the question, if you can based previous observations OR (2) by using a tool to get more information.

Available Actions:
- Weather_Tool: Allows you to get the current weather in a particular state or country.
- Response_Tool: If you know the response, use this tool, which will format the response.

Previous Questions, Actions, and Observations
{context}

QUESTION
{question}

Answer Format
Your response must be a valid JSON structure with a "Question" field containing the question and an "Action" field containing the proposed action to take to answer the question.
"""

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

#uses paul's api key by default
llm = ChatOpenAI(model="gpt-3.5-turbo",
                 api_key="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")

planning_prompt = ChatPromptTemplate.from_template(planning_prompt_template)

planning_chain = planning_prompt | llm | JsonOutputParser()

print("Invoking weather question test: ")
planning_chain.invoke({"question": "What is the current temperature in Kenner Louisiana?",
                       "context": "No previous communication"})


#DEFINING TOOL INPUTS

tool_inputs = {
    "Weather_Tool": {"city": "(str) The city in which we want to determine the weather",
                     "state": "(str) The two character state code of the city",
                     "country": "(str) The two character code of country, e.g. United States is 'US'"},
    "Response_Tool": {"response": "(str) The final response to the user's question."}
}

def format_tool_prompt_template(tool_name):
    tool_args = tool_inputs[tool_name]
    s = f"""The tool "{tool_name}" accepts {len(tool_args.keys())} keyword arguments, listed below with descriptions:

"""
    for k in tool_args.keys():
        s += f"\t{k}: {tool_args[k]}\n"
    return s

#USE AN LLM TO DETERMINE THE ARGUMENTS TO OUR TOOLS

tool_exec_prompt_template = """
General Instruction: We wish to use a tool to answer a question or execute an instruction. You are to generate a JSON dictionary (single line, no indents) containing the values for input arguments to that tool based on the question or instruction:

Tool Description:
{tool_prompt}

Question or Instruction:
{question}

Response:
"""
tool_exec_prompt = ChatPromptTemplate.from_template(tool_exec_prompt_template)

tool_exec_chain = tool_exec_prompt | llm | JsonOutputParser()

print("Proper tool exec chain invocation of weather: ")
tool_exec_chain.invoke({"question": "What is the weather today in Baton Rouge?",
                        "tool_prompt": format_tool_prompt_template("Weather_Tool")})

#Paul: OWM stands for " Open weather map," a common API style for showing the weather.
#probably the advocate also uses this but we need to check. 
#none of these functions here are google specific 
from pyowm import OWM
#Paul: what is this? a seed? a key I can't use?
owm = OWM('5cec79482318850a1df95f5a3165369b')
mgr = owm.weather_manager()
reg = owm.city_id_registry()
mgr = owm.weather_manager()

def get_weather(city, state, country):
    id = reg.locations_for(city, state=state, country=country, matching='exact')[0].id

    weather = mgr.weather_at_id(id).weather

    weather_str = f'Temperature = {weather.temperature("fahrenheit")["temp"]} F, Feels Like Temperature = {weather.temperature("fahrenheit")["feels_like"]} F, Humidity = {weather.humidity} %, Detailed Status = {weather.detailed_status}, Wind = {weather.wind(unit="miles_hour")["speed"]} mph at {weather.wind(unit="miles_hour")["deg"]} degrees'
    return weather_str

print("printing direct get of baton rouge weather: ")
print(get_weather(city="Baton Rouge", state="LA", country="US"))

#Define Function to Execute Tools

def execute_tool(tool_name, tool_kwargs):
    if tool_name == "Weather_Tool":
        output = get_weather(**tool_kwargs)
    
    elif tool_name == "Response_Tool":
        return tool_kwargs["response"]
    else:
        print("Fail")
        output = "None"

    return output

print("Invoking game weather: ")
planning_chain.invoke({"question": "Is today a nice day to play a football game outside?",
                       "context": "No previous communication"})

#DEFINE CHAIN TO FORMAT FINAL RESPONSE

final_response_template = """
Based on the following information, answer the question:
Information:
{information}

Question:
{question}

Response:
"""

final_response_prompt = ChatPromptTemplate.from_template(final_response_template)

final_response_chain = final_response_prompt | llm | StrOutputParser()

#SIMPLE TESTING

my_question = "Is today a nice day to play a football game outside in Baton Rouge?"
plan = planning_chain.invoke({"question": my_question, "context": "No previous communication"})
print(plan)
exec_data = tool_exec_chain.invoke({"question": my_question,
                                    "tool_prompt": format_tool_prompt_template(plan["Action"])})
print(exec_data)
tool_output = execute_tool(plan["Action"], exec_data)
print(tool_output)
print('\n\nFinal Response:')
print(final_response_chain.invoke({"question": my_question,
                                   "information": tool_output}))

