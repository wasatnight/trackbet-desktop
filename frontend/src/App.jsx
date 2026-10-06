import { BrowserRouter, NavLink, Route, Routes } from "react-router";

import Analiticas from "./pages/Analiticas";
import Dashboard from "./pages/Dashboard";
import Historial from "./pages/Historial";
import RegistrarApuesta from "./pages/RegistrarApuesta";

function App() {
  return (
    <BrowserRouter>
      <nav className="navegacion-principal">
        <NavLink to="/">Dashboard</NavLink>

        <NavLink to="/registrar">Registrar apuesta</NavLink>

        <NavLink to="/historial">Historial</NavLink>

        <NavLink to="/analiticas">Analíticas</NavLink>
      </nav>

      <Routes>
        <Route path="/" element={<Dashboard />} />

        <Route path="/historial" element={<Historial />} />

        <Route path="/registrar" element={<RegistrarApuesta />} />

        <Route path="/analiticas" element={<Analiticas />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
