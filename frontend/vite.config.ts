import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

// Vite config for React + TypeScript frontend.
// Dev server runs on http://localhost:5173 by default.
// All /api requests are proxied to the backend at http://localhost:3001.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:3001",
        changeOrigin: true
      }
    }
  }
});
