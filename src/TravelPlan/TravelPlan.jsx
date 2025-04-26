import React, { useState, useEffect } from "react";
import axios from "axios";
import styles from "./TravelPlan.module.css";

const FlightDestinations = () => {
  const [flights, setFlights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchFlights = async () => {
      try {
        const response = await axios.get(`http://api.aviationstack.com/v1/flights`, {
          params: {
            access_key: '3b891a0d3562b8388f071fe2e76c1da4',
            limit: 25,
            flight_status: 'active'
          }
        });

        if (response.data.error) {
          throw new Error(response.data.error.info);
        }

        setFlights(response.data.data.filter(f => f.arrival && f.departure));
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
        // Solution de repli avec des données mockées
        setFlights(mockFlights);
      }
    };

    fetchFlights();
  }, []);

  // Données mockées pour le fallback
  const mockFlights = [
    {
      departure: { iata: 'LAX', airport: 'Los Angeles', scheduled: '2023-06-15T10:00:00' },
      arrival: { iata: 'JFK', airport: 'New York JFK' },
      airline: { name: 'American Airlines' }
    },
    {
      departure: { iata: 'CDG', airport: 'Paris Charles de Gaulle', scheduled: '2023-06-15T12:30:00' },
      arrival: { iata: 'LHR', airport: 'London Heathrow' },
      airline: { name: 'Air France' }
    },
    // Ajoutez d'autres vols fictifs...
  ];

  return (
      <div className={styles.flightDestinations}>
        <h2>Vols en cours</h2>

        {loading && <p>Chargement en cours...</p>}
        {error && <p className={styles.error}>Erreur: {error} (affichage de données exemple)</p>}

        <div className={styles.flightsList}>
          {flights.map((flight, index) => (
              <div key={index} className={styles.flightCard}>
                <h3>{flight.departure.airport} ({flight.departure.iata}) → {flight.arrival.airport} ({flight.arrival.iata})</h3>
                <p>Compagnie: {flight.airline.name}</p>
                <p>Départ: {new Date(flight.departure.scheduled).toLocaleString()}</p>
              </div>
          ))}
        </div>
      </div>
  );
};

export default FlightDestinations;