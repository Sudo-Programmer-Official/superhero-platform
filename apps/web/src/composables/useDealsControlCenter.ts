import { computed, ref } from "vue";
import { getDealStatus, type DealStatus } from "../domain/deal";
import { archiveDeal, duplicateDeal, listDeals, type DealCardPayload, updateDealStatus } from "../services/api";
import { sessionState } from "../stores/session";
import { showToast } from "../stores/toast";

export type DealStatusFilter = "all" | "published" | "draft" | "sold_out" | "archived" | "expired";
export type DealSort = "newest" | "oldest" | "revenue_desc" | "conversion_desc" | "bookings_desc";
export type DealViewMode = "grid" | "list";

export type DealMetric = {
  bookings: number;
  revenue: number;
  conversion: number;
};

type DecoratedDeal = DealCardPayload & {
  metric: DealMetric;
  lifecycle: DealStatus;
};

const PAGE_SIZE = 12;

function calcMetric(deal: DealCardPayload): DealMetric {
  const bookings = Math.max(0, deal.capacity - deal.remaining_slots);
  const price = Number(deal.price || 0);
  const revenue = bookings * price;
  const conversion = deal.capacity > 0 ? Number(((bookings / deal.capacity) * 100).toFixed(1)) : 0;
  return { bookings, revenue, conversion };
}

function decorateDeal(deal: DealCardPayload): DecoratedDeal {
  return {
    ...deal,
    metric: calcMetric(deal),
    lifecycle: getDealStatus({
      status: deal.status,
      end_at: deal.end_at,
      seats_remaining: deal.seats_remaining
    })
  };
}

export function useDealsControlCenter(focusDealId?: string) {
  const deals = ref<DecoratedDeal[]>([]);
  const loading = ref(true);
  const error = ref("");
  const search = ref("");
  const filter = ref<DealStatusFilter>("all");
  const sort = ref<DealSort>("newest");
  const viewMode = ref<DealViewMode>("grid");
  const page = ref(1);
  const archivedIds = ref<Set<string>>(new Set());

  const focusId = (focusDealId || "").trim();

  const focusedDealFound = computed(() => {
    if (!focusId) return true;
    return deals.value.some((deal) => deal.id === focusId);
  });

  const statusCounts = computed(() => {
    const rows = deals.value.filter((deal) => !archivedIds.value.has(deal.id));
    return {
      all: rows.length,
      published: rows.filter((d) => d.lifecycle === "published").length,
      draft: rows.filter((d) => d.lifecycle === "draft").length,
      sold_out: rows.filter((d) => d.lifecycle === "sold_out").length,
      archived: rows.filter((d) => d.lifecycle === "archived").length,
      expired: rows.filter((d) => d.lifecycle === "expired").length
    };
  });

  const filteredDeals = computed(() => {
    let rows = deals.value.filter((deal) => !archivedIds.value.has(deal.id));

    const term = search.value.trim().toLowerCase();
    if (term) {
      rows = rows.filter((deal) => {
        return (
          deal.title.toLowerCase().includes(term) ||
          deal.location.toLowerCase().includes(term) ||
          deal.slug.toLowerCase().includes(term)
        );
      });
    }

    if (filter.value !== "all") {
      rows = rows.filter((deal) => deal.lifecycle === filter.value);
    }

    rows = [...rows].sort((a, b) => {
      if (sort.value === "oldest") return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      if (sort.value === "revenue_desc") return b.metric.revenue - a.metric.revenue;
      if (sort.value === "conversion_desc") return b.metric.conversion - a.metric.conversion;
      if (sort.value === "bookings_desc") return b.metric.bookings - a.metric.bookings;
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    });

    if (focusId) {
      rows = [...rows].sort((a, b) => {
        if (a.id === focusId) return -1;
        if (b.id === focusId) return 1;
        return 0;
      });
    }

    return rows;
  });

  const totalPages = computed(() => Math.max(1, Math.ceil(filteredDeals.value.length / PAGE_SIZE)));

  const paginatedDeals = computed(() => {
    const start = (page.value - 1) * PAGE_SIZE;
    return filteredDeals.value.slice(start, start + PAGE_SIZE);
  });

  const hasEmptyState = computed(() => !loading.value && filteredDeals.value.length === 0);

  function resetToFirstPage() {
    page.value = 1;
  }

  async function loadDeals() {
    if (!sessionState.token) return;
    loading.value = true;
    error.value = "";
    try {
      const payload = await listDeals(sessionState.token);
      deals.value = payload.map(decorateDeal);
    } catch (err) {
      error.value = `Failed to load deals: ${String(err)}`;
      showToast(error.value, "error");
    } finally {
      loading.value = false;
    }
  }

  async function setPublished(dealId: string, shouldPublish: boolean) {
    if (!sessionState.token) return;
    const idx = deals.value.findIndex((deal) => deal.id === dealId);
    if (idx < 0) return;

    const prev = deals.value[idx];
    const optimistic = decorateDeal({ ...prev, status: shouldPublish ? "published" : "draft" });
    deals.value[idx] = optimistic;

    try {
      const updated = await updateDealStatus(sessionState.token, dealId, shouldPublish ? "published" : "draft");
      deals.value[idx] = decorateDeal(updated);
      showToast(shouldPublish ? "Deal published" : "Deal unpublished", "success");
    } catch (err) {
      deals.value[idx] = prev;
      showToast(`Status update failed: ${String(err)}`, "error");
    }
  }

  async function markExpired(dealId: string) {
    if (!sessionState.token) return;
    const idx = deals.value.findIndex((deal) => deal.id === dealId);
    if (idx < 0) return;
    const prev = deals.value[idx];
    deals.value[idx] = decorateDeal({ ...prev, status: "expired" });

    try {
      const updated = await updateDealStatus(sessionState.token, dealId, "expired");
      deals.value[idx] = decorateDeal(updated);
      showToast("Deal archived to expired", "success");
    } catch (err) {
      deals.value[idx] = prev;
      showToast(`Archive failed: ${String(err)}`, "error");
    }
  }

  async function duplicateDealById(dealId: string) {
    if (!sessionState.token) return;
    try {
      const created = await duplicateDeal(sessionState.token, dealId);
      deals.value.unshift(decorateDeal(created));
      showToast("Draft duplicated", "success");
    } catch (err) {
      showToast(`Duplicate failed: ${String(err)}`, "error");
    }
  }

  async function archiveById(dealId: string) {
    if (!sessionState.token) return;
    try {
      const archived = await archiveDeal(sessionState.token, dealId);
      const idx = deals.value.findIndex((deal) => deal.id === dealId);
      if (idx >= 0) {
        deals.value[idx] = decorateDeal(archived);
      }
      showToast("Deal archived", "success");
    } catch (err) {
      showToast(`Archive failed: ${String(err)}`, "error");
    }
  }

  async function copyShareLink(sharePath: string | null) {
    if (!sharePath) return;
    try {
      await navigator.clipboard.writeText(`${window.location.origin}${sharePath}`);
      showToast("Share link copied", "success");
    } catch {
      showToast("Could not copy share link", "error");
    }
  }

  function viewPublicPage(sharePath: string | null) {
    if (!sharePath) return;
    window.open(`${window.location.origin}${sharePath}`, "_blank", "noopener,noreferrer");
  }

  function setFilter(next: DealStatusFilter) {
    filter.value = next;
    resetToFirstPage();
  }

  function setSort(next: DealSort) {
    sort.value = next;
    resetToFirstPage();
  }

  function setSearch(next: string) {
    search.value = next;
    resetToFirstPage();
  }

  function setViewMode(next: DealViewMode) {
    viewMode.value = next;
  }

  function goToNextPage() {
    page.value = Math.min(totalPages.value, page.value + 1);
  }

  function goToPrevPage() {
    page.value = Math.max(1, page.value - 1);
  }

  return {
    copyShareLink,
    duplicateDealById,
    filteredDeals,
    focusId,
    focusedDealFound,
    goToNextPage,
    goToPrevPage,
    hasEmptyState,
    loadDeals,
    loading,
    markExpired,
    page,
    paginatedDeals,
    search,
    setFilter,
    setSearch,
    setSort,
    setViewMode,
    setPublished,
    error,
    sort,
    statusCounts,
    totalPages,
    viewMode,
    filter,
    viewPublicPage,
    archiveById
  };
}
