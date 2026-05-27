import React from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App.js";
import "./styles.css";

const root = document.getElementById("root");

if (!root) {
  throw new Error("Widget root element was not found.");
}

createRoot(root).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
