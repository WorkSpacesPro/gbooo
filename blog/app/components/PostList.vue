<script setup lang="ts">
const { data: posts } = await useAsyncData('posts-list', () => {
  return queryCollection('content').where('path', 'LIKE', '/posts/%').all()
})
</script>

<template>
  <div class="mt-6 border-t border-gray-200 dark:border-gray-800">
    <div v-if="posts && posts.length > 0">
      <!-- 极简纯横线：默认蓝字，悬浮深蓝 -->
      <NuxtLink
        v-for="post in posts"
        :key="post.path"
        :to="post.path"
        class="flex items-center px-4 py-5 
               border-b border-gray-200 dark:border-gray-800 
               transition-all duration-200 group"
      >
        <!-- 核心变色逻辑在这里 -->
        <span class="text-lg font-medium 
                     text-blue-600 hover:text-blue-800 
                     dark:text-blue-400 dark:hover:text-blue-300 
                     transition-colors">
          {{ post.title }}
        </span>
      </NuxtLink>
    </div>
    
    <div v-else class="py-10 text-center text-gray-500">
      暂无文章。
    </div>
  </div>
</template>
