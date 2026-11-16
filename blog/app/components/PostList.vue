<script setup lang="ts">
const { data: posts } = await useAsyncData('posts-list', () => {
  return queryCollection('content').where('path', 'LIKE', '/posts/%').all()
})
</script>

<template>
  <div class="mt-6 border-t border-gray-200 dark:border-gray-800">
    <div v-if="posts && posts.length > 0">
      <!-- 循环列表，使用 odd: 和 even: 实现斑马纹 -->
      <NuxtLink
        v-for="post in posts"
        :key="post.path"
        :to="post.path"
        class="flex items-center px-2 py-4 border-b border-gray-200 dark:border-gray-800 transition-colors
               odd:bg-white even:bg-gray-50
               dark:odd:bg-[#111111] dark:even:bg-[#1a1a1a]
               hover:bg-gray-100 dark:hover:bg-gray-800 group"
      >
        <!-- 只显示标题，去掉描述 -->
        <span class="text-lg font-medium text-gray-800 dark:text-gray-200 group-hover:text-blue-600 dark:group-hover:text-blue-400">
          {{ post.title }}
        </span>
      </NuxtLink>
    </div>
    
    <div v-else class="py-10 text-center text-gray-500">
      暂无文章。
    </div>
  </div>
</template>
