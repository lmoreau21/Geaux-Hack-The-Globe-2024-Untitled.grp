import React, { useState } from 'react';
import { Container, TextField, Button, List, ListItem, ListItemText, Paper, Box } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import NavBar from './NavBar';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

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
    var source = 'gov_medicare';

    try {
      const response = await axios.post('http://127.0.0.1:8000/chatbot/', {
        question: inputText,
        chat_history: updatedMessages,
        date_source: source
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
    <Container maxWidth="sm">
      <Paper style={{ maxHeight: 500, overflow: 'auto', marginTop: 20, marginBottom: 20, padding: '20px' }}>
        <List>
          {messages.map((message, index) => (
            <ListItem key={index}>
              {/* Render the message content or Markdown based on the role */}
              {message.role === 'ai' ? (
                <Paper elevation={3} style={{ marginTop: 20, padding: '15px' }}>
                  <ReactMarkdown children={latestResponse} remarkPlugins={[remarkGfm]} />
                </Paper>
              ) : (
                <ListItemText primary={message.content} secondary={message.role === 'human' ? 'You' : 'AI'} />
              )}
            </ListItem>
          ))}
        </List>
        
      </Paper>
      <Box display="flex">
        <TextField
          variant="outlined"
          fullWidth
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Type your message here..."
        />
        <Button variant="contained" color="primary" endIcon={<SendIcon />} onClick={sendMessage}>
          Send
        </Button>
      </Box>
    </Container>
  );
}

function Home() {
  return <h1>Home Page</h1>;
}

function App() {
  return (
    <Router>
      <NavBar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/home" element={<Chat />} />
        {/* Add more routes as needed */}
      </Routes>
    </Router>
  );
}

export default App;