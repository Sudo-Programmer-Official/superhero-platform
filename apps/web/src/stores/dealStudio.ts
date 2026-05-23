import { reactive } from "vue";

export type DealStudioForm = {
  title: string;
  description: string;
  category: string;
  coverImage: string;
  startsAt: string;
  endsAt: string;
  seats: string;
  price: string;
  redemptionType: "qr" | "nfc";
  visibility: "public" | "private";
  location: string;
  timezone: string;
};

export type DealStudioStatus = "idle" | "saving" | "publishing" | "done";

export const dealStudioState = reactive({
  step: 1,
  status: "idle" as DealStudioStatus,
  lastDraftId: "",
  shareUrl: "",
  qrUrl: "",
  form: {
    title: "",
    description: "",
    category: "Breathwork",
    coverImage: "",
    startsAt: "",
    endsAt: "",
    seats: "20",
    price: "45.00",
    redemptionType: "qr",
    visibility: "public",
    location: "",
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC"
  } as DealStudioForm
});

export function nextDealStudioStep() {
  if (dealStudioState.step < 4) dealStudioState.step += 1;
}

export function prevDealStudioStep() {
  if (dealStudioState.step > 1) dealStudioState.step -= 1;
}

export function resetDealStudio() {
  dealStudioState.step = 1;
  dealStudioState.status = "idle";
  dealStudioState.lastDraftId = "";
  dealStudioState.shareUrl = "";
  dealStudioState.qrUrl = "";
  dealStudioState.form = {
    title: "",
    description: "",
    category: "Breathwork",
    coverImage: "",
    startsAt: "",
    endsAt: "",
    seats: "20",
    price: "45.00",
    redemptionType: "qr",
    visibility: "public",
    location: "",
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC"
  };
}
