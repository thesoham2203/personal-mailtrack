import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8000",
      "/t": "http://localhost:8000",
      "/d": "http://localhost:8000",
      "/u": "http://localhost:8000",
    },
  },
});
