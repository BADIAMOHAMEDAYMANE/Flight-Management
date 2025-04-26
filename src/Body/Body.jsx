import React from "react";
import styles from "./Body.module.css";
import madridImage from "../assets/Aymane.jpg";

const Photo = () => {
  const destinations = [
    { city: "Al Hoceima", price: 823 },
    { city: "Errachidia", price: 823 },
    { city: "Zagora", price: 823 },
    { city: "Ouarzazate", price: 823 },
    { city: "Tétouan", price: 823 },
    { city: "Guelmim", price: 1003 },
    { city: "Tan-Tan", price: 1003 },
    { city: "Oujda", price: 1023 },
  ];

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
        {destinations.map((destination, index) => (
          <div className={styles.destinationItem} key={index}>
            <span className={styles.cityName}>{destination.city}</span>
            <div className={styles.priceContainer}>
              <span className={styles.from}>from</span>
              <span className={styles.priceValue}>{destination.price}</span>
              <span className={styles.currency}>MAD 1/V</span>
            </div>
          </div>
        ))}
        <div className={styles.viewMore}>
          <a href="#">Voir plus d'offres →</a>
        </div>
      </div>
    </div>
  );
};

export default Photo;
