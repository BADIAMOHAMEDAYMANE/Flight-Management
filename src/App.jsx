import React from 'react';
import Navbar from './Navbar/Navbar';
import Footer from './Footer/Footer';
import './App.module.css';
import Flights from './Body/Body';
import FlightDestinations from './TravelPlan/TravelPlan';

function App() {
  return (
    <div className="app">
      <Navbar />
      <FlightDestinations/>
      <Flights/>
      <Footer />
    </div>
  );
}

export default App;