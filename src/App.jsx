import React, { useState } from 'react';
import Navbar from './Navbar/Navbar';
import Footer from './Footer/Footer';
import './App.module.css';
import Flights from './Body/Body';
import FlightDestinations from './TravelPlan/TravelPlan';
import Chatbot from './Chatbot/Chatbot'; // Import the Chatbot component

function App() {
  const [showChatbot, setShowChatbot] = useState(false);

  return (
    <div className="app">
      <Navbar onAssistantClick={() => setShowChatbot(true)} />
      
      {showChatbot ? (
        <Chatbot onClose={() => setShowChatbot(false)} />
      ) : (
        <>
          <FlightDestinations />
          <Flights />
        </>
      )}
      
      <Footer />
    </div>
  );
}

export default App;