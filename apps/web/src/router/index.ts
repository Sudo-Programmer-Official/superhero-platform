import { createRouter, createWebHistory } from "vue-router";
import AuthView from "../views/AuthView.vue";
import DealsView from "../views/DealsView.vue";
import HomeView from "../views/HomeView.vue";
import ProfileView from "../views/ProfileView.vue";
import { initSessionWatcher, sessionState } from "../stores/session";

initSessionWatcher();

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/auth", name: "auth", component: AuthView },
    { path: "/", name: "home", component: HomeView, meta: { requiresAuth: true } },
    { path: "/deals", name: "deals", component: DealsView, meta: { requiresAuth: true } },
    {
      path: "/profile",
      name: "profile",
      component: ProfileView,
      meta: { requiresAuth: true, roles: ["practitioner", "admin", "super_admin"] }
    }
  ]
});

router.beforeEach((to) => {
  if (!sessionState.ready) return true;
  if (to.meta.requiresAuth && !sessionState.token) return { name: "auth" };
  if (to.name === "auth" && sessionState.token) return { name: "home" };

  const allowedRoles = to.meta.roles as string[] | undefined;
  if (allowedRoles && sessionState.me && !allowedRoles.includes(sessionState.me.role)) {
    return { name: "home" };
  }
  return true;
});

export default router;
