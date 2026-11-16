<script setup lang="ts">
const { data: posts } = await useAsyncData('posts-list', () => {
  // 匹配 /posts/ 开头的所有文章
  return queryCollection('content').where('path', 'LIKE', '/posts/%').all()
})
</script>

<template>
  <div class="mt-6 border-t border-gray-200 dark:border-gray-800">
    <div v-if="posts && posts.length > 0">
      <!-- 极简风格：左侧竖线指示条 + 宽边距 + 底部实线 -->
      <NuxtLink
        v-for="post in posts"
        :key="post.path"
        :to="post.path"
        class="flex items-center px-4 py-5 
               border-b border-gray-200 dark:border-gray-800 
               border-l-4 border-l-transparent 
               hover:border-l-blue-500 
               transition-all duration-200 group"
      >
        <span class="text-lg font-medium text-gray-800 dark:text-gray-200 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
          {{ post.title }}
        </span>
      </NuxtLink>
    </div>
    
    <div v-else class="py-10 text-center text-gray-500">
      暂无文章。
    </div>
  </div>
</template>
