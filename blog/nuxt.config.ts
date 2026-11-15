import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
  modules: [
    '@nuxt/content',
    '@nuxt/icon',
    '@nuxt/eslint',
    '@nuxtjs/color-mode',
  ],

  css: ['assets/css/main.css'],
  colorMode: { classSuffix: '' },

  content: {
    // 👇 新增：使用 Node.js 原生 SQLite，绕过 better-sqlite3 编译报错
    experimental: {
      sqliteConnector: 'native'
    },
    build: {
      markdown: {
        highlight: {
          // See the available themes on https://github.com/shikijs/shiki/blob/main/docs/themes.md#all-theme
          theme: {
            dark: 'github-dark',
            default: 'github-light',
          },
        },
      },
    },
  },

  // 👇 核心修改 1：告诉网站它住在 /blog/ 路径下
  app: {
    baseURL: '/blog/' 
  },

  // 👇 核心修改 2：保留你的 404 设置，并指定 Cloudflare 打包格式
  nitro: {
    preset: 'cloudflare-pages', // 必须加，告诉系统按 Cloudflare 的格式输出
    prerender: {
      failOnError: false,
      routes: ['/404.html'] // 保留你的强制生成 404 页面
    }
  },

  future: {
    compatibilityVersion: 4,
  },
  compatibilityDate: '2025-02-19',

  vite: { plugins: [tailwindcss()] },
})
