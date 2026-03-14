/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./src/**/*.{ts,tsx}"],
    presets: [require("nativewind/preset")],
    theme: {
        extend: {
            fontFamily:
                {
                    sans: ["inter"],
                    bold: ["inter-bold"],
                    italic: ["inter-italic"],
                    boldItalic: ["inter-bold-italic"],


                },
            colors: {
                primary: "var(--color-primary)",
                "on-primary": "var(--color-on-primary)",
                "primary-container": "var(--color-primary-container)",
                "on-primary-container": "var(--color-on-primary-container)",
                secondary: "var(--color-secondary)",
                "on-secondary": "var(--color-on-secondary)",
                surface: "var(--color-surface)",
                "on-surface": "var(--color-on-surface)",
            },
            textColor :{
                "on-primary": "var(--color-on-primary)",
                "on-primary-container": "var(--color-on-primary-container)",
                "on-secondary": "var(--color-on-secondary)",
                "on-surface": "var(--color-on-surface)",
                "on-surface-variant": "var(--color-on-surface-variant)",
            },
            borderColor: {
                primary: "var(--color-primary)",
                "on-primary": "var(--color-on-primary)",
                "primary-container": "var(--color-primary-container)",
                "on-primary-container": "var(--color-on-primary-container)",
                secondary: "var(--color-secondary)",
                "on-secondary": "var(--color-on-secondary)",
                surface: "var(--color-surface)",
                "on-surface": "var(--color-on-surface)",
                "on-surface-variant": "var(--color-on-surface-variant)",
            }
        },

    },
    plugins: [],
}

