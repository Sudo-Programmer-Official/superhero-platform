<template>
  <div class="auth-layout">
    <div class="bg-orb bg-orb-a" aria-hidden="true"></div>
    <div class="bg-orb bg-orb-b" aria-hidden="true"></div>

    <header class="auth-header content-wrap">
      <RouterLink class="eyebrow auth-home-link" to="/">In-Person Superhero</RouterLink>
    </header>

    <main class="auth-main content-wrap" role="main">
      <RouterView />
    </main>
  </div>
</template>
