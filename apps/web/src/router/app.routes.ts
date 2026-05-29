import type { RouteRecordRaw } from "vue-router";
import PrimaryAppLayout from "../layouts/PrimaryAppLayout.vue";
import OperatorCreateOfferView from "../views/operator/OperatorCreateOfferView.vue";
import OperatorScannerView from "../views/operator/OperatorScannerView.vue";
import OperatorShareView from "../views/operator/OperatorShareView.vue";
import PayoutsView from "../views/PayoutsView.vue";
import AppProfileView from "../views/AppProfileView.vue";

const appMeta = { requiresAuth: true, roles: ["practitioner", "admin", "super_admin"] };

export const appRoutes: RouteRecordRaw[] = [
  {
    path: "/app",
    component: PrimaryAppLayout,
    meta: appMeta,
    children: [
      { path: "", redirect: { name: "app-deals" } },
      { path: "deals", name: "app-deals", component: OperatorShareView, meta: appMeta },
      { path: "deals/create", name: "app-deals-create", component: OperatorCreateOfferView, meta: appMeta },
      { path: "wallet", redirect: { name: "app-redemptions" }, meta: appMeta },
      { path: "redemptions", name: "app-redemptions", component: OperatorScannerView, meta: appMeta },
      { path: "payouts", name: "app-payouts", component: PayoutsView, meta: appMeta },
      { path: "profile", name: "app-profile", component: AppProfileView, meta: appMeta },
    ]
  }
];
