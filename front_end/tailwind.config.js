/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './app/**/*.{js,jsx,ts,tsx}',
        './components/**/*.{js,jsx,ts,tsx}',
    ],
    theme: {
        extend: {
            colors: {
                primary: '#1B4F72',
                secondary: '#1A7F5E',
                critical: '#C0392B',
                high: '#E74C3C',
                moderate: '#F39C12',
                low: '#27AE60',
            },
        },
    },
    plugins: [],
};
