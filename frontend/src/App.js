import React, { useState } from 'react';
import Chat from './ChatInterface';
import { Accessibility } from 'accessibility';

window.addEventListener('load', function() {
  new Accessibility();
}, false);

function App() {
  return (
    <div style={{ height: '100vh', width: '100vw' }}>
      <Chat/>
    </div>
  );
}

export default App;
