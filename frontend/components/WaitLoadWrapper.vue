<template>
  <div>
    <slot v-if="!loading" />
  </div>
</template>

<script setup lang="ts">
// Makes content wait for page load to render. Can be used to solve hydration mismatch errors.

const loading = ref(true);
const nuxtApp = useNuxtApp();
nuxtApp.hook("page:finish", () => {
  loading.value = false;
});
</script>
