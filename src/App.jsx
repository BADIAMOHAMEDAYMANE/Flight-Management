import React, { useState } from 'react';
import Navbar from './Navbar/Navbar';
import Footer from './Footer/Footer';
import './App.module.css';
import Flights from './Body/Body';
import FlightDestinations from './TravelPlan/TravelPlan';
import Chatbot from './Chatbot/Chatbot';
import DestinationDetails from './DestinationDetails/DestinationDetails';

function App() {
  const [showChatbot, setShowChatbot] = useState(false);
  const [selectedDestination, setSelectedDestination] = useState(null);

  const handleDestinationSelect = (destination) => {
    setSelectedDestination(destination);
    setShowChatbot(false); // Close chatbot when showing destination details
  };

  const handleBackFromDetails = () => {
    setSelectedDestination(null);
  };

  return (
    <div className="app">
      <Navbar onAssistantClick={() => setShowChatbot(true)} />
      
      {selectedDestination ? (
        <DestinationDetails 
          destination={selectedDestination} 
          onBack={handleBackFromDetails} 
        />
      ) : showChatbot ? (
        <Chatbot 
          onClose={() => setShowChatbot(false)} 
          onDestinationSelect={handleDestinationSelect}
        />
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