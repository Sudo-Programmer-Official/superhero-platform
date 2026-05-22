<template>
  <section class="dashboard-panel">
    <header class="dashboard-top">
      <div>
        <h1>Good morning, {{ firstName }} 👋</h1>
        <p>Here's what's happening with your practice today.</p>
      </div>
      <div class="dashboard-top__actions">
        <button class="icon-btn" type="button" aria-label="Search">⌕</button>
        <button class="icon-btn" type="button" aria-label="Notifications">◌</button>
        <AppButton tag="RouterLink" to="/dashboard/deals/create" variant="primary" size="nav" context="navbar" class="create-deal-btn">+ Create deal</AppButton>
      </div>
    </header>

    <section class="metrics-grid">
      <article v-for="metric in metrics" :key="metric.label" class="metric-card">
        <p class="metric-card__label">{{ metric.label }}</p>
        <p class="metric-card__value">{{ metric.value }}</p>
        <p class="metric-card__growth">{{ metric.growth }}</p>
      </article>
    </section>

    <section class="lower-grid">
      <article class="data-panel">
        <h2>Upcoming</h2>
        <div class="event-list">
          <div v-for="event in upcoming" :key="event.title" class="event-row">
            <div class="event-row__left">
              <img :src="event.image" :alt="event.title" />
              <div>
                <p>{{ event.title }}</p>
                <span>{{ event.meta }}</span>
              </div>
            </div>
            <p class="event-row__status" :class="event.statusTone">{{ event.status }}</p>
          </div>
        </div>
      </article>

      <article class="data-panel">
        <h2>Recent activity</h2>
        <div class="activity-list">
          <div v-for="activity in activities" :key="activity.id" class="activity-row">
            <div class="activity-row__left">
              <img :src="activity.image" alt="Activity" />
              <p>{{ activity.text }}</p>
            </div>
            <span>{{ activity.time }}</span>
          </div>
        </div>
      </article>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import AppButton from "../design-system/primitives/AppButton.vue";
import { activityLabel, activityTime, type ActivityEvent } from "../domain/activity";
import { listActivityEvents } from "../services/api";
import { sessionState } from "../stores/session";

const firstName = computed(() => {
  const displayName = sessionState.user?.displayName?.trim() || sessionState.me?.practitioner_name?.trim() || "there";
  return displayName.split(/\s+/)[0] || "there";
});

const metrics = [
  { label: "Total Bookings", value: "128", growth: "+18% this week" },
  { label: "Revenue", value: "$3,256", growth: "+21% this week" },
  { label: "Redemptions", value: "96", growth: "+18% this week" },
  { label: "Conversion Rate", value: "32%", growth: "+8% this week" }
];

const upcoming = [
  {
    title: "Breathwork Journey",
    meta: "May 24, 2026 · 7:00 PM",
    status: "12 / 20",
    statusTone: "is-green",
    image: "https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?auto=format&fit=crop&w=120&q=80"
  },
  {
    title: "Morning Flow Yoga",
    meta: "May 27, 2026 · 8:00 AM",
    status: "8 / 15",
    statusTone: "is-gold",
    image: "https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=120&q=80"
  },
  {
    title: "Sound Bath Evening",
    meta: "May 31, 2026 · 6:30 PM",
    status: "6 / 20",
    statusTone: "is-red",
    image: "https://images.unsplash.com/photo-1593811167562-9cef47bfc4d7?auto=format&fit=crop&w=120&q=80"
  }
];

const activityEvents = ref<ActivityEvent[]>([]);
const activities = computed(() =>
  activityEvents.value.slice(0, 8).map((event) => ({
    id: event.id,
    text: activityLabel(event),
    time: activityTime(event.created_at),
    image: "https://images.unsplash.com/photo-1531891437562-4301cf35b7e4?auto=format&fit=crop&w=120&q=80"
  }))
);

onMounted(async () => {
  if (!sessionState.token) return;
  try {
    activityEvents.value = await listActivityEvents(sessionState.token);
  } catch {
    activityEvents.value = [];
  }
});
</script>

<style scoped>
.dashboard-panel {
  width: 100%;
  min-height: 100dvh;
  box-sizing: border-box;
  border-radius: 0;
  border: 0;
  padding: 20px 24px 24px;
  background: linear-gradient(180deg, rgba(8, 12, 28, 0.82), rgba(5, 10, 24, 0.72));
  box-shadow: none;
}

.dashboard-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.dashboard-top h1 {
  margin: 0;
  font-size: 36px;
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.dashboard-top p {
  margin: 6px 0 0;
  font-size: 16px;
  color: rgba(255, 255, 255, 0.68);
}

.dashboard-top__actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.icon-btn {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.85);
  background: rgba(255, 255, 255, 0.03);
  transition: all 180ms ease;
}

.icon-btn:hover {
  background: rgba(255, 255, 255, 0.06);
}

.create-deal-btn {
  min-height: 48px;
  padding-inline: 22px;
  border-radius: 16px;
  font-size: 15px;
  font-weight: 600;
  box-shadow: 0 0 32px rgba(240, 190, 100, 0.24);
}

.metrics-grid {
  margin-top: 32px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.metric-card {
  min-height: 128px;
  border-radius: 22px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding: 22px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.03), rgba(255, 255, 255, 0.015));
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.24);
}

.metric-card__label {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.62);
}

.metric-card__value {
  margin: 12px 0 0;
  font-size: 38px;
  font-weight: 700;
}

.metric-card__growth {
  margin: 12px 0 0;
  font-size: 14px;
  color: #52d58b;
}

.lower-grid {
  margin-top: 24px;
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 20px;
}

.data-panel {
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding: 24px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.03), rgba(255, 255, 255, 0.015));
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.24);
}

.data-panel h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
}

.event-list,
.activity-list {
  margin-top: 16px;
  display: grid;
  gap: 16px;
}

.event-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-radius: 16px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.02);
  transition: all 180ms ease;
}

.event-row:hover,
.activity-row:hover {
  background: rgba(255, 255, 255, 0.04);
  box-shadow: 0 12px 56px rgba(0, 0, 0, 0.32);
}

.event-row__left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.event-row__left img {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  object-fit: cover;
}

.event-row__left p {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.event-row__left span {
  display: block;
  margin-top: 4px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.64);
}

.event-row__status {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  white-space: nowrap;
}

.event-row__status.is-green {
  color: #52d58b;
}

.event-row__status.is-gold {
  color: #f4c97d;
}

.event-row__status.is-red {
  color: #f08a6b;
}

.activity-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-radius: 16px;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.02);
  transition: all 180ms ease;
}

.activity-row__left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.activity-row__left img {
  width: 36px;
  height: 36px;
  border-radius: 999px;
  object-fit: cover;
}

.activity-row__left p {
  margin: 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
}

.activity-row span {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.55);
  white-space: nowrap;
}

@media (max-width: 1279px) {
  .metrics-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 1023px) {
  .dashboard-panel {
    min-height: calc(100dvh - 58px);
    padding: 18px 14px 24px;
    border-radius: 0;
  }

  .dashboard-top {
    flex-direction: column;
  }

  .dashboard-top h1 {
    font-size: 30px;
  }

  .dashboard-top__actions {
    width: 100%;
    justify-content: flex-start;
  }

  .lower-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 767px) {
  .metrics-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
  }

  .metric-card {
    padding: 16px;
    min-height: 112px;
  }

  .metric-card__value {
    font-size: 30px;
  }

  .event-row__status {
    font-size: 22px;
  }
}
</style>
