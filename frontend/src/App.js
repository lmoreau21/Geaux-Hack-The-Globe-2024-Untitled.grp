import React, { useState } from 'react';
import { Box } from '@mui/material';

import Chat from './Chat';
import PersistentDrawer from './PersistentDrawer';
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
    <PersistentDrawer/>
  );
}

export default App;
