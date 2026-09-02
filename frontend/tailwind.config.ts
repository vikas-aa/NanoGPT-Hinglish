import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        brand: {
          50:  "#f0f4ff",
          100: "#dce8ff",
          200: "#bdd3ff",
          300: "#90b2ff",
          400: "#5d87ff",
          500: "#3360ff",
          600: "#1a3ef5",
          700: "#132ce0",
          800: "#1526b5",
          900: "#172590",
        },
      },
      animation: {
        "dot-bounce": "dotBounce 1.4s infinite ease-in-out both",
        "fade-in": "fadeIn 0.2s ease-out",
        "slide-in": "slideIn 0.25s ease-out",
      },
      keyframes: {
        dotBounce: {
          "0%, 80%, 100%": { transform: "scale(0)", opacity: "0.3" },
          "40%":           { transform: "scale(1.0)", opacity: "1" },
        },
        fadeIn: {
          from: { opacity: "0", transform: "translateY(6px)" },
          to:   { opacity: "1", transform: "translateY(0)" },
        },
        slideIn: {
          from: { transform: "translateX(-100%)" },
          to:   { transform: "translateX(0)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
