import { ref } from "vue";

const theme = ref<"dark" | "light" | "wellness">("dark");

export function useTheme() {
  function setTheme(next: "dark" | "light" | "wellness") {
    theme.value = next;
    document.documentElement.setAttribute("data-theme", next);
  }

  return {
    theme,
    setTheme
  };
}
