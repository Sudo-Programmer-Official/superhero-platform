<template>
  <section class="deals-control-center">
    <PaddedSectionCard class="control-bar">
      <div class="control-bar__top">
        <div>
          <p class="eyebrow">Control Center</p>
          <h2>Operate your campaigns</h2>
        </div>
      </div>

      <div class="control-bar__row">
        <AppInput :model-value="search" placeholder="Search by title, location, slug" @update:model-value="setSearch" />

        <select class="control-select" :value="sort" @change="setSort(($event.target as HTMLSelectElement).value as DealSort)">
          <option value="newest">Newest first</option>
          <option value="oldest">Oldest first</option>
          <option value="revenue_desc">Revenue high → low</option>
          <option value="conversion_desc">Conversion high → low</option>
          <option value="bookings_desc">Bookings high → low</option>
        </select>

        <select class="control-select" :value="filter" @change="setFilter(($event.target as HTMLSelectElement).value as DealStatusFilter)">
          <option value="all">All statuses</option>
          <option value="published">Published</option>
          <option value="draft">Draft</option>
          <option value="sold_out">Sold out</option>
          <option value="archived">Archived</option>
          <option value="expired">Expired</option>
        </select>

        <div class="view-toggle" role="tablist" aria-label="View mode">
          <button class="toggle-btn" :class="{ 'is-active': viewMode === 'grid' }" @click="setViewMode('grid')">Grid</button>
          <button class="toggle-btn" :class="{ 'is-active': viewMode === 'list' }" @click="setViewMode('list')">List</button>
        </div>
      </div>

      <div class="chips">
        <button class="chip" :class="{ 'is-active': filter === 'all' }" @click="setFilter('all')">All {{ statusCounts.all }}</button>
        <button class="chip" :class="{ 'is-active': filter === 'published' }" @click="setFilter('published')">Published {{ statusCounts.published }}</button>
        <button class="chip" :class="{ 'is-active': filter === 'draft' }" @click="setFilter('draft')">Draft {{ statusCounts.draft }}</button>
        <button class="chip" :class="{ 'is-active': filter === 'sold_out' }" @click="setFilter('sold_out')">Sold out {{ statusCounts.sold_out }}</button>
        <button class="chip" :class="{ 'is-active': filter === 'archived' }" @click="setFilter('archived')">Archived {{ statusCounts.archived }}</button>
        <button class="chip" :class="{ 'is-active': filter === 'expired' }" @click="setFilter('expired')">Expired {{ statusCounts.expired }}</button>
      </div>
    </PaddedSectionCard>

    <AppCard v-if="focusId && !focusedDealFound" muted>
      <p class="mb-1 text-xs uppercase tracking-[0.12em] text-[var(--accent)]">Deep Link</p>
      <p class="m-0 text-sm text-[var(--text-secondary)]">Deal not found for id: {{ focusId.slice(0, 8) }}</p>
    </AppCard>

    <div v-if="loading" class="skeleton-grid" :class="{ 'is-list': viewMode === 'list' }">
      <div v-for="n in viewMode === 'grid' ? 6 : 4" :key="`sk-${n}`" class="skeleton-card shimmer"></div>
    </div>

    <AppCard v-else-if="error">
      <AppErrorState title="Deals unavailable" :description="error" />
    </AppCard>

    <AppCard v-else-if="hasEmptyState" class="empty-state">
      <div class="empty-illustration">◌</div>
      <h3>No deals yet</h3>
      <p>Launch your first campaign to start tracking bookings, revenue, and conversion.</p>
      <AppButton tag="RouterLink" to="/dashboard/deals/create" variant="primary" size="form">Create First Deal</AppButton>
    </AppCard>

    <template v-else>
      <div v-if="viewMode === 'grid'" class="deal-grid">
        <article v-for="deal in paginatedDeals" :key="deal.id" class="deal-card" :class="{ 'is-focused': focusId === deal.id }">
          <div class="cover-wrap">
            <img v-if="deal.image" :src="deal.image" :alt="deal.title" class="cover" />
            <div v-else class="cover cover--fallback"></div>
            <span class="status" :class="`is-${getStatusColor(deal.lifecycle)}`">{{ getStatusLabel(deal.lifecycle) }}</span>
          </div>

          <div class="deal-body">
            <h3>{{ deal.title }}</h3>
            <p class="meta">{{ prettyDate(deal.start_at) }} · {{ deal.location_name }}</p>

            <div class="kpis">
              <div>
                <span>Seats sold</span>
                <strong>{{ deal.metric.bookings }} / {{ deal.total_seats }}</strong>
              </div>
              <div>
                <span>Revenue</span>
                <strong>{{ formatMoney(deal.metric.revenue, deal.currency) }}</strong>
              </div>
              <div>
                <span>Conversion</span>
                <strong>{{ deal.metric.conversion.toFixed(1) }}%</strong>
              </div>
            </div>

            <div class="chips-inline">
              <span class="mini-chip">Wallet {{ deal.wallet_enabled ? 'on' : 'off' }}</span>
              <span class="mini-chip">Remaining {{ deal.seats_remaining }}</span>
            </div>

            <div class="actions">
              <AppButton variant="ghost" @click="onEdit(deal.id)">Edit</AppButton>
              <AppButton variant="ghost" @click="duplicateDealById(deal.id)">Duplicate</AppButton>
              <AppButton v-if="deal.lifecycle !== 'published'" variant="secondary" @click="setPublished(deal.id, true)">Publish</AppButton>
              <AppButton v-else variant="secondary" @click="setPublished(deal.id, false)">Unpublish</AppButton>
              <AppButton v-if="deal.public_url" variant="ghost" @click="copyShareLink(deal.public_url)">Copy link</AppButton>
              <AppButton v-if="deal.public_url" variant="ghost" @click="viewPublicPage(deal.public_url)">View public</AppButton>
              <AppButton variant="ghost" @click="archiveById(deal.id)">Archive</AppButton>
            </div>
          </div>
        </article>
      </div>

      <AppCard v-else class="list-wrap">
        <table class="deal-table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Status</th>
              <th>Bookings</th>
              <th>Revenue</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="deal in paginatedDeals" :key="deal.id" :class="{ 'is-focused': focusId === deal.id }">
              <td>
                <p class="table-title">{{ deal.title }}</p>
                <p class="table-sub">{{ deal.location_name }}</p>
              </td>
              <td><span class="status" :class="`is-${getStatusColor(deal.lifecycle)}`">{{ getStatusLabel(deal.lifecycle) }}</span></td>
              <td>{{ deal.metric.bookings }} / {{ deal.total_seats }}</td>
              <td>{{ formatMoney(deal.metric.revenue, deal.currency) }}</td>
              <td>{{ prettyDate(deal.created_at) }}</td>
              <td>
                <div class="table-actions">
                  <button @click="duplicateDealById(deal.id)">Duplicate</button>
                  <button @click="setPublished(deal.id, deal.lifecycle !== 'published')">{{ deal.lifecycle === 'published' ? 'Unpublish' : 'Publish' }}</button>
                  <button @click="archiveById(deal.id)">Archive</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </AppCard>

      <div class="pagination">
        <AppButton variant="ghost" :disabled="page <= 1" @click="goToPrevPage">Previous</AppButton>
        <p>Page {{ page }} / {{ totalPages }}</p>
        <AppButton variant="ghost" :disabled="page >= totalPages" @click="goToNextPage">Next</AppButton>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import AppButton from "../../design-system/primitives/AppButton.vue";
import AppCard from "../../design-system/primitives/AppCard.vue";
import AppErrorState from "../../design-system/primitives/AppErrorState.vue";
import AppInput from "../../design-system/primitives/AppInput.vue";
import PaddedSectionCard from "../../design-system/patterns/PaddedSectionCard.vue";
import { useDealsControlCenter, type DealSort, type DealStatusFilter } from "../../composables/useDealsControlCenter";
import { formatDealDate, formatDealTime, formatMoney, getStatusColor, getStatusLabel } from "../../domain/deal";

const props = defineProps<{ focusDealId?: string }>();
const router = useRouter();

const {
  archiveById,
  copyShareLink,
  duplicateDealById,
  focusId,
  focusedDealFound,
  goToNextPage,
  goToPrevPage,
  hasEmptyState,
  loadDeals,
  loading,
  error,
  page,
  paginatedDeals,
  search,
  setFilter,
  setSearch,
  setSort,
  setViewMode,
  setPublished,
  sort,
  statusCounts,
  totalPages,
  viewMode,
  filter,
  viewPublicPage
} = useDealsControlCenter(props.focusDealId);

function prettyDate(value: string): string {
  return `${formatDealDate(value)} ${formatDealTime(value)}`;
}

function onEdit(dealId: string) {
  void router.push({ path: "/dashboard/deals/create", query: { edit: dealId } });
}

onMounted(async () => {
  await loadDeals();
});
</script>

<style scoped>
.deals-control-center { display: grid; gap: 20px; padding-bottom: 32px; }
.control-bar { position: sticky; top: 24px; z-index: 5; backdrop-filter: blur(12px); padding-top: 32px; }
.control-bar__top { display: flex; justify-content: space-between; gap: 16px; align-items: center; }
.control-bar__top h2 { margin: 4px 0 0; font-size: 28px; line-height: 1.2; }
.control-bar__row { margin-top: 20px; display: grid; grid-template-columns: minmax(260px, 1.4fr) 200px 200px auto; gap: 16px; align-items: stretch; }
.control-select { height: 48px; border-radius: 14px; border: 1px solid rgba(255,255,255,.14); background: rgba(12,18,30,.68); color: #dbe5f3; padding: 0 12px; }
.view-toggle { display: flex; gap: 10px; }
.toggle-btn { height: 48px; border-radius: 14px; border: 1px solid rgba(255,255,255,.16); background: rgba(255,255,255,.03); color: rgba(255,255,255,.75); padding: 0 14px; }
.toggle-btn.is-active { border-color: rgba(240,190,100,.55); background: rgba(240,190,100,.16); color: #f4d8a7; }
.chips { margin-top: 20px; display: flex; flex-wrap: wrap; gap: 14px; }
.chip { border-radius: 999px; border: 1px solid rgba(255,255,255,.14); background: rgba(255,255,255,.03); color: rgba(255,255,255,.75); padding: 8px 12px; font-size: 12px; }
.chip.is-active { border-color: rgba(240,190,100,.5); background: rgba(240,190,100,.15); color: #f4d8a7; }
.skeleton-grid { display: grid; gap: 16px; grid-template-columns: repeat(3, minmax(0,1fr)); }
.skeleton-grid.is-list { grid-template-columns: 1fr; }
.skeleton-card { height: 230px; border-radius: 20px; border: 1px solid rgba(255,255,255,.08); background: rgba(255,255,255,.04); }
.shimmer { background-image: linear-gradient(100deg, rgba(255,255,255,.03) 20%, rgba(255,255,255,.1) 50%, rgba(255,255,255,.03) 80%); background-size: 200% 100%; animation: shimmer 1.5s linear infinite; }
.empty-state { text-align: center; padding: 32px 24px; display: grid; gap: 12px; justify-items: center; }
.empty-illustration { width: 64px; height: 64px; border-radius: 18px; border: 1px solid rgba(240,190,100,.38); background: rgba(240,190,100,.12); display: grid; place-items: center; color: #f4d8a7; font-size: 28px; }
.deal-grid { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 20px; }
.deal-card {
  position: relative;
  border-radius: 22px;
  border: 1px solid rgba(193, 218, 255, 0.14);
  overflow: hidden;
  background:
    linear-gradient(180deg, rgba(20, 33, 54, 0.74), rgba(8, 14, 28, 0.88)),
    radial-gradient(140% 100% at 10% 0%, rgba(110, 156, 230, 0.15), transparent 55%);
  backdrop-filter: blur(10px);
  box-shadow:
    0 14px 36px rgba(0, 0, 0, 0.28),
    0 0 0 1px rgba(146, 182, 233, 0.08) inset,
    0 -20px 40px rgba(123, 156, 214, 0.08) inset;
  transition: transform 220ms ease, box-shadow 220ms ease, border-color 220ms ease;
}
.deal-card::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.11), rgba(255, 255, 255, 0) 26%);
  opacity: 0.55;
}
.deal-card::after {
  content: "";
  position: absolute;
  inset: 1px;
  border-radius: 21px;
  pointer-events: none;
  border: 1px solid rgba(255, 255, 255, 0.06);
}
.deal-card:hover {
  transform: translateY(-4px);
  border-color: rgba(203, 228, 255, 0.24);
  box-shadow:
    0 26px 56px rgba(0, 0, 0, 0.4),
    0 8px 26px rgba(121, 171, 255, 0.14),
    0 0 0 1px rgba(160, 197, 255, 0.14) inset,
    0 -24px 42px rgba(132, 166, 225, 0.1) inset;
}
.deal-card.is-focused { box-shadow: 0 0 0 1px rgba(240,190,100,.45), 0 28px 52px rgba(240,190,100,.16), 0 -18px 30px rgba(240,190,100,.08) inset; }
.cover-wrap { position: relative; }
.cover { width: 100%; height: 160px; object-fit: cover; display: block; transform: scale(1); transform-origin: center; transition: transform 260ms ease, filter 260ms ease; }
.deal-card:hover .cover { transform: scale(1.03); filter: saturate(1.04) contrast(1.02); }
.cover--fallback { background: linear-gradient(135deg, rgba(30,49,78,.88), rgba(8,14,25,.95)); }
.status { position: absolute; top: 10px; right: 10px; border-radius: 999px; border: 1px solid rgba(255,255,255,.16); background: rgba(8,12,22,.72); color: #dbe5f3; padding: 4px 9px; font-size: 11px; text-transform: uppercase; letter-spacing: .08em; }
.status.is-green { border-color: rgba(82,213,139,.5); color: #52d58b; }
.status.is-amber { border-color: rgba(240,190,100,.55); color: #f4d8a7; }
.status.is-red { border-color: rgba(255,120,120,.55); color: #ffb5b5; }
.status.is-slate { border-color: rgba(164,176,198,.45); color: #b8c2d6; }
.deal-body { padding: 18px; display: grid; gap: 14px; }
.deal-body h3 { margin: 0; font-size: 21px; line-height: 1.15; }
.meta { margin: 0; color: rgba(255,255,255,.66); font-size: 13px; }
.kpis { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 12px; }
.kpis div {
  border-radius: 12px;
  border: 1px solid rgba(188, 214, 255, 0.14);
  background: linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.02));
  box-shadow: 0 1px 0 rgba(255,255,255,.08) inset, 0 8px 18px rgba(0,0,0,.18) inset;
  padding: 12px;
}
.kpis span { display: block; font-size: 11px; text-transform: uppercase; letter-spacing: .08em; color: rgba(255,255,255,.56); }
.kpis strong { font-size: 16px; line-height: 1.2; color: #f1f6ff; }
.chips-inline { display: flex; gap: 12px; flex-wrap: wrap; }
.mini-chip {
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 11px;
  border: 1px solid rgba(188, 214, 255, 0.2);
  color: rgba(235, 242, 255, 0.88);
  background: linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.02));
}
.actions { display: flex; gap: 8px; flex-wrap: wrap; }
.actions :deep(button),
.actions :deep(a) {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.18), 0 1px 0 rgba(255, 255, 255, 0.1) inset;
  transition: transform 180ms ease, box-shadow 180ms ease, background 180ms ease, border-color 180ms ease;
}
.actions :deep(button:hover),
.actions :deep(a:hover) {
  transform: translateY(-1px);
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.24), 0 0 16px rgba(117, 168, 255, 0.16);
}
.list-wrap { overflow: auto; }
.deal-table { width: 100%; border-collapse: collapse; min-width: 820px; }
.deal-table th { text-align: left; font-size: 12px; text-transform: uppercase; letter-spacing: .08em; color: rgba(255,255,255,.58); border-bottom: 1px solid rgba(255,255,255,.12); padding: 12px; }
.deal-table td { padding: 12px; border-bottom: 1px solid rgba(255,255,255,.07); color: rgba(255,255,255,.82); }
.deal-table tr.is-focused { background: rgba(240,190,100,.07); }
.table-title { margin: 0; font-weight: 600; }
.table-sub { margin: 3px 0 0; font-size: 12px; color: rgba(255,255,255,.55); }
.table-actions { display: flex; gap: 8px; }
.table-actions button { background: transparent; border: 1px solid rgba(255,255,255,.16); border-radius: 999px; color: rgba(255,255,255,.78); padding: 4px 8px; font-size: 12px; }
.pagination { display: flex; justify-content: space-between; align-items: center; gap: 16px; }
.pagination p { margin: 0; color: rgba(255,255,255,.7); }
@keyframes shimmer { to { background-position: -200% 0; } }
@media (max-width: 1240px) {
  .deal-grid, .skeleton-grid { grid-template-columns: repeat(2, minmax(0,1fr)); }
}
@media (max-width: 980px) {
  .control-bar { position: static; }
  .control-bar__row { grid-template-columns: 1fr 1fr; gap: 14px; }
}
@media (max-width: 767px) {
  .deals-control-center { padding-bottom: 84px; }
  .control-bar { position: sticky; top: 12px; padding-top: 28px; }
  .control-bar__top { align-items: flex-start; flex-direction: column; }
  .control-bar__row { grid-template-columns: 1fr; }
  .deal-grid, .skeleton-grid { grid-template-columns: 1fr; }
  .pagination { position: sticky; bottom: 10px; border: 1px solid rgba(255,255,255,.12); border-radius: 14px; padding: 8px; background: rgba(8,12,22,.86); backdrop-filter: blur(12px); }
}
</style>
