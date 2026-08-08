import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import ChatPage from "./pages/ChatPage.jsx";
import VectorDbPage from "./pages/VectorDbPage.jsx";

export default function App() {
  return (
    <div className="app-root">
      <Navbar />
      <div className="app-body">
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/vector-db" element={<VectorDbPage />} />
        </Routes>
      </div>
    </div>
  );
}
