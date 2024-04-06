import React, { useState } from 'react';

import PersistentDrawer from './PersistentDrawer';
import { Accessibility } from 'accessibility';

window.addEventListener('load', function() {
  new Accessibility();
}, false);

function App() {
  return (
    <PersistentDrawer/>
  );
}

export default App;
