import type { RouteRecordRaw } from "vue-router";
import LandingView from "../views/LandingView.vue";
import PublicDealView from "../views/PublicDealView.vue";
import PublicProfileView from "../views/PublicProfileView.vue";

export const publicRoutes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "landing",
    component: LandingView
  },
  {
    path: "/openmat/:practitionerSlug",
    name: "public-profile",
    component: PublicProfileView
  },
  {
    path: "/p/:practitionerSlug",
    name: "public-profile-short",
    component: PublicProfileView
  },
  {
    path: "/openmat/:practitionerSlug/:dealSlug",
    name: "public-deal",
    component: PublicDealView
  }
];
