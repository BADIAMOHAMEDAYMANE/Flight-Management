import React, { useState, useContext } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './Navbar/Navbar';
import Footer from './Footer/Footer';
import './App.module.css';
import Flights from './Body/Body';
import FlightDestinations from './TravelPlan/TravelPlan';
import Chatbot from './Chatbot/Chatbot';
import DestinationDetails from './DestinationDetails/DestinationDetails';
import LoginPage from './Login/LoginPage';
import { AuthContext } from './AuthContext';

function App() {
  const [showChatbot, setShowChatbot] = useState(false);
  const [selectedDestination, setSelectedDestination] = useState(null);
  const { user, isLoading } = useContext(AuthContext);

  const handleDestinationSelect = (destination) => {
    setSelectedDestination(destination);
    setShowChatbot(false);
  };

  const handleBackFromDetails = () => {
    setSelectedDestination(null);
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="app">
      {user ? (
        <>
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
        </>
      ) : (
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      )}
    </div>
  );
}

export default App;