import React, { useState, useRef, useEffect } from 'react';
import {CircularProgress , Typography, Divider, Container, TextField, Button, List, ListItem, ListItemText, Paper, Box } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import getDataChoice, { data_choice } from './PersistentDrawer.jsx';

function Chat() {
  const [isLoading, setIsLoading] = useState(false);

  const [inputText, setInputText] = useState('');
  const [latestResponse, setLatestResponse] = useState('');
  const [chat_history, setChatHistory] = useState([]);
  const listEndRef = useRef(null);
  const [messages, setMessages] = useState([]);
  


  useEffect(() => {
    listEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    // Update the chat history state before sending the request
    const updatedMessages = [...messages, { role: "human", content: inputText }];
    setMessages(updatedMessages);
    setInputText('');

    setIsLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:8000/chatbot/', {
        question: inputText,
        chat_history: messages,
        date_source: data_choice
      });

      // Assuming the response is successful and in the expected format
      if (response.data && response.data.latest_response) {
        // Update both the chat history and the latest response
        console.log(response.data.latest_response)
        console.log(messages)
        setMessages(response.data.chat_history);
        setChatHistory(response.data.chat_history);
        setLatestResponse(response.data.latest_response);
      }
    } catch (error) {
      console.error('Error sending message:', error);
     
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container  style={{height: '79vh', display: 'flex', flexDirection: 'column', overflow:'hidden', padding:'0px'}}>
      
      <Container style={{ flexGrow: 1,overflow: 'auto', }}>
        <List>
          {messages.map((message, index) => (
            <Container>
              <Divider textAlign='left'> {message.role === 'human' ? 'You' : 'AI'} </Divider>
            <ListItem key={index}>
              {/* Render the message content or Markdown based on the role */}
              {message.role === 'ai' ? (
                <Box >
                  <ReactMarkdown children={message.content} remarkPlugins={[remarkGfm]} />
                </Box>
              ) : (
                <ListItemText primary={message.content} />
              )}
            
              
            </ListItem>
              
            </Container>
          ))}
          {isLoading && (
                <Container>
                <Divider textAlign='left'> AI </Divider>
                <Box display="flex" justifyContent="center">
                  <CircularProgress />
                </Box>
                </Container>
              )}
          <div ref={listEndRef} /> 
        </List>
        
      </Container>
      <Box display="flex" component="form" onSubmit={sendMessage}>
        <TextField
          variant="outlined"
          fullWidth
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Type your message here..."
        />
        <Button type="submit" variant="contained" color="primary" endIcon={<SendIcon />}>
          Send
        </Button>
      </Box>
      
      <Typography variant="h10" align="center" paddingTop={'3px'}> We make mistakes too! Please be patient with us. </Typography>
      
    </Container>
  );
}

export default Chat;