import { createRouter, createWebHistory } from "vue-router";
import AppLayout from "../layouts/AppLayout.vue";
import AuthLayout from "../layouts/AuthLayout.vue";
import AuthView from "../views/AuthView.vue";
import DealsView from "../views/DealsView.vue";
import HomeView from "../views/HomeView.vue";
import ProfileView from "../views/ProfileView.vue";
import { initSessionWatcher, sessionState } from "../stores/session";
import { evaluateRouteGuard } from "./guard";

initSessionWatcher();

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      component: AppLayout,
      children: [
        { path: "", name: "home", component: HomeView, meta: { requiresAuth: true } },
        { path: "deals", name: "deals", component: DealsView, meta: { requiresAuth: true } },
        {
          path: "profile",
          name: "profile",
          component: ProfileView,
          meta: { requiresAuth: true, roles: ["practitioner", "admin", "super_admin"] }
        }
      ]
    },
    {
      path: "/auth",
      component: AuthLayout,
      children: [{ path: "", name: "auth", component: AuthView }]
    },
  ]
});

router.beforeEach((to) => evaluateRouteGuard(to, sessionState));

export default router;
