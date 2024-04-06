import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import { Link } from 'react-router-dom';

const NavBar = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          ChatGPT UI
        </Typography>
        <Box>
          <Link to="/home" style={{ color: 'white', textDecoration: 'none', marginRight: '10px' }}>Home</Link>
          <Link to="/usage" style={{ color: 'white', textDecoration: 'none', marginRight: '10px' }}>Usage</Link>
          <Link to="/privacy" style={{ color: 'white', textDecoration: 'none', marginRight: '10px' }}>Privacy</Link>
          <Link to="/resources" style={{ color: 'white', textDecoration: 'none', marginRight: '10px' }}>Resources</Link>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default NavBar;