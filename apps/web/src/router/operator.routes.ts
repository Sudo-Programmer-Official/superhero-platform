import type { RouteRecordRaw } from "vue-router";
import OperatorLayout from "../layouts/OperatorLayout.vue";
import OperatorCreateOfferView from "../views/operator/OperatorCreateOfferView.vue";
import OperatorScannerView from "../views/operator/OperatorScannerView.vue";
import OperatorShareView from "../views/operator/OperatorShareView.vue";
import OperatorWalletView from "../views/operator/OperatorWalletView.vue";

export const operatorRoutes: RouteRecordRaw[] = [
  {
    path: "/operator",
    component: OperatorLayout,
    meta: { requiresAuth: true, roles: ["practitioner", "admin", "super_admin"] },
    children: [
      { path: "", redirect: { name: "operator-share" } },
      { path: "share", name: "operator-share", component: OperatorShareView, meta: { requiresAuth: true, roles: ["practitioner", "admin", "super_admin"] } },
      { path: "share/create", name: "operator-offer-create", component: OperatorCreateOfferView, meta: { requiresAuth: true, roles: ["practitioner", "admin", "super_admin"] } },
      { path: "wallet", name: "operator-wallet", component: OperatorWalletView, meta: { requiresAuth: true, roles: ["practitioner", "admin", "super_admin"] } },
      { path: "scanner", name: "operator-scanner", component: OperatorScannerView, meta: { requiresAuth: true, roles: ["practitioner", "admin", "super_admin"] } }
    ]
  }
];
