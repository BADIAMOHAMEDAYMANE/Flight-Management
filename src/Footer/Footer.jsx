import React from "react";
import styles from "./Footer.module.css";
import { Instagram, Facebook, Linkedin, Mail, MapPin, Phone } from "lucide-react";
import logoImage from "../assets/logo.PNG";

const Footer = () => {
  return (
    <footer className={styles.footer}>
      <div className={styles.footerContainer}>
        {/* First Column - Logo and About */}
        <div className={styles.footerSection}>
          <div className={styles.logoContainer}>
            <img src={logoImage} alt="TravelMate Logo" className={styles.footerLogo} />
            <p className={styles.tagline}>TRAVEL MORE, SPEND LESS</p>
          </div>
          <p className={styles.footerText}>
            TravelMate revolutionizes travel planning by offering the best flight deals 
            and personalized recommendations for your perfect getaway.
          </p>
          <div className={styles.contactInfo}>
            <div className={styles.contactItem}>
              <MapPin size={16} className={styles.contactIcon} />
              <span>Gueliz, 40100 Marrakech</span>
            </div>
            <div className={styles.contactItem}>
              <Phone size={16} className={styles.contactIcon} />
              <span>+212 6 35 54 69 55</span>
            </div>
            <div className={styles.contactItem}>
              <Mail size={16} className={styles.contactIcon} />
              <span>contact@travelmate.com</span>
            </div>
          </div>
        </div>

        {/* Second Column - Quick Links */}
        <div className={styles.footerSection}>
          <h3 className={styles.footerTitle}>Quick Links</h3>
          <ul className={styles.footerLinks}>
            <li>
              <a href="/about">About Us</a>
            </li>
            <li>
              <a href="/destinations">Popular Destinations</a>
            </li>
            <li>
              <a href="/deals">Special Deals</a>
            </li>
            <li>
              <a href="/blog">Travel Blog</a>
            </li>
            <li>
              <a href="/faq">FAQs</a>
            </li>
          </ul>
        </div>

        {/* Third Column - Legal */}
        <div className={styles.footerSection}>
          <h3 className={styles.footerTitle}>Legal</h3>
          <ul className={styles.footerLinks}>
            <li>
              <a href="/terms">Terms of Service</a>
            </li>
            <li>
              <a href="/privacy">Privacy Policy</a>
            </li>
            <li>
              <a href="/cookies">Cookie Policy</a>
            </li>
            <li>
              <a href="/refund">Refund Policy</a>
            </li>
          </ul>
        </div>

        {/* Fourth Column - Social Media */}
        <div className={styles.footerSection}>
          <h3 className={styles.footerTitle}>Connect With Us</h3>
          <div className={styles.socialIcons}>
            <a 
              href="https://instagram.com" 
              className={styles.socialLink}
              aria-label="Instagram"
            >
              <Instagram size={20} />
            </a>
            <a 
              href="https://facebook.com" 
              className={styles.socialLink}
              aria-label="Facebook"
            >
              <Facebook size={20} />
            </a>
            <a 
              href="https://twitter.com" 
              className={styles.socialLink}
              aria-label="Twitter"
            >
              <Linkedin size={20} />
            </a>
            <a 
              href="mailto:contact@travelmate.com" 
              className={styles.socialLink}
              aria-label="Email"
            >
              <Mail size={20} />
            </a>
          </div>
          
          <div className={styles.newsletter}>
            <h4 className={styles.newsletterTitle}>Newsletter</h4>
            <p className={styles.newsletterText}>
              Subscribe for exclusive deals and travel tips
            </p>
            <div className={styles.newsletterForm}>
              <input 
                type="email" 
                placeholder="Your email address" 
                className={styles.newsletterInput}
              />
              <button className={styles.newsletterButton}>
                Subscribe
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className={styles.footerCopyright}>
        <div className={styles.copyrightContainer}>
          <p>© {new Date().getFullYear()} TravelMate. All rights reserved.</p>
          <div className={styles.paymentMethods}>
            <span className={styles.paymentIcon}>💳</span>
            <span className={styles.paymentIcon}>📱</span>
            <span className={styles.paymentIcon}>💰</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;