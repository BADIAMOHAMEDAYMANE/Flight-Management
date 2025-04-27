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
        const response = await axios.get(
          `http://api.aviationstack.com/v1/flights`,
          {
            params: {
              access_key: "3b891a0d3562b8388f071fe2e76c1da4",
              limit: 25,
              flight_status: "active",
            },
          }
        );

        if (response.data.error) {
          throw new Error(response.data.error.info);
        }

        // Filter flights that have both arrival and departure data
        setFlights(response.data.data.filter((f) => f.arrival && f.departure));
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchFlights();
  }, []);

  // Filter current and future flights for rendering
  const currentAndFutureFlights = flights.filter((flight) => {
    // Get current time in milliseconds
    const currentTime = new Date().getTime();

    // Get scheduled departure time in milliseconds
    const departureTime = new Date(flight.departure.scheduled).getTime();

    // Only show flights where departure time is in the future
    return departureTime >= currentTime;
  });

  return (
    <div className={styles.flightDestinations}>
      <h2>Vols en cours</h2>

      {loading && <p>Chargement en cours...</p>}
      {error && (
        <p className={styles.error}>
          Erreur: {error} (affichage de données exemple)
        </p>
      )}

      {!loading && currentAndFutureFlights.length === 0 && (
        <p>Aucun vol à venir n'est disponible.</p>
      )}

      <div className={styles.flightsList}>
        {currentAndFutureFlights.map((flight, index) => {
          const { departure, arrival, airline } = flight;
          const {
            airport: departureAirport,
            iata: departureIata,
            scheduled,
          } = departure;
          const { airport: arrivalAirport, iata: arrivalIata } = arrival;
          const { name: airlineName } = airline;

          return (
            <div key={index} className={styles.flightCard}>
              <h3>
                {departureAirport} ({departureIata}) → {arrivalAirport} (
                {arrivalIata})
              </h3>
              <p>Compagnie: {airlineName}</p>
              <p>Départ: {new Date(scheduled).toLocaleString()}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default FlightDestinations;
