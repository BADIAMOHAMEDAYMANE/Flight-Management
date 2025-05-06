import React, { useState, useEffect } from 'react';
import styles from './DestinationDetails.module.css';

const DestinationDetails = ({ destination, onBack }) => {
  const [loading, setLoading] = useState(true);
  const [destinationData, setDestinationData] = useState({
    weather: null,
    flights: [],
    accommodations: []
  });
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDestinationData = async () => {
      try {
        setLoading(true);
        const response = await fetch(`http://localhost:5000/api/destination-details`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ destination })
        });

        if (!response.ok) {
          throw new Error('Failed to fetch destination data');
        }

        const data = await response.json();
        console.log('Destination data received:', data);
        setDestinationData(data);
      } catch (err) {
        console.error('Error fetching destination data:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (destination) {
      fetchDestinationData();
    }
  }, [destination]);

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <button className={styles.backButton} onClick={onBack}>← Back</button>
          <h1>Loading details for {destination}...</h1>
        </div>
        <div className={styles.loadingSpinner}></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <button className={styles.backButton} onClick={onBack}>← Back</button>
          <h1>Error loading {destination}</h1>
        </div>
        <p className={styles.error}>{error}</p>
      </div>
    );
  }

  const { weather, flights, accommodations } = destinationData;

  // Helper function to format price from string or number
  const formatPrice = (price) => {
    if (typeof price === 'number') return `$${price}`;
    if (typeof price === 'string') {
      // If already has $ symbol, return as is
      if (price.includes('$')) return price;
      return `$${price}`;
    }
    return 'Price not available';
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <button className={styles.backButton} onClick={onBack}>← Back</button>
        <h1>Travel Details: {destination}</h1>
      </div>

      <div className={styles.contentGrid}>
        {/* Weather Section */}
        <div className={styles.section}>
          <h2>Weather</h2>
          {weather ? (
            <div className={styles.weatherCard}>
              <div className={styles.weatherMain}>
                <span className={styles.temperature}>{weather.temperature}°C</span>
                <span className={styles.condition}>{weather.condition}</span>
              </div>
              <div className={styles.weatherDetails}>
                <p>Humidity: {weather.humidity}%</p>
                <p>Wind: {weather.wind} km/h</p>
              </div>
              <div className={styles.forecast}>
                <h3>5-Day Forecast</h3>
                <div className={styles.forecastItems}>
                  {weather.forecast && weather.forecast.map((day, idx) => (
                    <div key={idx} className={styles.forecastDay}>
                      <div>{day.day}</div>
                      <div>{day.temperature}°C</div>
                      <div>{day.condition}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <p>No weather data available</p>
          )}
        </div>

        {/* Flights Section */}
        <div className={styles.section}>
          <h2>Best Flights</h2>
          {flights && flights.length > 0 ? (
            <div className={styles.flightsList}>
              {flights.map((flight, idx) => (
                <div key={idx} className={styles.flightCard}>
                  <div className={styles.flightHeader}>
                    <span className={styles.airline}>{flight.airline}</span>
                    <span className={styles.price}>${flight.price}</span>
                  </div>
                  <div className={styles.flightRoute}>
                    <div className={styles.departure}>
                      <div className={styles.time}>{flight.departureTime}</div>
                      <div className={styles.airport}>{flight.departureAirport}</div>
                    </div>
                    <div className={styles.flightDuration}>
                      <div className={styles.durationLine}></div>
                      <div className={styles.duration}>{flight.duration}</div>
                    </div>
                    <div className={styles.arrival}>
                      <div className={styles.time}>{flight.arrivalTime}</div>
                      <div className={styles.airport}>{flight.arrivalAirport}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p>No flight information available</p>
          )}
        </div>

        {/* Accommodations Section */}
        <div className={styles.section}>
          <h2>Accommodations</h2>
          {accommodations && accommodations.length > 0 ? (
            <div className={styles.accommodationsList}>
              {accommodations.map((hotel, idx) => (
                <div key={idx} className={styles.hotelCard}>
                  <div className={styles.hotelImage}>
                    <div className={styles.imagePlaceholder}>
                      <span>{hotel.name.substring(0, 2)}</span>
                    </div>
                  </div>
                  <div className={styles.hotelInfo}>
                    <h3>{hotel.name}</h3>
                    <div className={styles.hotelRating}>
                      {Array(hotel.rating).fill('★').join('')}
                      {Array(5 - Math.min(5, hotel.rating)).fill('☆').join('')}
                    </div>
                    <p className={styles.hotelLocation}>{hotel.location}</p>
                    <p className={styles.hotelPrice}>{formatPrice(hotel.price)} per night</p>
                    {hotel.amenities && hotel.amenities.length > 0 && (
                      <p className={styles.hotelAmenities}>
                        {hotel.amenities.join(' • ')}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p>No accommodation information available</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default DestinationDetails;