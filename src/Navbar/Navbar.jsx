import React, { useState, useEffect } from "react";
import styles from "./Navbar.module.css";
import logoImage from "../assets/Avion.png";
import { Menu, X, ChevronDown, User, LogIn, MessageCircle } from "lucide-react"; // Added MessageCircle

const Navbar = ({ onAssistantClick }) => {  // Added prop
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isScrolled, setIsScrolled] = useState(false);
    const [activeLink, setActiveLink] = useState('accueil');

    // Gestion du défilement pour la transparence de la navbar
    useEffect(() => {
        const handleScroll = () => {
            if (window.scrollY > 10) {
                setIsScrolled(true);
            } else {
                setIsScrolled(false);
            }
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    // Gestion des liens actifs
    const handleLinkClick = (link) => {
        setActiveLink(link);
        setIsMenuOpen(false);
        if (link === 'assistant') {
            onAssistantClick(); // Trigger chatbot display
        }
    };

    return (
        <nav className={`${styles.navbar} ${isScrolled ? styles.scrolled : ''}`}>
            <div className={styles.logoContainer}>
                <img
                    src={logoImage}
                    alt="Logo de l'application"
                    className={styles.logo}
                />
                <span className={styles.logoText}>Air Voyage</span>
            </div>

            <ul className={`${styles.links} ${isMenuOpen ? styles.open : ''}`}>
                <li>
                    <a
                        href="#"
                        className={activeLink === 'accueil' ? styles.active : ''}
                        onClick={() => handleLinkClick('accueil')}
                    >
                        Accueil
                    </a>
                </li>
                <li>
                    <a
                        href="#"
                        className={activeLink === 'destinations' ? styles.active : ''}
                        onClick={() => handleLinkClick('destinations')}
                    >
                        Destinations
                    </a>
                </li>
                <li>
                    <a
                        href="#"
                        className={activeLink === 'vols' ? styles.active : ''}
                        onClick={() => handleLinkClick('vols')}
                    >
                        Vols
                    </a>
                </li>
                <li>
                    <a
                        href="#"
                        className={activeLink === 'promos' ? styles.active : ''}
                        onClick={() => handleLinkClick('promos')}
                    >
                        Promotions
                    </a>
                </li>
                <li>
                    <a
                        href="#"
                        className={activeLink === 'contact' ? styles.active : ''}
                        onClick={() => handleLinkClick('contact')}
                    >
                        Contact
                    </a>
                </li>
                {/* Only added this new item */}
                <li>
                    <a
                        href="#"
                        className={activeLink === 'assistant' ? styles.active : ''}
                        onClick={() => handleLinkClick('assistant')}
                    >
                        <MessageCircle size={16} style={{ marginRight: '6px' }} />
                        Assistant
                    </a>
                </li>
            </ul>

            <div className={styles.buttons}>
                <button className={styles.signInButton}>
                    <LogIn size={16} style={{ marginRight: '4px' }} />
                    Connexion
                </button>
                <button className={styles.signUpButton}>Inscription</button>
            </div>

            <button
                className={`${styles.menuButton} ${isMenuOpen ? styles.open : ''}`}
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                aria-label="Menu"
            >
                <span className={styles.menuIcon}></span>
                <span className={styles.menuIcon}></span>
                <span className={styles.menuIcon}></span>
            </button>
        </nav>
    );
};

export default Navbar;