import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxies /api to your FastAPI backend during dev so you avoid CORS entirely.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
