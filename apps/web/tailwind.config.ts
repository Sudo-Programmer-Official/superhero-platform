import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{vue,ts}"],
  theme: {
    extend: {
      colors: {
        surface: {
          0: "var(--surface-0)",
          1: "var(--surface-1)",
          2: "var(--surface-2)"
        },
        text: {
          0: "var(--text-0)",
          1: "var(--text-1)"
        },
        accent: "var(--accent)"
      },
      borderRadius: {
        card: "var(--radius-card)",
        panel: "var(--radius-panel)"
      },
      spacing: {
        xs: "var(--space-xs)",
        sm: "var(--space-sm)",
        md: "var(--space-md)",
        lg: "var(--space-lg)",
        xl: "var(--space-xl)"
      }
    }
  },
  plugins: []
} satisfies Config;
