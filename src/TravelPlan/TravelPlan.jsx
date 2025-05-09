import React, { useState, useEffect } from "react";
import styles from "./TravelPlan.module.css";

const FlightDestinations = () => {
  const [flights, setFlights] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  const [flightStatus, setFlightStatus] = useState("active");
  const [sortBy, setSortBy] = useState("departure");
  const [lastUpdated, setLastUpdated] = useState(null);
  const [apiAvailable, setApiAvailable] = useState(true);


  const API_KEY = "b75e1cef2e2b27b7107f56b5a5f0cf0c";
  const FLIGHTS_PER_PAGE = 10;

  const fetchFlights = async () => {
    if (!apiAvailable) return;

    try {
      setLoading(true);
      setError(null);
      const params = new URLSearchParams({
        access_key: API_KEY,
        limit: FLIGHTS_PER_PAGE,
        offset: (page - 1) * FLIGHTS_PER_PAGE,
        flight_status: flightStatus,
      });


      if (searchTerm.match(/^[A-Za-z]{2}\d+$/)) {
        params.append('flight_iata', searchTerm.toUpperCase());
      } else if (searchTerm) {
        params.append('airline_name', searchTerm);
      }

      // Tentative avec un service de proxy CORS alternatif
      const apiUrl = `https://api.allorigins.win/get?url=${encodeURIComponent(`https://api.aviationstack.com/v1/flights?${params.toString()}`)}`;

      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        timeout: 10000
      });

      if (!response.ok) {
        throw new Error(`Erreur API: ${response.status}`);
      }

      const { contents } = await response.json();
      const { data = [] } = JSON.parse(contents);


      const currentTime = new Date();
      const filteredFlights = data
          .filter(({ departure }) => {
            if (!departure?.scheduled) return false;
            const departureTime = new Date(departure.scheduled);
            return departureTime > currentTime;
          })
          .sort((a, b) => {
            const dateA = new Date(sortBy === "departure" ? a.departure.scheduled : a.arrival.scheduled);
            const dateB = new Date(sortBy === "departure" ? b.departure.scheduled : b.arrival.scheduled);
            return dateA - dateB;
          });

      setFlights(filteredFlights);
      setLastUpdated(new Date());
      setLoading(false);

    } catch (err) {
      console.error("Erreur lors de la récupération des vols:", err);
      setLoading(false);


      setError(`Erreur: Impossible de se connecter à l'API de vols. ${err.message}`);


      setTimeout(() => {
        setApiAvailable(true);
        setError(null);
      }, 60000);
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    const timer = setTimeout(() => {
      fetchFlights();
    }, 500);

    return () => {
      controller.abort();
      clearTimeout(timer);
    };
  }, [page, flightStatus, searchTerm, sortBy, apiAvailable]);

  const formatTime = (dateString, timezone) => {
    if (!dateString) return '--:--';
    try {
      return new Date(dateString).toLocaleTimeString('fr-FR', {
        timeZone: timezone,
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return '--:--';
    }
  };

  const formatDate = (dateString, timezone) => {
    if (!dateString) return '--/--';
    try {
      return new Date(dateString).toLocaleDateString('fr-FR', {
        timeZone: timezone,
        day: '2-digit',
        month: '2-digit'
      });
    } catch {
      return '--/--';
    }
  };

  const handleRetry = () => {
    setPage(1);
    setError(null);
    setApiAvailable(true);
    fetchFlights();
  };

  return (
      <div className={styles.container}>
        <header className={styles.header}>
          <h1>Vols mondiaux en temps réel</h1>
          {lastUpdated && (
              <div className={styles.lastUpdated}>
                Mis à jour: {lastUpdated.toLocaleTimeString('fr-FR')}
              </div>
          )}
        </header>

        <div className={styles.controls}>
          <div className={styles.searchGroup}>
            <input
                type="text"
                placeholder="Rechercher un vol (ex: AF123) ou compagnie"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                disabled={!apiAvailable}
            />
            <button
                onClick={handleRetry}
                className={styles.refreshButton}
                disabled={loading || !apiAvailable}
            >
              {loading ? 'Chargement...' : 'Actualiser'}
            </button>
          </div>

          <div className={styles.filterGroup}>
            <select
                value={flightStatus}
                onChange={(e) => setFlightStatus(e.target.value)}
                disabled={loading}
            >
              <option value="active">En vol</option>
              <option value="scheduled">Programmé</option>
              <option value="landed">Atterri</option>
              <option value="cancelled">Annulé</option>
            </select>

            <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                disabled={loading}
            >
              <option value="departure">Tri par départ ↑</option>
              <option value="arrival">Tri par arrivée ↓</option>
            </select>
          </div>
        </div>

        {error && (
            <div className={styles.error}>
              <p>{error}</p>
              {error.includes("Limite") && (
                  <div className={styles.solution}>
                    <a href="https://aviationstack.com/signup" target="_blank" rel="noopener noreferrer">
                      Obtenir une clé API premium
                    </a>
                  </div>
              )}
              <button onClick={handleRetry} className={styles.retryButton}>
                Réessayer
              </button>
            </div>
        )}

        {loading && (
            <div className={styles.loading}>
              <div className={styles.spinner}></div>
              <p>Recherche des vols en cours...</p>
            </div>
        )}

        <div className={styles.flightsGrid}>
          {flights.map(({ airline, flight, flight_status, departure, arrival, duration }) => (
              <div key={`${flight?.iata}-${departure?.scheduled}`}
                   className={styles.flightCard}>
                <div className={styles.cardHeader}>
                  <div className={styles.airlineInfo}>
                    {airline?.iata && (
                        <img
                            src={`https://daisycon.io/images/airline/?width=100&height=100&color=ffffff&iata=${airline.iata}`}
                            alt={airline.name}
                            className={styles.airlineLogo}
                            onError={(e) => {
                              e.target.style.display = 'none';
                            }}
                        />
                    )}
                    <div>
                      <h3>{airline?.name || 'Compagnie inconnue'}</h3>
                      <p className={styles.flightNumber}>
                        {flight?.iata || 'N/A'}
                      </p>
                    </div>
                  </div>
                  <span className={`${styles.status} ${flight_status ? styles[flight_status] : ''}`}>
                {flight_status?.toUpperCase() || 'INCONNU'}
              </span>
                </div>

                <div className={styles.routeInfo}>
                  <div className={styles.airport}>
                    <h4>{departure?.iata || '---'}</h4>
                    <p>{departure?.airport || 'Aéroport inconnu'}</p>
                    <div className={styles.timeInfo}>
                      <span>{formatDate(departure?.scheduled, departure?.timezone)}</span>
                      <time>{formatTime(departure?.scheduled, departure?.timezone)}</time>
                    </div>
                    <p className={styles.terminal}>
                      Terminal: {departure?.terminal || '?'} • Porte: {departure?.gate || '?'}
                    </p>
                  </div>

                  <div className={styles.flightDuration}>
                    <div className={styles.duration}>
                      {duration ? `${Math.floor(duration / 60)}h ${duration % 60}min` : '--h --min'}
                    </div>
                    <div className={styles.arrow}>→</div>
                  </div>

                  <div className={styles.airport}>
                    <h4>{arrival?.iata || '---'}</h4>
                    <p>{arrival?.airport || 'Aéroport inconnu'}</p>
                    <div className={styles.timeInfo}>
                      <span>{formatDate(arrival?.scheduled, arrival?.timezone)}</span>
                      <time>{formatTime(arrival?.scheduled, arrival?.timezone)}</time>
                    </div>
                    <p className={styles.terminal}>
                      Terminal: {arrival?.terminal || '?'} • Porte: {arrival?.gate || '?'}
                    </p>
                  </div>
                </div>
              </div>
          ))}
        </div>

        {!loading && flights.length === 0 && !error && (
            <div className={styles.noResults}>
              <p>Aucun vol trouvé pour ces critères</p>
              <button onClick={() => {
                setSearchTerm("");
                setFlightStatus("active");
                setPage(1);
              }}>
                Réinitialiser les filtres
              </button>
            </div>
        )}

        {flights.length > 0 && (
            <div className={styles.pagination}>
              <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1 || loading}
              >
                Précédent
              </button>

              <span>Page {page}</span>

              <button
                  onClick={() => setPage(p => p + 1)}
                  disabled={loading || flights.length < FLIGHTS_PER_PAGE}
              >
                Suivant
              </button>
            </div>
        )}
      </div>
  );
};

export default FlightDestinations;