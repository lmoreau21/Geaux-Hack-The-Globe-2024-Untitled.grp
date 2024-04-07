# Healthcare Information Chatbot
Lilly Moreau & James Power

## Project Overview
This project aims to provide users with easy access to detailed information about Louisiana Medicaid, U.S. government Medicare, and general health insurance questions through a chatbot interface. The chatbot is powered by OpenAI's GPT-3.5 model and utilizes LangChain for efficient data retrieval and response generation, with a Chroma database storing pre-processed, vector-embedded document data. Our Django backend handles API requests and data management, while the React frontend offers an intuitive user interface styled with Material UI.

## Key Features
* Information Retrieval: Dynamically fetches relevant information from a curated database.
* Chat Interface: Users can query the system in natural language.
* Responsive Design: The UI adjusts for different devices, enhancing accessibility.
* Data Sources: Compiles reputable sources to ensure accuracy and reliability.

### Technical Stack
* Backend: Django
* Frontend: React with Material UI
* AI and NLP: OpenAI GPT-3.5, LangChain LLM
* Database: Chroma (Vector database for efficient data retrieval)

## Key Components
#### Backend
* chat_chain.py: Central to the chatbot's operation, orchestrating the data retrieval, processing, and interaction with GPT-3.5.
* pull_data.py: Responsible for fetching and preprocessing data from reputable sources to populate the Chroma DB.
* chatbot_post.py: Hanldes the post request and invokes the chat chain
* Environment Variables: Utilizes .env for managing sensitive API keys securely.
#### Frontend
* chat.jsx: Implements the chat interface, handling user inputs and displaying chatbot responses.
* PersistentDrawer.jsx: Manages the navigation drawer, theme toggling between light and dark modes, and the switching of data sources.

## Setup and Installation

### Prerequisites

- Python 3.10
- Node.js 14+
- Django
- React
