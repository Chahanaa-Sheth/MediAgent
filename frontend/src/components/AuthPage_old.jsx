import { useState } from "react";
import { APIService } from "../services/api";

export default function AuthPage({ auth }) {

  const [isLogin, setIsLogin] = useState(true);

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {

    console.log("USERNAME:", username);
    console.log("PASSWORD:", password);

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
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center"
      }}
    >
      <div
        style={{
          width: 400,
          padding: 30,
          border: "1px solid #ddd",
          borderRadius: 12
        }}
      >
        <h1>MediAgent</h1>

        <h3>
          {isLogin ? "Login" : "Sign Up"}
        </h3>

        <input
          placeholder="Username"
          value={username}
          onChange={(e) =>
            setUsername(e.target.value)
          }
          style={{
            width: "100%",
            marginBottom: 10,
            padding: 10
          }}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) =>
            setPassword(e.target.value)
          }
          style={{
            width: "100%",
            marginBottom: 10,
            padding: 10
          }}
        />

        {error && (
          <p style={{ color: "red" }}>
            {error}
          </p>
        )}

        <button
          onClick={handleSubmit}
          disabled={loading}
          style={{
            width: "100%",
            padding: 10
          }}
        >
          {loading
            ? "Loading..."
            : isLogin
            ? "Login"
            : "Create Account"}
        </button>

        <br />
        <br />

        <button
          onClick={() =>
            setIsLogin(!isLogin)
          }
          style={{
            width: "100%",
            padding: 10
          }}
        >
          {isLogin
            ? "Need an account?"
            : "Already have an account?"}
        </button>
      </div>
    </div>
  );
}