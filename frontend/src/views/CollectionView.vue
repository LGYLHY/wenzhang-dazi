<template>
  <section>
    <div class="page-head">
      <h2>我的收藏</h2>
      <p>你点亮星标的好文案都在这里，按情绪分组 · 已存 {{ total }} 条</p>
    </div>

    <!-- 无收藏空态 -->
    <div class="card empty" v-if="total === 0">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
      </svg>
      <div class="t">还没有收藏，去生成页点亮星标吧</div>
      <a class="l" @click="$router.push('/generate')">去生成 →</a>
    </div>

    <div class="two-col" v-else>
      <!-- 左侧分组 -->
      <nav class="group-nav">
        <button class="g" :class="{ on: group === 'all' }" @click="group = 'all'">
          <span class="dot" :style="{ background: 'var(--c-text-3)' }" />
          全部
          <span class="cnt">{{ total }}</span>
        </button>
        <button
          v-for="g in groups"
          :key="g.emotion"
          class="g"
          :class="{ on: group === g.emotion }"
          @click="group = g.emotion"
        >
          <span class="dot" :style="{ background: colorOf(g.emotion) }" />
          {{ g.emotion }}
          <span class="cnt">{{ g.count }}</span>
        </button>
      </nav>

      <!-- 右侧列表 -->
      <div>
        <div style="display: flex; justify-content: flex-end; margin-bottom: var(--sp-md)">
          <button class="btn-soft danger" @click="onClearAll">清空收藏</button>
        </div>
        <div class="fav-list" v-if="filtered.length">
          <div
            v-for="item in filtered"
            :key="item.id"
            class="card card-hover fav-item"
          >
            <div class="strip" :style="{ background: colorOf(item.emotion) }" />
            <div class="c-body">
              <div class="c-text" :title="item.text">{{ item.text }}</div>
              <div class="c-actions">
                <button class="icon-btn" title="复制" @click="onCopy(item)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="9" y="9" width="13" height="13" rx="2" />
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                  </svg>
                </button>
                <button class="icon-btn del" title="删除" @click="onRemove(item)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="3 6 5 6 21 6" />
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 分组空态 -->
        <div class="card empty" v-else>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10" />
            <path d="M8 14s1.5 2 4 2 4-2 4-2" />
            <line x1="9" y1="9" x2="9.01" y2="9" />
            <line x1="15" y1="9" x2="15.01" y2="9" />
          </svg>
          <div class="t">这个分组还没有收藏</div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { historyStore } from '../stores/historyStore'
import { useToast } from '../stores/toast'
import { listEmotions } from '../api/generate'

const group = ref('all')
const toast = useToast()

// 情绪色（fallback 与设计文档 8 色一致）
const emotions = ref({
  日常: '#E8590C', 治愈: '#0D9488', 幽默: '#FFB703', 文艺: '#7F77DD',
  带货: '#A8763E', 凡尔赛: '#378ADD', 清新: '#5DCAA5', 情感: '#F2708A',
})

onMounted(async () => {
  try {
    const data = await listEmotions()
    if (data && typeof data === 'object') emotions.value = data
  } catch (_) {/* fallback */}
})

const total = computed(() => historyStore.list().length)
const groups = computed(() => {
  const cnt = historyStore.groupCounts()
  // 保持 8 情绪的设计顺序，过滤掉计数为 0 的
  return Object.keys(emotions.value)
    .filter((k) => cnt[k])
    .map((k) => ({ emotion: k, count: cnt[k] }))
})
const filtered = computed(() => {
  const list = historyStore.list()
  if (group.value === 'all') return list
  return list.filter((i) => i.emotion === group.value)
})

function colorOf(emotion) {
  return emotions.value[emotion] || '#E8590C'
}

function onCopy(item) {
  navigator.clipboard
    .writeText(item.text)
    .then(() => (toast.msg.value = '已复制到剪贴板'))
    .catch(() => (toast.msg.value = '复制失败，请重试'))
}

function onRemove(item) {
  historyStore.remove(item.id)
  toast.msg.value = '已删除'
}

function onClearAll() {
  if (!window.confirm('确定清空全部收藏吗？此操作不可恢复。')) return
  historyStore.clear()
  group.value = 'all'
  toast.msg.value = '已清空收藏'
}
</script>

<style scoped>
.page-head h2 { font-size: 20px; font-weight: 600; }
.page-head p { color: var(--c-text-2); font-size: 14px; margin-top: 4px; }

.two-col {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: var(--sp-2xl);
  align-items: start;
  margin-top: var(--sp-xl);
}
.group-nav {
  position: sticky; top: 88px;
  display: flex; flex-direction: column; gap: 4px;
}
.group-nav .g {
  display: flex; align-items: center; gap: var(--sp-sm);
  padding: 10px 14px; border-radius: var(--radius-control);
  color: var(--c-text-2); font-size: 14px; font-weight: 600;
  transition: 0.15s; text-align: left; width: 100%;
}
.group-nav .g .dot { width: 9px; height: 9px; border-radius: 50%; flex: none; }
.group-nav .g .cnt { margin-left: auto; color: var(--c-text-3); font-weight: 400; }
.group-nav .g:hover { background: rgba(232, 89, 12, 0.06); color: var(--c-text-1); }
.group-nav .g.on { background: var(--c-primary); color: #fff; }
.group-nav .g.on .cnt { color: rgba(255, 255, 255, 0.8); }
.group-nav .g.on .dot { box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.5); }

.fav-list { display: flex; flex-direction: column; gap: var(--sp-md); }
.fav-item { display: flex; overflow: hidden; }
.fav-item .strip { width: 4px; flex: none; }
.fav-item .c-body {
  flex: 1; padding: var(--sp-md) var(--sp-lg);
  display: flex; align-items: center; gap: var(--sp-md);
}
.fav-item .c-text {
  flex: 1; font-size: 14px; color: var(--c-text-1);
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
  line-height: 1.6;
}
.fav-item .c-actions { display: flex; gap: var(--sp-sm); flex: none; }

.icon-btn {
  width: 36px; height: 36px; border-radius: 10px;
  display: grid; place-items: center;
  background: rgba(0, 0, 0, 0.04); color: var(--c-text-2); transition: 0.15s;
}
.icon-btn:hover { background: rgba(232, 89, 12, 0.1); color: var(--c-primary); }
.icon-btn.del:hover { background: rgba(220, 38, 38, 0.1); color: var(--c-error); }
.icon-btn svg { width: 18px; height: 18px; }

.btn-soft {
  background: #fff; color: var(--c-text-2);
  border-radius: var(--radius-control); height: 36px; padding: 0 var(--sp-md);
  font-size: 13px; border: 1px solid rgba(0, 0, 0, 0.06);
  transition: 0.15s; display: inline-flex; align-items: center; gap: 6px;
}
.btn-soft.danger { color: var(--c-error); border-color: rgba(220, 38, 38, 0.3); }
.btn-soft.danger:hover { background: rgba(220, 38, 38, 0.06); }

.empty {
  text-align: center; padding: var(--sp-2xl);
  color: var(--c-text-3);
  display: flex; flex-direction: column; align-items: center; gap: var(--sp-md);
  margin-top: var(--sp-xl);
}
.empty svg { width: 56px; height: 56px; color: var(--c-text-3); opacity: 0.5; }
.empty .t { font-size: 15px; color: var(--c-text-2); }
.empty .l { color: var(--c-primary); font-weight: 600; cursor: pointer; }

@media (max-width: 768px) {
  .two-col { grid-template-columns: 1fr; gap: var(--sp-lg); }
  .group-nav {
    position: static; flex-direction: row; overflow-x: auto; padding-bottom: 4px;
  }
  .group-nav .g { white-space: nowrap; flex: none; }
}
@media (min-width: 769px) and (max-width: 1199px) {
  .two-col { grid-template-columns: 200px 1fr; }
}
</style>
