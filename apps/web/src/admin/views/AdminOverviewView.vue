<template>
  <DashboardPageShell eyebrow="Admin" title="Platform Overview" subtitle="Multi-tenant governance, financial operations, and live ecosystem visibility.">
    <PaddedSectionCard v-if="loading">
      <AppLoadingState title="Loading control tower metrics" description="Fetching live platform operations, payout, and activity data." />
    </PaddedSectionCard>
    <PaddedSectionCard v-else-if="error">
      <AppErrorState title="Overview unavailable" :description="error" />
    </PaddedSectionCard>

    <template v-else>
      <section class="metrics-grid">
        <article v-for="metric in metrics" :key="metric.label" class="metric-card">
          <p>{{ metric.label }}</p>
          <strong>{{ metric.value }}</strong>
          <span>{{ metric.delta }}</span>
        </article>
      </section>

      <section class="upper-grid">
        <PaddedSectionCard>
          <h3>Growth Trend</h3>
          <div class="trend-bars"><span v-for="(value, index) in trend" :key="index" :style="barStyle(value)"></span></div>
        </PaddedSectionCard>

        <PaddedSectionCard>
          <h3>Operational Alerts</h3>
          <div class="list">
            <article v-for="(alert, index) in alerts" :key="index" class="list-item">{{ alert }}</article>
          </div>
        </PaddedSectionCard>
      </section>

      <section class="upper-grid">
        <PaddedSectionCard>
          <h3>Payout Queue</h3>
          <div class="list">
            <article v-for="item in payoutQueue" :key="item.id" class="list-item list-item--row">
              <div>
                <p>{{ item.creator }}</p>
                <span>{{ item.id }}</span>
              </div>
              <div class="right">
                <strong>{{ item.amount }}</strong>
                <AppStatusPill :status="item.status" />
              </div>
            </article>
          </div>
        </PaddedSectionCard>

        <PaddedSectionCard>
          <h3>Top Creators</h3>
          <div class="list">
            <article v-for="creator in topCreators" :key="creator.name" class="list-item list-item--row">
              <div>
                <p>{{ creator.name }}</p>
                <span>{{ creator.deals }} live deals</span>
              </div>
              <strong>{{ creator.revenue }}</strong>
            </article>
          </div>
        </PaddedSectionCard>
      </section>

      <PaddedSectionCard>
        <h3>Live Activity Feed</h3>
        <div v-if="activity.length === 0" class="empty">No activity available.</div>
        <div v-else class="list">
          <article v-for="item in activity" :key="item.id" class="list-item list-item--row">
            <p>{{ item.text }}</p>
            <span>{{ item.at }}</span>
          </article>
        </div>
      </PaddedSectionCard>
    </template>
  </DashboardPageShell>
</template>

<script setup lang="ts">
import { onMounted, watchEffect } from "vue";
import { useAdminOverview } from "../composables/useAdminOverview";
import DashboardPageShell from "../../design-system/patterns/DashboardPageShell.vue";
import PaddedSectionCard from "../../design-system/patterns/PaddedSectionCard.vue";
import AppErrorState from "../../design-system/primitives/AppErrorState.vue";
import AppLoadingState from "../../design-system/primitives/AppLoadingState.vue";
import AppStatusPill from "../../design-system/primitives/AppStatusPill.vue";
import { adminState } from "../stores/adminState";

const { activity, alerts, error, loading, load, metrics, payoutQueue, topCreators, trend } = useAdminOverview();

function barStyle(value: number) {
  const max = Math.max(...trend.value, 1);
  const h = Math.max(10, Math.round((value / max) * 100));
  return { height: `${h}%` };
}

onMounted(load);

watchEffect(() => {
  adminState.alerts = alerts.value.slice(0, 2);
});
</script>

<style scoped>
.metrics-grid { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 14px; }
.metric-card { border-radius: 14px; border: 1px solid rgba(255,255,255,.1); background: rgba(255,255,255,.03); padding: 14px; }
.metric-card p { margin: 0; font-size: 11px; text-transform: uppercase; letter-spacing: .08em; color: rgba(255,255,255,.6); }
.metric-card strong { display: block; margin-top: 10px; font-size: 28px; letter-spacing: -0.02em; }
.metric-card span { display: block; margin-top: 6px; color: #52d58b; font-size: 12px; }
.upper-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.trend-bars { height: 140px; display: grid; grid-auto-flow: column; gap: 8px; align-items: end; }
.trend-bars span { border-radius: 9px 9px 3px 3px; background: linear-gradient(180deg, rgba(113,182,255,.9), rgba(30,66,132,.88)); }
.list { display: grid; gap: 10px; }
.list-item { border-radius: 12px; border: 1px solid rgba(255,255,255,.1); background: rgba(255,255,255,.02); padding: 10px 12px; }
.list-item--row { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.list-item p { margin: 0; }
.list-item span { display: block; margin-top: 4px; font-size: 12px; color: rgba(255,255,255,.58); }
.right { text-align: right; }
.badge { border-radius: 999px; border: 1px solid rgba(240,190,100,.4); color: #f4d8a7; padding: 3px 8px; font-size: 10px; text-transform: uppercase; letter-spacing: .08em; }
.empty { color: rgba(255,255,255,.62); }
@media (max-width: 1200px) {
  .metrics-grid { grid-template-columns: 1fr 1fr; }
  .upper-grid { grid-template-columns: 1fr; }
}
@media (max-width: 767px) {
  .metrics-grid { grid-template-columns: 1fr; }
}
</style>
