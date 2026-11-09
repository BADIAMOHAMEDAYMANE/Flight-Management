import React, { useState, useRef, useEffect } from 'react';
import styles from './Chatbot.module.css';
import ReactMarkdown from 'react-markdown';

const Chatbot = ({ onClose, onDestinationSelect }) => {
    const [message, setMessage] = useState('');
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [userPreferences, setUserPreferences] = useState({});
    const [suggestedButtons, setSuggestedButtons] = useState([]);
    const [showBudgetCalculator, setShowBudgetCalculator] = useState(false);
    const [budgetParams, setBudgetParams] = useState({
        destination: '',
        budgetLevel: 'mid-range',
        duration: 7,
        travelers: 1
    });
    
    const sessionId = useRef(Date.now().toString()).current; // Persistent session ID
    const chatWindowRef = useRef(null);

    // Auto-scroll to bottom when messages change
    useEffect(() => {
        if (chatWindowRef.current) {
            chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSendMessage = async (text = message) => {
        if ((!text.trim() && !message.trim()) || isLoading) return;
        
        const messageToSend = text.trim() ? text : message.trim();

        // Check for "I choose [destination]" pattern
        const choosePattern = /^I\s+choose\s+(.+)$/i;
        const match = messageToSend.match(choosePattern);

        // Add user message to UI immediately
        setMessages(prev => [...prev, { text: messageToSend, sender: 'user' }]);
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
        
        // Check for budget calculation request
        const budgetPattern = /^budget\s+for\s+(.+)$/i;
        const budgetMatch = messageToSend.match(budgetPattern);
        
        if (budgetMatch) {
            const destination = budgetMatch[1].trim();
            setBudgetParams(prev => ({...prev, destination: destination}));
            setShowBudgetCalculator(true);
            return;
        }
        
        // Regular message handling
        setIsLoading(true);

        try {
            const response = await fetch('http://localhost:5000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    message: messageToSend, 
                    sessionId 
                }),
            });

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            // Update user preferences if provided
            if (data.userPreferences) {
                setUserPreferences(data.userPreferences);
            }

            // Process destination cards and suggestion buttons if available
            let processedResponse = data.response;
            let destinationCards = [];
            let suggestionButtons = [];
            
            if (data.processed_response) {
                processedResponse = data.processed_response.text;
                destinationCards = data.processed_response.destinationCards || [];
                suggestionButtons = data.processed_response.suggestionButtons || [];
                
                // Update suggestion buttons
                setSuggestedButtons(suggestionButtons);
            }
            
            setMessages(prev => [...prev, { 
                text: processedResponse, 
                sender: 'bot',
                destinationCards: destinationCards
            }]);
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

    const handleSuggestionClick = (suggestion) => {
        setMessage(suggestion);
        handleSendMessage(suggestion);
    };

    const handleBudgetCalculation = async () => {
        setIsLoading(true);
        setShowBudgetCalculator(false);
        
        try {
            const response = await fetch('http://localhost:5000/api/budget-calculator', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ...budgetParams,
                    sessionId
                }),
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Format budget information for display
            const formattedBudget = formatBudgetResponse(data);
            
            setMessages(prev => [...prev, {
                text: formattedBudget,
                sender: 'bot',
                isBudget: true
            }]);
            
        } catch (error) {
            console.error('Budget calculation error:', error);
            setMessages(prev => [...prev, {
                text: 'Sorry, there was an error calculating the budget. Please try again.',
                sender: 'bot'
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const formatBudgetResponse = (budgetData) => {
        const { destination, duration, travelers, budgetLevel, dailyCost, accommodation, food, activities, transportation, flights, totalCost } = budgetData;
        
        return `## Travel Budget for ${destination}
        
**Trip Details:**
- Duration: ${duration} days
- Travelers: ${travelers}
- Budget Level: ${budgetLevel.charAt(0).toUpperCase() + budgetLevel.slice(1)}

**Daily Expenses:**
- Accommodation: $${accommodation.min}-$${accommodation.max} per day
- Food: $${food.min}-$${food.max} per day
- Activities: $${activities.min}-$${activities.max} per day
- Local Transportation: $${transportation.min}-$${transportation.max} per day

**Flights:**
- Estimated cost: $${flights.min}-$${flights.max} total for ${travelers} traveler(s)

**Total Trip Estimate:**
- Daily expenses: $${dailyCost.min}-$${dailyCost.max}
- Total trip cost: $${totalCost.min}-$${totalCost.max} including flights

*This is an estimate and actual costs may vary.*`;
    };

    // Function to render message content with markdown support
    const renderMessageContent = (text) => {
        return (
            <ReactMarkdown
                components={{
                    h2: ({node, ...props}) => <h2 className={styles.messageHeading} {...props} />,
                    strong: ({node, ...props}) => <strong className={styles.messageHighlight} {...props} />,
                    li: ({node, ...props}) => <li className={styles.messageListItem} {...props} />,
                    ul: ({node, ...props}) => <ul className={styles.messageList} {...props} />,
                    ol: ({node, ...props}) => <ol className={styles.messageOrderedList} {...props} />
                }}
            >
                {text}
            </ReactMarkdown>
        );
    };

    // Function to render destination cards
    const renderDestinationCards = (destinations) => {
        if (!destinations || destinations.length === 0) return null;
        
        return (
            <div className={styles.destinationCardsContainer}>
                {destinations.map((destination, index) => (
                    <div 
                        key={index} 
                        className={styles.destinationCard}
                        onClick={() => handleSuggestionClick(`I choose ${destination}`)}
                    >
                        <div className={styles.destinationCardImage}>
                            {/* Placeholder image - in a real app you'd use actual destination images */}
                            <div className={styles.destinationImagePlaceholder}></div>
                        </div>
                        <div className={styles.destinationCardContent}>
                            <h3>{destination}</h3>
                            <button className={styles.viewDetailsBtn}>View Details</button>
                        </div>
                    </div>
                ))}
            </div>
        );
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
                        <div className={styles.quickSuggestionsContainer}>
                            <button 
                                className={styles.suggestionButton}
                                onClick={() => handleSuggestionClick("Recommend beach destinations")}
                            >
                                Beach Vacations
                            </button>
                            <button 
                                className={styles.suggestionButton}
                                onClick={() => handleSuggestionClick("Popular city breaks")}
                            >
                                City Breaks
                            </button>
                            <button 
                                className={styles.suggestionButton}
                                onClick={() => handleSuggestionClick("Budget travel ideas")}
                            >
                                Budget Travel
                            </button>
                        </div>
                    </div>
                ) : (
                    messages.map((msg, index) => (
                        <div 
                            key={index} 
                            className={`${msg.sender === 'user' ? styles.userMessage : styles.botMessage} ${msg.isRedirect ? styles.redirectMessage : ''}`}
                        >
                            {msg.sender === 'bot' ? (
                                <>
                                    {renderMessageContent(msg.text)}
                                    {msg.destinationCards && renderDestinationCards(msg.destinationCards)}
                                </>
                            ) : msg.text}
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
                
                {/* Suggestion buttons */}
                {suggestedButtons.length > 0 && !isLoading && (
                    <div className={styles.suggestionButtonsContainer}>
                        {suggestedButtons.map((suggestion, index) => (
                            <button
                                key={index}
                                className={styles.suggestionButton}
                                onClick={() => handleSuggestionClick(suggestion)}
                            >
                                {suggestion}
                            </button>
                        ))}
                    </div>
                )}
            </div>
            
            {/* Budget Calculator */}
            {showBudgetCalculator && (
                <div className={styles.budgetCalculator}>
                    <h3>Travel Budget Calculator for {budgetParams.destination}</h3>
                    <div className={styles.budgetForm}>
                        <div className={styles.formGroup}>
                            <label>Budget Level:</label>
                            <select 
                                value={budgetParams.budgetLevel}
                                onChange={(e) => setBudgetParams({...budgetParams, budgetLevel: e.target.value})}
                            >
                                <option value="budget">Budget</option>
                                <option value="mid-range">Mid-range</option>
                                <option value="luxury">Luxury</option>
                            </select>
                        </div>
                        <div className={styles.formGroup}>
                            <label>Duration (days):</label>
                            <input 
                                type="number" 
                                min="1" 
                                max="30"
                                value={budgetParams.duration}
                                onChange={(e) => setBudgetParams({...budgetParams, duration: parseInt(e.target.value)})}
                            />
                        </div>
                        <div className={styles.formGroup}>
                            <label>Travelers:</label>
                            <input 
                                type="number" 
                                min="1" 
                                max="10"
                                value={budgetParams.travelers}
                                onChange={(e) => setBudgetParams({...budgetParams, travelers: parseInt(e.target.value)})}
                            />
                        </div>
                        <div className={styles.budgetButtons}>
                            <button onClick={handleBudgetCalculation} className={styles.calculateBtn}>Calculate</button>
                            <button onClick={() => setShowBudgetCalculator(false)} className={styles.cancelBtn}>Cancel</button>
                        </div>
                    </div>
                </div>
            )}
            
            <div className={styles.inputArea}>
                <input 
                    type="text" 
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Ask me about travel destinations..." 
                    disabled={isLoading || showBudgetCalculator}
                />
                <button 
                    onClick={() => handleSendMessage()}
                    disabled={isLoading || !message.trim() || showBudgetCalculator}
                >
                    {isLoading ? 'Sending...' : 'Send'}
                </button>
            </div>
        </div>
    );
};

export default Chatbot;