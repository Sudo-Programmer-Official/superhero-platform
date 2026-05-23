import type { RouteRecordRaw } from "vue-router";
import AppLayout from "../layouts/AppLayout.vue";
import BookingsView from "../views/BookingsView.vue";
import CreateDealView from "../views/CreateDealView.vue";
import DealsView from "../views/DealsView.vue";
import HomeView from "../views/HomeView.vue";
import PayoutsView from "../views/PayoutsView.vue";
import ProfileView from "../views/ProfileView.vue";
import RedemptionsView from "../views/RedemptionsView.vue";
import SettingsView from "../views/SettingsView.vue";
import WalletPassesView from "../views/WalletPassesView.vue";

export const dashboardRoutes: RouteRecordRaw[] = [
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
      { path: "dashboard/payouts", name: "payouts", component: PayoutsView, meta: { requiresAuth: true } },
      { path: "dashboard/settings", name: "settings", component: SettingsView, meta: { requiresAuth: true } },
      {
        path: "dashboard/profile",
        name: "profile",
        component: ProfileView,
        meta: { requiresAuth: true, roles: ["practitioner", "admin", "super_admin"] }
      }
    ]
  }
];
