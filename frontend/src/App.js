import React, { useState } from 'react';
import { Box } from '@mui/material';

import Chat from './Chat';
import PersistentDrawer from './PersistentDrawer';
import Chat from './ChatInterface';
import { Accessibility } from 'accessibility';

window.addEventListener('load', function() {
  new Accessibility();
}, false);

function App() {
  const [open, setOpen] = React.useState(true);
  const handleDrawerOpen = () => {
      setOpen(true);
  };
  const handleDrawerClose = () => {
      setOpen(false);
  };

  return (
    <Box>
      <Chat handleDrawerOpen={handleDrawerOpen}/>
      <PersistentDrawer open={open} handleDrawerClose={handleDrawerClose}/>
    </Box>
  );
}

export default App;
