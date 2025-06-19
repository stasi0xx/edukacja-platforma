/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./src/**/*.{js,ts,jsx,tsx}"],
    theme: {
        extend: {
            colors: {
                primary: '#ff0055',
                dark: '#1a1a1a',
                light: '#ffffff',
                muted: '#999999',
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                display: ['"Playfair Display"', "serif"],
            },
        },
    },
    plugins: [],
};
