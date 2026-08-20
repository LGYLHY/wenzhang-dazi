<template>
  <section>
    <div class="page-head">
      <h2>模板广场</h2>
      <p>按场景挑一个，一键带入生成页</p>
    </div>

    <!-- 分类 Tab -->
    <div class="tabs">
      <button
        v-for="cat in CATEGORIES"
        :key="cat"
        class="tab"
        :class="{ on: active === cat }"
        @click="switchTab(cat)"
      >{{ cat }}</button>
    </div>

    <!-- 卡片网格 -->
    <div class="tpl-grid" v-if="templates.length">
      <div
        v-for="t in templates"
        :key="t.id"
        class="card card-hover tpl"
        @click="useTemplate(t)"
      >
        <div class="ico">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS[t.icon] || ICONS.tag" />
        </div>
        <h3>{{ t.title }}</h3>
        <ul class="examples">
          <li
            v-for="(ex, i) in (Array.isArray(t.example) ? t.example : [t.example])"
            :key="i"
            title="点击使用这条示例"
            @click.stop="useTemplate(t, i)"
          >{{ ex }}</li>
        </ul>
        <span class="go">
          用这个模板
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="5" y1="12" x2="19" y2="12" />
            <polyline points="12 5 19 12 12 19" />
          </svg>
        </span>
      </div>
    </div>

    <!-- 空态 -->
    <div class="card empty" v-else-if="!loading">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10" />
        <path d="M8 14s1.5 2 4 2 4-2 4-2" />
        <line x1="9" y1="9" x2="9.01" y2="9" />
        <line x1="15" y1="9" x2="15.01" y2="9" />
      </svg>
      <div class="t">这个分类还没有模板</div>
    </div>

    <!-- 加载中骨架 -->
    <div class="tpl-grid" v-else>
      <div v-for="i in 4" :key="i" class="card sk-tpl" />
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listTemplates } from '../api/templates'

const CATEGORIES = ['全部', '节日', '旅行', '美食', '情感', '带货']

const ICONS = {
  sun: '<path d="M12 17a5 5 0 1 0 0-10 5 5 0 0 0 0 10Z"/><polyline points="12 1 12 3"/><polyline points="12 21 12 23"/><polyline points="4.22 4.22 5.64 5.64"/><polyline points="18.36 18.36 19.78 19.78"/><polyline points="1 12 3 12"/><polyline points="21 12 23 12"/><polyline points="4.22 19.78 5.64 18.36"/><polyline points="18.36 5.64 19.78 4.22"/>',
  map: '<polygon points="1 6 8 3 16 6 23 3 23 18 16 21 8 18 1 21"/><line x1="8" y1="3" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="21"/>',
  food: '<path d="M3 2v7c0 1.1.9 2 2 2h0a2 2 0 0 0 2-2V2"/><line x1="4" y1="2" x2="4" y2="22"/><path d="M14 2v20"/><path d="M14 11a4 4 0 0 0 4 4 3 3 0 0 0 3-3V2"/>',
  heart: '<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78Z"/>',
  gift: '<polyline points="20 12 20 22 4 22 4 12"/><rect x="2" y="7" width="20" height="5"/><line x1="12" y1="22" x2="12" y2="7"/><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7Z"/><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7Z"/>',
  tag: '<path d="M20.59 13.41 12 22l-9-9V3h10l9 9.41a2 2 0 0 1 0 1Z"/><line x1="7" y1="7" x2="7.01" y2="7"/>',
}

const router = useRouter()
const active = ref('全部')
const templates = ref([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const cat = active.value === '全部' ? 'all' : active.value
    templates.value = await listTemplates(cat)
  } catch (_) {
    templates.value = []
  } finally {
    loading.value = false
  }
}

function switchTab(cat) {
  active.value = cat
  load()
}

function useTemplate(t, exIndex = 0) {
  // 预载到生成页：只带选中的那一条示例（默认第 1 条），输入框保持干净
  const examples = Array.isArray(t.example) ? t.example : [t.example]
  const ex = examples[exIndex] || examples[0] || ''
  router.push({
    path: '/generate',
    query: { tpl: t.title, example: ex, key: t.prompt_key },
  })
}

onMounted(load)
</script>

<style scoped>
.page-head h2 { font-size: 20px; font-weight: 600; }
.page-head p { color: var(--c-text-2); font-size: 14px; margin-top: 4px; }

.tabs { display: flex; gap: var(--sp-sm); flex-wrap: wrap; margin-bottom: var(--sp-xl); margin-top: var(--sp-lg); }
.tab {
  border-radius: var(--radius-pill); padding: 8px 16px;
  font-size: 14px; font-weight: 600;
  background: #fff; color: var(--c-text-2);
  border: 1px solid rgba(0, 0, 0, 0.06); transition: 0.15s;
}
.tab:hover { border-color: rgba(232, 89, 12, 0.4); color: var(--c-primary); }
.tab.on { background: var(--c-primary); color: #fff; border-color: var(--c-primary); }

.tpl-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--sp-lg); }
.tpl {
  padding: var(--sp-lg); cursor: pointer;
  display: flex; flex-direction: column; gap: var(--sp-sm);
}
.tpl .ico {
  width: 44px; height: 44px; border-radius: 12px;
  display: grid; place-items: center;
  background: rgba(232, 89, 12, 0.08); color: var(--c-primary);
}
.tpl .ico svg { width: 24px; height: 24px; }
.tpl h3 { font-size: 16px; font-weight: 600; }
.tpl .examples {
  list-style: none; padding: 0; margin: 0;
  font-size: 12px; color: var(--c-text-2); line-height: 1.55;
}
.tpl .examples li {
  padding: 3px 0 3px 14px;
  border-left: 2px solid rgba(232, 89, 12, 0.18);
  margin: 3px 0;
  cursor: pointer;
  border-radius: 0 6px 6px 0;
  transition: 0.15s;
}
.tpl .examples li:hover {
  background: rgba(232, 89, 12, 0.06);
  border-left-color: var(--c-primary);
  color: var(--c-text-1);
}
.tpl .go {
  margin-top: auto; font-size: 13px; color: var(--c-primary);
  font-weight: 600; display: inline-flex; align-items: center; gap: 4px;
}
.tpl .go svg { width: 14px; height: 14px; }

.sk-tpl { height: 170px; }

.empty {
  text-align: center; padding: var(--sp-2xl); margin-top: var(--sp-lg);
  color: var(--c-text-3);
  display: flex; flex-direction: column; align-items: center; gap: var(--sp-md);
}
.empty svg { width: 56px; height: 56px; opacity: 0.5; }
.empty .t { font-size: 15px; color: var(--c-text-2); }

@media (max-width: 768px) {
  .tpl-grid { grid-template-columns: 1fr; }
}
</style>
