import React from "react";
import styles from "./Navbar.module.css";
import logoImage from "../assets/Avion.png";

const Navbar = () => {
  return (
    <nav className={styles.navbar}>
      <div className={styles.logoContainer}>
        <img 
          src={logoImage} 
          alt="Logo de l'application" 
          className={styles.logo} 
        />
      </div>
      <ul className={styles.links}>
        <li>
          <a href="#">Accueil</a>
        </li>
        <li>
          <a href="#">Destinations</a>
        </li>
        <li>
          <a href="#">Contact</a>
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;