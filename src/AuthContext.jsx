// src/AuthContext.jsx
import { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [users, setUsers] = useState(() => {
    // Initialize with some default users or empty array
    const storedUsers = localStorage.getItem('travelmate_users');
    return storedUsers ? JSON.parse(storedUsers) : [
      { id: 1, email: 'user@example.com', password: 'password', name: 'Test User' }
    ];
  });

  useEffect(() => {
    // Check session on initial load
    const storedUser = localStorage.getItem('travelmate_user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setIsLoading(false);
  }, []);

  useEffect(() => {
    // Save users to localStorage whenever it changes
    localStorage.setItem('travelmate_users', JSON.stringify(users));
  }, [users]);

  const login = (email, password) => {
    const foundUser = users.find(u => u.email === email && u.password === password);
    if (foundUser) {
      setUser(foundUser);
      localStorage.setItem('travelmate_user', JSON.stringify(foundUser));
      return true;
    }
    return false;
  };

  const register = (name, email, password) => {
    // Check if user already exists
    if (users.some(u => u.email === email)) {
      return false;
    }

    const newUser = {
      id: users.length + 1,
      name,
      email,
      password
    };
    
    setUsers(prev => [...prev, newUser]);
    setUser(newUser);
    localStorage.setItem('travelmate_user', JSON.stringify(newUser));
    return true;
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('travelmate_user');
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};