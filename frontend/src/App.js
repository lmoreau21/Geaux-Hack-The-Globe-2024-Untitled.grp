import React, { useState } from 'react';
import { Container, TextField, Button, List, ListItem, ListItemText, Paper, Box } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import NavBar from './NavBar';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');

  const sendMessage = (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    setMessages([...messages, { id: Date.now(), text: inputText, sender: 'You' }]);
    setInputText('');
  };

  return (
    <Container maxWidth="sm">
      <Paper style={{ maxHeight: 500, overflow: 'auto', marginTop: 20, marginBottom: 20, padding: '20px' }}>
        <List>
          {messages.map((message, index) => (
            <ListItem key={index}>
              <ListItemText primary={message.text} secondary={message.sender} />
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
        <Route path="/chat" element={<Chat />} />
        {/* Add more routes as needed */}
      </Routes>
    </Router>
  );
}

export default App;