import React, { useState } from 'react';

import PersistentDrawer from './PersistentDrawer';
import { Accessibility } from 'accessibility';

window.addEventListener('load', function() {
  var options = {
    textToSpeech: true,
    speechToText: true,
    icon: {
      img: 'accessible',
      position: {
            top: { size: 100, units: 'px' },
            right: { size: 15, units: 'px' },
            type: 'fixed'
        }
    }
    

};
options.textToSpeechLang = 'en-US'; // or any other language
options.speechToTextLang = 'en-US'; // or any other language
  new Accessibility(options);
}, false);

function App() {
  return (
    <PersistentDrawer/>
  );
}

export default App;
