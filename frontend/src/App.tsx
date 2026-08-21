import { BrowserRouter, Routes, Route, Link, Navigate, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "./hooks/useAuth";
import Login from "./pages/Login";
import Chat from "./pages/Chat";
import Approvals from "./pages/Approvals";
import Documents from "./pages/Documents";
import Evaluations from "./pages/Evaluations";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { token, loading } = useAuth();
  if (loading) return <div className="loading">Loading...</div>;
  if (!token) return <Navigate to="/login" />;
  return <>{children}</>;
}

function Navbar() {
  const { user, logout } = useAuth();
  const location = useLocation();

  if (!user) return null;

  const links = [
    { to: "/chat", label: "Chat" },
    { to: "/approvals", label: "Approvals" },
    { to: "/documents", label: "Documents" },
    { to: "/evaluations", label: "Evaluations" },
  ];

  return (
    <nav className="navbar">
      <div className="nav-brand">AI Customer Ops</div>
      <div className="nav-links">
        {links.map((l) => (
          <Link
            key={l.to}
            to={l.to}
            className={location.pathname === l.to ? "active" : ""}
          >
            {l.label}
          </Link>
        ))}
      </div>
      <div className="nav-user">
        <span>{user.email}</span>
        <span className="nav-role">{user.role}</span>
        <button className="btn btn-sm" onClick={logout}>
          Logout
        </button>
      </div>
    </nav>
  );
}

function AppRoutes() {
  const { token } = useAuth();

  return (
    <>
      <Navbar />
      <Routes>
        <Route
          path="/login"
          element={token ? <Navigate to="/chat" /> : <Login />}
        />
        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <Chat />
            </ProtectedRoute>
          }
        />
        <Route
          path="/approvals"
          element={
            <ProtectedRoute>
              <Approvals />
            </ProtectedRoute>
          }
        />
        <Route
          path="/documents"
          element={
            <ProtectedRoute>
              <Documents />
            </ProtectedRoute>
          }
        />
        <Route
          path="/evaluations"
          element={
            <ProtectedRoute>
              <Evaluations />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/chat" />} />
      </Routes>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
