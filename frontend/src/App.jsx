import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import { AuthProvider } from "./context/AuthContext";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Recommendations from "./pages/Recommendations";
import MovieDetails from "./pages/MovieDetails";

function ProtectedRoute({ children }) {
  const token = localStorage.getItem("token");

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>

        <Routes>

          <Route
            path="/"
            element={<Home />}
          />

          <Route
            path="/login"
            element={<Login />}
          />

          <Route
            path="/register"
            element={<Register />}
          />

          <Route
            path="/recommendations"
            element={
              <ProtectedRoute>
                <Recommendations />
              </ProtectedRoute>
            }
          />

          <Route
            path="/movie/:movieId"
            element={<MovieDetails />}
          />

          <Route
            path="*"
            element={
              <Navigate
                to="/"
                replace
              />
            }
          />

        </Routes>

      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;