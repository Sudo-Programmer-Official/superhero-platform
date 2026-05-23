<template>
  <DashboardPageShell eyebrow="Profile" title="Profile" subtitle="Manage your public practitioner identity and account details.">
    <div class="profile-wrap">
      <ProfilePanel />
    </div>
  </DashboardPageShell>
</template>

<script setup lang="ts">
import DashboardPageShell from "../design-system/patterns/DashboardPageShell.vue";
import ProfilePanel from "../modules/profile/ProfilePanel.vue";
</script>

<style scoped>
.profile-wrap {
  width: 100%;
  max-width: 960px;
}
</style>
