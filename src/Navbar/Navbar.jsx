// Navbar.jsx
import React, { useState, useEffect, useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import styles from "./Navbar.module.css";
import logoImage from "../assets/logo.png";
import { Menu, X, ChevronDown, User, LogIn, LogOut, MessageCircle } from "lucide-react";
import { AuthContext } from "../AuthContext";

const Navbar = ({ onAssistantClick }) => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isScrolled, setIsScrolled] = useState(false);
    const [activeLink, setActiveLink] = useState('accueil');
    const { user, logout } = useContext(AuthContext);
    const navigate = useNavigate();

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

    const handleLogout = () => {
        logout();
        navigate('/login');
        setIsMenuOpen(false);
    };

    return (
        <nav className={`${styles.navbar} ${isScrolled ? styles.scrolled : ''}`}>
            <div className={styles.logoContainer} onClick={() => navigate('/')}>
                <img
                    src={logoImage}
                    alt="Logo de l'application"
                    className={styles.logo}
                />
                <span className={styles.logoText}>TravelMate</span>
            </div>

            <ul className={`${styles.links} ${isMenuOpen ? styles.open : ''}`}>
                <li>
                    <Link
                        className={activeLink === 'accueil' ? styles.active : ''}
                        to="/home"
                        onClick={() => setActiveLink('accueil')}
                    >
                        Accueil
                    </Link>
                </li>
                <li>
                    <Link
                        to="/home/destinations"
                        className={activeLink === 'destinations' ? styles.active : ''}
                        onClick={() => setActiveLink('destinations')}
                    >
                        Destinations
                    </Link>
                </li>
                <li>
                    <Link
                        to="/home/vols"
                        className={activeLink === 'vols' ? styles.active : ''}
                        onClick={() => setActiveLink('vols')}
                    >
                        Vols
                    </Link>
                </li>
                <li>
                    <Link
                        to="#footer"
                        className={activeLink === 'contact' ? styles.active : ''}
                    >
                        Contact
                    </Link>
                </li>
                <li>
                    <Link
                        to="/home/chatbot"
                        className={activeLink === 'assistant' ? styles.active : ''}
                        onClick={() => setActiveLink('assistant')}

                    >
                        <MessageCircle size={16} style={{ marginRight: '6px' }} />
                        Assistant
                    </Link>
                </li>
            </ul>

            <div className={styles.buttons}>
                {user ? (
                    <>
                        <div className={styles.userInfo}>
                            <User size={16} style={{ marginRight: '6px' }} />
                            <span>{user.name}</span>
                        </div>
                        <button 
                            className={styles.signInButton} 
                            onClick={handleLogout}
                        >
                            <LogOut size={16} style={{ marginRight: '4px' }} />
                            Déconnexion
                        </button>
                    </>
                ) : (
                    <>
                        <button 
                            className={styles.signInButton}
                            onClick={() => {
                                navigate('/login');
                                setIsMenuOpen(false);
                            }}
                        >
                            <LogIn size={16} style={{ marginRight: '4px' }} />
                            Connexion
                        </button>
                        <button 
                            className={styles.signUpButton}
                            onClick={() => {
                                navigate('/login?tab=register');
                                setIsMenuOpen(false);
                            }}
                        >
                            Inscription
                        </button>
                    </>
                )}
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