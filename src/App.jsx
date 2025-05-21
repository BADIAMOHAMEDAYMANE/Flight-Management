import { Navigate, Outlet, useLocation } from "react-router-dom";
import Navbar from "./Navbar/Navbar";
import Footer from "./Footer/Footer";
import "./App.module.css";
import { useContext, useEffect } from "react";
import { AuthContext } from "./AuthContext";

function App() {

  const location = useLocation();

  const { user, isLoading } = useContext(AuthContext);

  useEffect(() => {
    if (location.hash === "#footer") {
      const footer = document.getElementById("footer");
      if (footer) {
        footer.scrollIntoView({ behavior: "smooth" });
      }
    }
  }, [location]);

  if(isLoading) {
    return <p>Loading ...</p>
  }
  else if(!user) {
    return <Navigate to="/login" replace />;
  }
  return (
    <div className="app">
      <Navbar />
      <Outlet />
      <footer id="footer">
        <Footer />
      </footer>
    </div>
  );
}

export default App;
