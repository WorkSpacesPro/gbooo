<script setup lang="ts">
const route = useRoute()
const { data: page } = await useAsyncData(route.path, () => {
  return queryCollection('content').path(route.path).first()
})
</script>

<template>
  <div>
    <ContentRenderer v-if="page" :value="page" />
    <div v-else>页面不存在 (404)</div>
  </div>
</template>
