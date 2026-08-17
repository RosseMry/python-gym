import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxies /api requests to the FastAPI backend during local development
// so the frontend can just call fetch("/api/...") without hardcoding a
// host/port or fighting CORS.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
