/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],

  theme: {
    extend: {
      /* 🎨 Paleta de marca PC FUTSAL */
      colors: {
        brand: {
          bg: "#000000",       // fondo global (negro)
          card: "#121212",     // fondo de tarjetas / módulos
          accent: "#A51B3D",   // rojo principal PC FUTSAL
          navy: "#0B1C2E",     // azul oscuro complementario
          text: "#FFFFFF",     // texto principal
          textSecondary: "#B3B3B3", // texto secundario
          success: "#00C46A",  // verde de éxito
          warning: "#FFD43B",  // amarillo de aviso
          error: "#7A0F2A",    // rojo oscuro (tarjetas rojas)
        },
      },

      /* 🧩 Tipografías de marca */
      fontFamily: {
        base: ['Cabin', 'sans-serif'],
        title: ['Orbitron', 'sans-serif'],
      },
    },
  },

  plugins: [],
};
