import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  "#eef7ff",
          100: "#d9edff",
          200: "#bcdfff",
          300: "#8ecaff",
          400: "#59acff",
          500: "#348bff",
          600: "#1d6cf5",
          700: "#1856d8",
          800: "#1a48ae",
          900: "#1c4089",
        },
      },
    },
  },
  plugins: [],
};
export default config;
