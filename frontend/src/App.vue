<template>
  <div class="app">
    <!-- 顶部导航 -->
    <header class="topbar">
      <div class="brand">
        <span class="logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 20h9" />
            <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4Z" />
          </svg>
        </span>
        <span>
          文案搭子
          <small>有记忆的朋友圈图文搭档</small>
        </span>
      </div>

      <nav class="nav">
        <router-link to="/generate" :class="{ active: $route.name === 'generate' }">生成</router-link>
        <a href="#/favorites" :class="{ active: $route.name === 'favorites' }">收藏</a>
        <a href="#/square" :class="{ active: $route.name === 'square' }">广场</a>
        <a href="#/polish" :class="{ active: $route.name === 'polish' }">润色</a>
        <a href="#/help" :class="{ active: $route.name === 'help' }">帮助</a>
      </nav>

      <div class="avatar">搭</div>
    </header>

    <!-- 网络错误条 -->
    <div class="errbar" :class="{ show: errorVisible }">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z" />
        <line x1="12" y1="9" x2="12" y2="13" />
        <line x1="12" y1="17" x2="12.01" y2="17" />
      </svg>
      <span>{{ errorMsg }}</span>
      <button class="close" @click="errorVisible = false">关闭</button>
    </div>

    <main>
      <router-view />
    </main>

    <!-- 移动端底部 Tab Bar -->
    <nav class="tabbar">
      <router-link to="/generate" :class="{ on: $route.name === 'generate' }">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 20h9" />
          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4Z" />
        </svg>生成
      </router-link>
      <a href="#/favorites">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
        </svg>收藏
      </a>
      <a href="#/square">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="7" height="7" />
          <rect x="14" y="3" width="7" height="7" />
          <rect x="14" y="14" width="7" height="7" />
          <rect x="3" y="14" width="7" height="7" />
        </svg>广场
      </a>
      <a href="#/polish">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 20h9" />
          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4Z" />
        </svg>润色
      </a>
      <a href="#/help">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10" />
          <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>我的
      </a>
    </nav>

    <!-- Toast -->
    <div class="toast" :class="{ show: toastVisible }">
      <svg class="ok" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="20 6 9 17 4 12" />
      </svg>
      <span>{{ toastMsg }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useToast } from './stores/toast'
import { useErrorBar } from './stores/errorBar'

const toast = useToast()
const err = useErrorBar()

const toastVisible = ref(false)
const toastMsg = ref('')
const errorVisible = ref(false)
const errorMsg = ref('网络异常，请重试')

let toastTimer = null
function showToast(msg) {
  toastMsg.value = msg
  toastVisible.value = true
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => (toastVisible.value = false), 1600)
}

let errTimer = null
function showError(msg = '网络异常，请重试') {
  errorMsg.value = msg
  errorVisible.value = true
  clearTimeout(errTimer)
  errTimer = setTimeout(() => (errorVisible.value = false), 4000)
}

watch(toast.msg, (v) => v && showToast(v))
watch(err.msg, (v) => v && showError(v))
</script>
