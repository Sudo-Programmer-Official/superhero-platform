import { createRouter, createWebHistory } from "vue-router";
import AppLayout from "../layouts/AppLayout.vue";
import AuthLayout from "../layouts/AuthLayout.vue";
import BookingsView from "../views/BookingsView.vue";
import DealsView from "../views/DealsView.vue";
import CreateDealView from "../views/CreateDealView.vue";
import HomeView from "../views/HomeView.vue";
import LandingView from "../views/LandingView.vue";
import OnboardingView from "../views/OnboardingView.vue";
import ProfileView from "../views/ProfileView.vue";
import RedemptionsView from "../views/RedemptionsView.vue";
import WalletPassesView from "../views/WalletPassesView.vue";
import PublicProfileView from "../views/PublicProfileView.vue";
import PublicDealView from "../views/PublicDealView.vue";
import SigninView from "../views/SigninView.vue";
import SignupView from "../views/SignupView.vue";
import { initSessionWatcher, sessionState } from "../stores/session";
import { evaluateRouteGuard } from "./guard";

initSessionWatcher();

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "landing",
      component: LandingView
    },
    {
      path: "/",
      component: AuthLayout,
      children: [
        { path: "signin", name: "signin", component: SigninView },
        { path: "signup", name: "signup", component: SignupView },
        { path: "onboarding", name: "onboarding", component: OnboardingView, meta: { requiresAuth: true } }
      ]
    },
    {
      path: "/openmat/:practitionerSlug",
      name: "public-profile",
      component: PublicProfileView
    },
    {
      path: "/openmat/:practitionerSlug/:dealSlug",
      name: "public-deal",
      component: PublicDealView
    },
    {
      path: "/",
      component: AppLayout,
      children: [
        { path: "dashboard", name: "dashboard", component: HomeView, meta: { requiresAuth: true } },
        { path: "dashboard/deals", name: "deals", component: DealsView, meta: { requiresAuth: true } },
        { path: "dashboard/bookings", name: "bookings", component: BookingsView, meta: { requiresAuth: true } },
        { path: "dashboard/deals/create", name: "deals-create", component: CreateDealView, meta: { requiresAuth: true } },
        { path: "dashboard/wallet-passes", name: "wallet-passes", component: WalletPassesView, meta: { requiresAuth: true } },
        { path: "dashboard/redemptions", name: "redemptions", component: RedemptionsView, meta: { requiresAuth: true } },
        {
          path: "dashboard/profile",
          name: "profile",
          component: ProfileView,
          meta: { requiresAuth: true, roles: ["practitioner", "admin", "super_admin"] }
        }
      ]
    }
  ]
});

router.beforeEach((to) => evaluateRouteGuard(to, sessionState));

export default router;
