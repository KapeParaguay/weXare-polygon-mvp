import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f1f8ff",
          500: "#2563eb",
          700: "#1e40af"
        }
      }
    }
  },
  plugins: []
};

export default config;
