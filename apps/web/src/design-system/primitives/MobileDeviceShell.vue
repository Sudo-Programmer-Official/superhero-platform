<template>
  <article class="device-card">
    <div class="device-shell">
      <div class="device-shell__island"></div>
      <div class="device-shell__content">
        <slot />
      </div>
      <div class="device-shell__tabs">
        <span :class="{ 'is-active': activeTab === 'home' }">⌂</span>
        <span :class="{ 'is-active': activeTab === 'deals' }">▣</span>
        <span :class="{ 'is-active': activeTab === 'wallet' }">◉</span>
        <span :class="{ 'is-active': activeTab === 'redeem' }">⌁</span>
        <span :class="{ 'is-active': activeTab === 'profile' }">◌</span>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
defineProps<{
  activeTab: "home" | "deals" | "wallet" | "redeem" | "profile";
}>();
</script>

<style scoped>
.device-card {
  width: fit-content;
  margin: 0 auto;
}

.device-shell {
  width: 280px;
  height: 620px;
  margin: 0 auto;
  border-radius: 32px;
  padding: 10px;
  background: linear-gradient(180deg, #0f1726, #080f1b);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 80px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.device-shell__island {
  width: 112px;
  height: 20px;
  margin: 4px auto 10px;
  border-radius: 999px;
  background: #060a14;
}

.device-shell__content {
  height: 520px;
  border-radius: 24px;
  overflow-y: auto;
  overflow-x: hidden;
  background: #050816;
  padding: 20px;
  color: #f8fafc;
}

.device-shell__tabs {
  margin-top: 10px;
  border-radius: 16px;
  height: 52px;
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  align-items: center;
  justify-items: center;
  color: rgba(255, 255, 255, 0.6);
  background: rgba(7, 12, 24, 0.76);
  backdrop-filter: blur(18px);
}

.device-shell__tabs span {
  font-size: 18px;
  line-height: 1;
}

.device-shell__tabs .is-active {
  color: #f0be64;
  text-shadow: 0 0 12px rgba(240, 190, 100, 0.45);
}

@media (max-width: 768px) {
  .device-shell {
    width: min(82vw, 320px);
    height: 600px;
  }

  .device-shell__content {
    height: 500px;
  }
}
</style>
