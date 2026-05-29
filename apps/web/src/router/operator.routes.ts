import type { RouteRecordRaw } from "vue-router";
export const operatorRoutes: RouteRecordRaw[] = [
  { path: "/operator", redirect: "/app" },
  { path: "/operator/share", redirect: "/app/deals" },
  { path: "/operator/share/create", redirect: "/app/deals/create" },
  { path: "/operator/wallet", redirect: "/app/redemptions" },
  { path: "/operator/scanner", redirect: "/app/redemptions" },
];
