import type { RouteRecordRaw } from "vue-router";
import AdminLayout from "../admin/layouts/AdminLayout.vue";
import AdminOpsView from "../admin/views/AdminOpsView.vue";
import AdminOverviewView from "../admin/views/AdminOverviewView.vue";

export const adminRoutes: RouteRecordRaw[] = [
  {
    path: "/admin",
    component: AdminLayout,
    meta: {
      requiresAuth: true,
      roles: ["super_admin", "admin", "operator", "finance_admin", "support_admin", "moderator"]
    },
    children: [
      { path: "", redirect: { name: "admin-overview" } },
      { path: "overview", name: "admin-overview", component: AdminOverviewView, meta: { requiresAuth: true, roles: ["super_admin", "admin", "operator", "finance_admin", "support_admin", "moderator"] } },
      { path: "practitioners", name: "admin-practitioners", component: AdminOpsView, meta: { requiresAuth: true, roles: ["super_admin", "admin", "operator", "support_admin"], adminMode: "practitioners", adminEyebrow: "Admin", adminTitle: "Practitioners", adminSubtitle: "CRM-style practitioner operations and account governance." } },
      { path: "deals", name: "admin-deals", component: AdminOpsView, meta: { requiresAuth: true, roles: ["super_admin", "admin", "operator", "moderator"], adminMode: "deals", adminEyebrow: "Admin", adminTitle: "Deals", adminSubtitle: "Global campaign moderation, visibility, and revenue oversight." } },
      { path: "wallet-passes", name: "admin-wallet-passes", component: AdminOpsView, meta: { requiresAuth: true, roles: ["super_admin", "admin", "operator", "support_admin"], adminMode: "wallet-passes", adminEyebrow: "Admin", adminTitle: "Wallet Passes", adminSubtitle: "Pass generation, lifecycle, and provider diagnostics." } },
      { path: "redemptions", name: "admin-redemptions", component: AdminOpsView, meta: { requiresAuth: true, roles: ["super_admin", "admin", "operator", "support_admin", "moderator"], adminMode: "redemptions", adminEyebrow: "Admin", adminTitle: "Redemptions", adminSubtitle: "Live scan feed, fraud flags, and duplicate detection." } },
      { path: "bookings", name: "admin-bookings", component: AdminOpsView, meta: { requiresAuth: true, roles: ["super_admin", "admin", "operator", "finance_admin", "support_admin"], adminMode: "bookings", adminEyebrow: "Admin", adminTitle: "Bookings", adminSubtitle: "Canonical booking records with payment and refund states." } },
      { path: "payouts", name: "admin-payouts", component: AdminOpsView, meta: { requiresAuth: true, roles: ["super_admin", "finance_admin"], adminMode: "payouts", adminEyebrow: "Admin", adminTitle: "Payouts", adminSubtitle: "Payout queue, transfer states, and approval workflows." } },
      { path: "subscriptions", name: "admin-subscriptions", component: AdminOpsView, meta: { requiresAuth: true, roles: ["super_admin", "finance_admin", "support_admin"], adminMode: "subscriptions", adminEyebrow: "Admin", adminTitle: "Subscriptions", adminSubtitle: "Plan performance, billing failures, and retention risk." } },
      { path: "merchandise", name: "admin-merchandise", component: AdminOpsView, meta: { requiresAuth: true, roles: ["super_admin", "admin", "operator"], adminMode: "merchandise", adminEyebrow: "Admin", adminTitle: "Merchandise", adminSubtitle: "Inventory, fulfillment, and commerce operations." } },
      { path: "analytics", name: "admin-analytics", component: AdminOpsView, meta: { requiresAuth: true, roles: ["super_admin", "admin", "operator", "finance_admin"], adminMode: "analytics", adminEyebrow: "Admin", adminTitle: "Analytics", adminSubtitle: "Growth curves, conversion funnels, and retention signals." } },
      { path: "support", name: "admin-support", component: AdminOpsView, meta: { requiresAuth: true, roles: ["super_admin", "admin", "operator", "support_admin"], adminMode: "support", adminEyebrow: "Admin", adminTitle: "Support", adminSubtitle: "Tickets, escalations, and internal note workflows." } },
      { path: "automations", name: "admin-automations", component: AdminOpsView, meta: { requiresAuth: true, roles: ["super_admin", "admin", "operator"], adminMode: "automations", adminEyebrow: "Admin", adminTitle: "Automations", adminSubtitle: "Job queues, retries, and notification pipeline health." } },
      { path: "moderation", name: "admin-moderation", component: AdminOpsView, meta: { requiresAuth: true, roles: ["super_admin", "admin", "operator", "moderator"], adminMode: "moderation", adminEyebrow: "Admin", adminTitle: "Moderation", adminSubtitle: "Flagged content, risk signals, and policy enforcement." } },
      { path: "integrations", name: "admin-integrations", component: AdminOpsView, meta: { requiresAuth: true, roles: ["super_admin", "admin", "operator", "finance_admin"], adminMode: "integrations", adminEyebrow: "Admin", adminTitle: "Integrations", adminSubtitle: "Provider health, sync status, and webhook visibility." } },
      { path: "system-health", name: "admin-health", component: AdminOpsView, meta: { requiresAuth: true, roles: ["super_admin", "admin", "operator"], adminMode: "health", adminEyebrow: "Admin", adminTitle: "System Health", adminSubtitle: "Uptime, queue depth, and platform risk indicators." } },
      { path: "settings", name: "admin-settings", component: AdminOpsView, meta: { requiresAuth: true, roles: ["super_admin"], adminMode: "settings", adminEyebrow: "Admin", adminTitle: "Admin Settings", adminSubtitle: "Platform fees, feature flags, and maintenance controls." } }
    ]
  }
];
