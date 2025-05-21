import App from "../App"
import Body from "../Body/Body";
import Chatbot from "../Chatbot/Chatbot"
import LoginPage from "../Login/LoginPage";
import Main from "../Main/Main";
import FlightDestinations from "../TravelPlan/TravelPlan"
import { Route, Routes } from "react-router";


const AppRoutes = () => {
    return (
        <Routes>
            <Route path="login" element={<LoginPage />} />
            <Route path="home" element={<App/>}>
             <Route path="" element={<Main/>}/>
             <Route path="destinations" element={<FlightDestinations/>}/>
             <Route path="vols" element={<Body/>}/>
             <Route path="chatbot" element={<Chatbot />}/>
            </Route>
        </Routes>
    )
}

export default AppRoutes;