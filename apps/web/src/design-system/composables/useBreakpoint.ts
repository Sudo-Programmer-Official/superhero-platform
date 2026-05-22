import { computed, ref } from "vue";

const width = ref(typeof window !== "undefined" ? window.innerWidth : 0);

if (typeof window !== "undefined") {
  window.addEventListener("resize", () => {
    width.value = window.innerWidth;
  });
}

export function useBreakpoint() {
  const isMobile = computed(() => width.value < 768);
  const isTablet = computed(() => width.value >= 768 && width.value < 1024);
  const isDesktop = computed(() => width.value >= 1024);

  return { width, isMobile, isTablet, isDesktop };
}
