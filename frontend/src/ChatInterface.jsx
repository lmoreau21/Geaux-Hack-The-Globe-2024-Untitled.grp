import React, { useEffect, useRef, useState } from 'react';
import './ChatInterface.css'; 
import axios from 'axios';
import { FaChevronRight } from "react-icons/fa";
import ReactMarkdown from 'react-markdown';
import { StreamChat } from 'stream-chat'

function ChatInterface() {
  const [messages, setMessages] = useState(() => {
    // Load the chat history from localStorage when the component is mounted
    const savedMessages = localStorage.getItem('chatHistory');
    return savedMessages ? JSON.parse(savedMessages) : [];
  });

  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(scrollToBottom, [messages]);
  
  useEffect(() => {
    // Save the chat history in localStorage whenever it changes
    localStorage.setItem('chatHistory', JSON.stringify(messages));
  }, [messages]);
  
  function roleSendMessage(role, content) {
    // Add the role's message to the messages state
    setMessages(prevMessages => [...prevMessages, { role, content }]);

    // After the role sends a message, wait for 1 second and then get a response from the chatbot
    setTimeout(() => {
      console.log('Getting response from chatbot...');
  
      // Define the chat history and question
      const chatHistory = messages;
      const question = content;

      // Define the data to be sent in the POST request
      const data = {
          "chat_history": chatHistory,
          "question": question
      };
      console.log(data);
  
      axios.post('http://localhost:8000/chatbot/json_post/', data)
          .then(response => {
              // The response data is added to the messages state
              console.log(response);
              console.log('Response from chatbot: ', response['data']['latest_response']);
              setMessages(response['data']['chat_history']);
          })
          .catch(error => {
            
            setMessages(prevMessages => [...prevMessages, { role: 'ai', content: 'Please try again later.' }]);
            console.error('Error fetching data: ', error);
          });
     });
  }

  function handleSubmit(event) {
      event.preventDefault();
      roleSendMessage('user', inputText);
      setInputText('');
  }

  return (
    <div className="chat-interface">
        <h1 className='title'>Chat Interface</h1>
        <div className="chat-box">
        <div className="messages">
            <div className="message-list">
            {messages.map((message, index) => {
              if (message.role === 'ai') {
                // For AI messages, use dangerouslySetInnerHTML to render HTML content
                return (
                  <div key={index} className='message-inner'>
                    <div className='ai-icon' />
                    <div className='message'>
                      <h4 className='message-ai'>Health Bot</h4>
                      <ReactMarkdown className='message-text'>{message.content}</ReactMarkdown>
                      </div>
                  </div>
                );
              } else {
                // For user messages, render as plain text
                return (
                  <div key={index} className='message-inner'>
                    <div className='user-icon' />
                    <div className='message'>
                      <h4 className='message-user'>You</h4>
                      <p className='message-text'>{message.content}</p>
                    </div>
                  </div>
                );
              }
            })}

            <div ref={messagesEndRef} />
            </div>
            
            <form className="message-form" onSubmit={handleSubmit}>
              <textarea 
                value={inputText}
                onChange={event => setInputText(event.target.value)} 
                placeholder="Type your message here..."
              />
               <button type="submit">
               <FaChevronRight />
                </button>
            </form>
      </div>
      </div>
    </div>
  );
}

export default ChatInterface;