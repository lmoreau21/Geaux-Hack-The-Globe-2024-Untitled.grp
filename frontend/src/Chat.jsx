import React, { useState } from 'react';
import { Container, TextField, Button, List, ListItem, ListItemText, Paper, Box } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import getDataChoice, { data_choice } from './PersistentDrawer.jsx';
function Chat() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [latestResponse, setLatestResponse] = useState('');

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    // Update the chat history state before sending the request
    const updatedMessages = [...messages, { role: "human", content: inputText }];
    setMessages(updatedMessages);
    setInputText('');


    try {
      const response = await axios.post('http://127.0.0.1:8000/chatbot/', {
        question: inputText,
        chat_history: updatedMessages,
        date_source: data_choice
      });

      // Assuming the response is successful and in the expected format
      if (response.data && response.data.latest_response) {
        // Update both the chat history and the latest response
        setMessages(response.data.chat_history);
        setLatestResponse(response.data.latest_response);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      // Handle error scenarios appropriately
    }
  };

  return (
    <Container style={{ height: '80vh', width: '100%', display: 'flex', flexDirection: 'column' }}>
      <Paper style={{ flexGrow: 1, overflow: 'auto', marginTop: 10, marginBottom: 0, padding: '0px' }}>
        <List>
          {messages.map((message, index) => (
            <ListItem key={index}>
              {/* Render the message content or Markdown based on the role */}
              {message.role === 'ai' ? (
                <Paper elevation={3} style={{ marginTop: 10, padding: '5px' }}>
                  <ReactMarkdown children={latestResponse} remarkPlugins={[remarkGfm]} />
                </Paper>
              ) : (
                <ListItemText primary={message.content} secondary={message.role === 'human' ? 'You' : 'AI'} />
              )}
            </ListItem>
          ))}
        </List>
        
      </Paper>
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
    </Container>
  );
}

export default Chat;