<script setup lang="ts">
const { data: posts } = await useAsyncData('posts-list', () => {
  return queryCollection('content').path('/posts').all()
})
</script>

<template>
  <div class="flex flex-col gap-4 mt-8">
    <div v-if="posts && posts.length > 0">
      <div v-for="post in posts" :key="post.path" class="p-4 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-blue-500 transition-colors">
        <NuxtLink :to="post.path" class="text-xl font-bold text-blue-600 dark:text-blue-400">
          {{ post.title }}
        </NuxtLink>
        <p class="text-gray-500 text-sm mt-2">{{ post.description || '点击查看文章详情' }}</p>
      </div>
    </div>
    <div v-else class="text-gray-500">
      暂无文章。
    </div>
  </div>
</template>
