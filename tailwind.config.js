/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["\"Space Grotesk\"", "system-ui", "sans-serif"],
        mono: ["\"IBM Plex Mono\"", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      colors: {
        ink: "#0c0f16",
        mist: "#f3f2ef",
        ember: "#f1684e",
        tide: "#2d6cdf",
        field: "#d9e5cf",
      },
      boxShadow: {
        glow: "0 12px 40px rgba(45, 108, 223, 0.25)",
      },
      keyframes: {
        floaty: {
          "0%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-8px)" },
          "100%": { transform: "translateY(0px)" },
        },
        pulseSoft: {
          "0%": { opacity: "0.4" },
          "50%": { opacity: "0.8" },
          "100%": { opacity: "0.4" },
        },
      },
      animation: {
        floaty: "floaty 6s ease-in-out infinite",
        pulseSoft: "pulseSoft 4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
