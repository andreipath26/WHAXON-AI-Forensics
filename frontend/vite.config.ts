import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/static/obsidian/",
  build: {
    outDir: "../src/whaxon/interfaces/web/static/obsidian",
    emptyOutDir: true,
    assetsDir: "assets",
    sourcemap: false,
    manifest: true,
  },
  test: {
    environment: "jsdom",
  },
});
