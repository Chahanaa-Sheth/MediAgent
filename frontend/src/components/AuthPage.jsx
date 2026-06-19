import { useState } from "react";
import { APIService } from "../services/api";
import "./AuthPage.css";

export default function AuthPage({ auth }) {
  const [isLogin, setIsLogin] = useState(true);

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError("");

      if (isLogin) {
        const result = await APIService.login(
          username,
          password
        );

        auth.setToken(
          result.access_token
        );

        auth.setUsername(
          username
        );
      } else {
        await APIService.signup(
          username,
          password
        );

        alert(
          "Account created successfully. Please login."
        );

        setIsLogin(true);
      }
    } catch (err) {
      setError(
        err.message || "Authentication failed"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      {/* LEFT PANEL */}
      <div className="auth-left">
        <div className="logo">
          <span className="logo-icon">✚</span>
          <span>MediAgent</span>
        </div>

        <div className="badge">
          AI-POWERED • MEDICAL RESEARCH
        </div>

        <h1>
          Your medical
          <br />
          co-pilot,
          <br />
          always on call.
        </h1>

        <p>
          PubMed-powered medical research,
          symptom analysis, PDF intelligence,
          and clinical reasoning.
        </p>

        <div className="feature-card">
          📝 AI Medical Analysis
        </div>

        <div className="feature-card">
          🔬 PubMed Research Search
        </div>

        <div className="feature-card">
          📄 PDF Knowledge Base
        </div>
      </div>

      {/* RIGHT PANEL */}
      <div className="auth-right">

        <div className="tabs">
          <button
            className={!isLogin ? "active" : ""}
            onClick={() =>
              setIsLogin(false)
            }
          >
            Create account
          </button>

          <button
            className={isLogin ? "active" : ""}
            onClick={() =>
              setIsLogin(true)
            }
          >
            Sign in
          </button>
        </div>

        <h2>
          {isLogin
            ? "Welcome Back"
            : "Get Started"}
        </h2>

        <p className="subtitle">
          {isLogin
            ? "Login to continue using MediAgent."
            : "Create your MediAgent account."}
        </p>

        {error && (
          <div className="error-box">
            {error}
          </div>
        )}

        <label>Username</label>

        <input
          type="text"
          placeholder="Enter username"
          value={username}
          onChange={(e) =>
            setUsername(
              e.target.value
            )
          }
        />

        <label>Password</label>

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) =>
            setPassword(
              e.target.value
            )
          }
        />

        <button
          className="submit-btn"
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading
            ? "Please wait..."
            : isLogin
            ? "Sign In"
            : "Create Account"}
        </button>

        <p className="bottom-text">
          {isLogin
            ? "Need an account?"
            : "Already have an account?"}

          <span
            onClick={() =>
              setIsLogin(!isLogin)
            }
          >
            {isLogin
              ? " Create one"
              : " Sign in"}
          </span>
        </p>
      </div>
    </div>
  );
}