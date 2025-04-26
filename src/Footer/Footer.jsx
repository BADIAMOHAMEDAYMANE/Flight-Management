import React from "react";
import styles from "./Footer.module.css";

const Footer = () => {
  return (
    <footer className={styles.footer}>
      <div className={styles.footerContent}>
        <div className={styles.footerSection}>
          <h3>À propos</h3>
          <p>
            Mon Application est une solution innovante pour simplifier votre quotidien.
          </p>
        </div>
        
        <div className={styles.footerSection}>
          <h3>Liens utiles</h3>
          <ul>
            <li><a href="/conditions">Conditions d'utilisation</a></li>
            <li><a href="/confidentialite">Politique de confidentialité</a></li>
            <li><a href="/contact">Contactez-nous</a></li>
          </ul>
        </div>
        
        <div className={styles.footerSection}>
          <h3>Réseaux sociaux</h3>
          <div className={styles.socialIcons}>
            <a href="#"><i className="fab fa-facebook"></i></a>
            <a href="#"><i className="fab fa-twitter"></i></a>
            <a href="#"><i className="fab fa-instagram"></i></a>
            <a href="#"><i className="fab fa-linkedin"></i></a>
          </div>
        </div>
      </div>
      
      <div className={styles.footerBottom}>
        <p>&copy; 2025 Mon Application. Tous droits réservés.</p>
      </div>
    </footer>
  );
};

export default Footer;