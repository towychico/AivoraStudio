import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

import "./index.css";
import "@siberui/react/globals.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
      <div className="dark min-h-screen bg-[#050810] text-slate-100">
          <App />
      </div>
  </React.StrictMode>,
);
