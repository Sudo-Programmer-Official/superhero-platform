import { createRouter, createWebHistory } from "vue-router";
import { initSessionWatcher, sessionState } from "../stores/session";
import { adminRoutes } from "./admin.routes";
import { authRoutes } from "./auth.routes";
import { dashboardRoutes } from "./dashboard.routes";
import { evaluateRouteGuard } from "./guard";
import { publicRoutes } from "./public.routes";

initSessionWatcher();

const router = createRouter({
  history: createWebHistory(),
  routes: [
    ...publicRoutes,
    ...authRoutes,
    ...dashboardRoutes,
    ...adminRoutes
  ]
});

router.beforeEach((to) => evaluateRouteGuard(to, sessionState));

export default router;
