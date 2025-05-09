import React, { useState, useEffect } from "react";
import styles from "./Body.module.css";
import madridImage from "../assets/Aymane.jpg";

const Photo = () => {
  const [destinations, setDestinations] = useState([]);
  const [visibleCount, setVisibleCount] = useState(10);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_KEY = "b75e1cef2e2b27b7107f56b5a5f0cf0c";

  const fetchFlights = async () => {
    try {
      setLoading(true);
      const response = await fetch(
          `http://api.aviationstack.com/v1/flights?access_key=${API_KEY}&dep_country=MA&limit=100`
      );

      if (!response.ok) {
        throw new Error("Erreur lors de la récupération des données");
      }

      const { data, error: apiError } = await response.json();

      if (apiError) {
        throw new Error(apiError.info);
      }

      const processedDestinations = [];
      const uniqueDestinations = new Set();

      for (const flight of data) {
        const { arrival, flight: flightInfo, departure } = flight;
        const { airport: destinationCity, country: destinationCountry, country_code } = arrival;

        if (
            uniqueDestinations.has(destinationCity) ||
            country_code === "MA" ||
            !destinationCity
        ) {
          continue;
        }

        let price;
        if (flightInfo.distance) {
          price = Math.round(flightInfo.distance);
        } else if (arrival.scheduled && departure.scheduled) {
          const arrTime = new Date(arrival.scheduled);
          const depTime = new Date(departure.scheduled);
          const flightDuration = (arrTime - depTime) / (1000 * 60 * 60);
          price = Math.round(flightDuration * 500);
        } else {
          const flightNumber = parseInt(flightInfo.number.replace(/\D/g, "")) || 1000;
          price = flightNumber;
        }

        const displayName = destinationCity + (destinationCountry ? `, ${destinationCountry}` : "");

        processedDestinations.push({
          city: displayName,
          price
        });

        uniqueDestinations.add(destinationCity);
      }

      if (processedDestinations.length === 0) {
        throw new Error("Aucun vol trouvé au départ du Maroc");
      }

      setDestinations(processedDestinations);
    } catch (err) {
      console.error("Erreur API:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFlights();
  }, []);

  const handleVoirPlus = () => {
    setVisibleCount((prev) => prev + 10);
  };

  return (
      <div className={styles.travelContainer}>
        <div className={styles.madridCard}>
          <div
              className={styles.madridImage}
              style={{ backgroundImage: `url(${madridImage})` }}
          >
            <div className={styles.madridOverlay}>
              <h2>Madrid</h2>
              <p>from</p>
              <div className={styles.price}>2.181</div>
              <span className={styles.priceLabel}>MAD|Round Trip</span>
            </div>
          </div>
        </div>

        <div className={styles.destinationsList}>
          {loading ? (
              <div className={styles.loading}>Chargement des destinations...</div>
          ) : error ? (
              <div className={styles.error}>{error}</div>
          ) : (
              <>
                {destinations.slice(0, visibleCount).map(({ city, price }, index) => (
                    <div className={styles.destinationItem} key={index}>
                      <span className={styles.cityName}>{city}</span>
                      <div className={styles.priceContainer}>
                        <span className={styles.from}>from</span>
                        <span className={styles.priceValue}>{price}</span>
                        <span className={styles.currency}>MAD 1/V</span>
                      </div>
                    </div>
                ))}
              </>
          )}

          {!loading && visibleCount < destinations.length && (
              <div className={styles.viewMore}>
                <button onClick={handleVoirPlus}>Voir plus d'offres →</button>
              </div>
          )}

          {!loading && visibleCount >= destinations.length && (
              <div className={styles.noMore}>Toutes les offres sont affichées.</div>
          )}
        </div>
      </div>
  );
};

export default Photo;
