import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 后端端口可由 start.bat 通过环境变量 VITE_API_PORT 指定，
// 避免与他人已占用 8000 端口的服务冲突。
const apiPort = process.env.VITE_API_PORT || 8000

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: `http://127.0.0.1:${apiPort}`,
        changeOrigin: true,
      },
    },
  },
})
