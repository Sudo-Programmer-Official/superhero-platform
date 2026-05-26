import type { RouteRecordRaw } from "vue-router";
import AuthLayout from "../layouts/AuthLayout.vue";
import OnboardingView from "../views/OnboardingView.vue";
import SigninView from "../views/SigninView.vue";
import SignupView from "../views/SignupView.vue";

export const authRoutes: RouteRecordRaw[] = [
  { path: "/sign-in", redirect: (to) => ({ path: "/signin", query: to.query }) },
  { path: "/sign-up", redirect: (to) => ({ path: "/signup", query: to.query }) },
  {
    path: "/",
    component: AuthLayout,
    children: [
      { path: "signin", name: "signin", component: SigninView },
      { path: "signup", name: "signup", component: SignupView },
      { path: "onboarding", name: "onboarding", component: OnboardingView, meta: { requiresAuth: true } }
    ]
  }
];
