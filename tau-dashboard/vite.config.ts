import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "node:path";

let http_host = "http://localhost:3000";
let ws_host = "ws://localhost:3000";

// https://vite.dev/config/
export default defineConfig({
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: http_host,
        changeOrigin: true,
        secure: false,
      },
      "/swagger-ui": {
        target: http_host,
        changeOrigin: true,
        secure: false,
      },
      "/ws/": {
        target: ws_host,
        changeOrigin: true,
        ws: true,
        secure: false,
      },
    },
  },
});
