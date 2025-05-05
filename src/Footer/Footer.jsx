import React from "react";
import styles from "./Footer.module.css";
import { Instagram, Facebook, Linkedin, Mail, MapPin, Phone } from "lucide-react";

const Footer = () => {
  return (
      <footer className={styles.footer}>
        <div className={styles.footerContainer}>
          <div className={styles.footerSection}>
            <h3 className={styles.footerTitle}>À propos</h3>
            <p className={styles.footerText}>
              Mon Application est une solution innovante pour simplifier votre quotidien. Nous nous engageons à vous offrir la meilleure expérience utilisateur possible.
            </p>
            <div className={styles.contactInfo}>
              <div className={styles.contactItem}>
                <MapPin size={16} /> <span>Gueliz, 40100 Paris</span>
              </div>
              <div className={styles.contactItem}>
                <Phone size={16} /> <span>+212 6 35 54 69 55</span>
              </div>
              <div className={styles.contactItem}>
                <Mail size={16} /> <span>contact@monapplication.fr</span>
              </div>
            </div>
          </div>

          <div className={styles.footerSection}>
            <h3 className={styles.footerTitle}>Liens utiles</h3>
            <ul className={styles.footerLinks}>
              <li><a href="/conditions">Conditions d'utilisation</a></li>
              <li><a href="/confidentialite">Politique de confidentialité</a></li>
              <li><a href="/contact">Contactez-nous</a></li>
            </ul>
          </div>

          <div className={styles.footerSection}>
            <h3 className={styles.footerTitle}>Réseaux sociaux</h3>
            <div className={styles.socialIcons}>
              <a href="https://instagram.com" className={styles.socialLink} aria-label="Instagram">
                <Instagram size={24} />
              </a>
              <a href="https://facebook.com" className={styles.socialLink} aria-label="Facebook">
                <Facebook size={24} />
              </a>
              <a href="https://linkedin.com" className={styles.socialLink} aria-label="LinkedIn">
                <Linkedin size={24} />
              </a>
            </div>
          </div>
        </div>

        <div className={styles.footerCopyright}>
          © 2025 Mon Application. Tous droits réservés.
        </div>
      </footer>
  );
};

export default Footer;