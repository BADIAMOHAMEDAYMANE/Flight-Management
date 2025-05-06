import React, { useState, useRef, useEffect } from 'react';
import styles from './Chatbot.module.css';

const Chatbot = ({ onClose, onDestinationSelect }) => {
    const [message, setMessage] = useState('');
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const sessionId = useRef(Date.now().toString()).current; // Persistent session ID
    const chatWindowRef = useRef(null);

    // Auto-scroll to bottom when messages change
    useEffect(() => {
        if (chatWindowRef.current) {
            chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSendMessage = async () => {
        if (!message.trim() || isLoading) return;

        // Check for "I choose [destination]" pattern
        const choosePattern = /^I\s+choose\s+(.+)$/i;
        const match = message.match(choosePattern);

        // Add user message to UI immediately
        setMessages(prev => [...prev, { text: message, sender: 'user' }]);
        setMessage('');
        
        // If it's a destination selection message
        if (match) {
            const destination = match[1].trim();
            
            // Add bot response confirming the destination selection
            setMessages(prev => [...prev, { 
                text: `Taking you to ${destination} details page...`, 
                sender: 'bot',
                isRedirect: true
            }]);
            
            // Slight delay before redirect to show the confirmation message
            setTimeout(() => {
                onDestinationSelect(destination);
            }, 1500);
            
            return;
        }
        
        // Regular message handling
        setIsLoading(true);

        try {
            const response = await fetch('http://localhost:5000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    message, 
                    sessionId 
                }),
            });

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            setMessages(prev => [...prev, { text: data.response, sender: 'bot' }]);
        } catch (error) {
            console.error('Chat error:', error);
            setMessages(prev => [...prev, { 
                text: 'Sorry, there was an error. Please try again.', 
                sender: 'bot' 
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={styles.chatbotContainer}>
            <div className={styles.chatHeader}>
                <h2>Travel Assistant</h2>
                <button onClick={onClose} className={styles.closeButton}>
                    &times;
                </button>
            </div>
            
            <div className={styles.chatWindow} ref={chatWindowRef}>
                {messages.length === 0 ? (
                    <div className={styles.welcomeMessage}>
                        <p>Hello! I'm your travel assistant. Ask me about destinations, flights, or travel tips!</p>
                        <p>To see detailed information about a destination, type <strong>"I choose [City or Country]"</strong></p>
                    </div>
                ) : (
                    messages.map((msg, index) => (
                        <div 
                            key={index} 
                            className={`${msg.sender === 'user' ? styles.userMessage : styles.botMessage} ${msg.isRedirect ? styles.redirectMessage : ''}`}
                        >
                            {msg.text}
                        </div>
                    ))
                )}
                {isLoading && (
                    <div className={styles.botMessage}>
                        <div className={styles.typingIndicator}>
                            <span>•</span><span>•</span><span>•</span>
                        </div>
                    </div>
                )}
            </div>
            
            <div className={styles.inputArea}>
                <input 
                    type="text" 
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Ask me about travel destinations..." 
                    disabled={isLoading}
                />
                <button 
                    onClick={handleSendMessage}
                    disabled={isLoading || !message.trim()}
                >
                    {isLoading ? 'Sending...' : 'Send'}
                </button>
            </div>
        </div>
    );
};

export default Chatbot;