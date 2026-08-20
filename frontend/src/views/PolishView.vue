<template>
  <section>
    <div class="page-head">
      <h2>AI 润色</h2>
      <p>粘贴你写好的文案，一键换风格</p>
    </div>

    <div class="polish">
      <!-- 原文输入 -->
      <div class="card panel">
        <h3>原文 <span class="badge">粘贴</span></h3>
        <textarea v-model="srcText" placeholder="粘贴你写好的文案…" />
        <button class="btn-ghost" :disabled="polishing || !srcText.trim()" @click="doPolish">
          {{ polishing ? '润色中…' : '润色一下' }}
        </button>
      </div>

      <!-- 润色结果 -->
      <div class="card panel">
        <h3>润色结果 <span class="badge" :style="done ? badgeDone : badgeIdle">{{ mode }}</span></h3>
        <div class="seg">
          <button
            v-for="m in MODES"
            :key="m"
            :class="{ on: mode === m }"
            @click="switchMode(m)"
          >{{ m }}</button>
        </div>
        <div class="result-box">
          {{ resultText || '点击左侧「润色一下」，或先切换风格再生成 ✨' }}
        </div>
        <div class="actions">
          <button class="btn-soft" :disabled="!resultText" @click="copyResult">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="9" y="9" width="13" height="13" rx="2" />
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
            </svg>复制
          </button>
          <button class="btn-soft" :disabled="!resultText" @click="replaceSrc">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 2v6h6" />
              <path d="M21 12A9 9 0 0 0 6 5.3L3 8" />
              <path d="M21 22v-6h-6" />
              <path d="M3 12a9 9 0 0 0 15 6.7l3-2.7" />
            </svg>替换原文
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { polish } from '../api/polish'
import { ApiError } from '../api/client'
import { useToast } from '../stores/toast'

const MODES = ['更文艺', '更简短', '加 emoji', '更幽默', '更治愈']
const toast = useToast()

const srcText = ref('')
const mode = ref('更文艺')
const resultText = ref('')
const polishing = ref(false)
const done = ref(false)

const badgeDone = { color: 'var(--c-secondary)', background: 'rgba(13,148,136,.1)' }
const badgeIdle = { color: 'var(--c-text-3)', background: 'rgba(0,0,0,.05)' }

async function doPolish() {
  if (!srcText.value.trim()) {
    toast.msg.value = '请先输入要润色的文案'
    return
  }
  polishing.value = true
  try {
    const resp = await polish({ text: srcText.value, mode: mode.value })
    resultText.value = resp.text
    done.value = true
    toast.msg.value = `已润色（${mode.value}）`
  } catch (e) {
    handleError(e)
  } finally {
    polishing.value = false
  }
}

function switchMode(m) {
  mode.value = m
  // 已有结果时立即重新润色
  if (done.value && srcText.value.trim()) doPolish()
}

function copyResult() {
  navigator.clipboard
    .writeText(resultText.value)
    .then(() => (toast.msg.value = '已复制到剪贴板'))
    .catch(() => (toast.msg.value = '复制失败，请重试'))
}

function replaceSrc() {
  if (!resultText.value) return
  srcText.value = resultText.value
  toast.msg.value = '已替换原文'
}

function handleError(e) {
  // 润色失败/网络异常统一用小 Toast 轻提示
  if (e instanceof ApiError) toast.msg.value = e.message || '润色失败，请重试'
  else toast.msg.value = '润色失败，请重试'
}
</script>

<style scoped>
.page-head h2 { font-size: 20px; font-weight: 600; }
.page-head p { color: var(--c-text-2); font-size: 14px; margin-top: 4px; }

.polish {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: var(--sp-lg); align-items: start; margin-top: var(--sp-xl);
}
.panel { padding: var(--sp-xl); display: flex; flex-direction: column; gap: var(--sp-md); }
.panel h3 { font-size: 16px; font-weight: 600; display: flex; align-items: center; gap: 8px; }
.panel h3 .badge {
  font-size: 11px; font-weight: 700;
  padding: 2px 8px; border-radius: 999px;
}
.panel textarea {
  width: 100%; min-height: 200px; resize: vertical;
  border: 1px solid rgba(0, 0, 0, 0.08); border-radius: var(--radius-control);
  padding: var(--sp-md); font-size: 15px; line-height: 1.7;
  outline: none; transition: 0.15s; background: #fff; color: var(--c-text-1);
}
.panel textarea:focus { border-color: var(--c-primary); box-shadow: 0 0 0 3px rgba(232, 89, 12, 0.1); }

.btn-ghost {
  align-self: flex-start;
  background: rgba(232, 89, 12, 0.07); color: var(--c-primary); font-weight: 600;
  border-radius: var(--radius-control); height: 40px; padding: 0 var(--sp-lg);
  font-size: 14px; transition: 0.15s;
}
.btn-ghost:hover:not(:disabled) { background: rgba(232, 89, 12, 0.14); }
.btn-ghost:disabled { opacity: 0.5; cursor: not-allowed; }

.seg { display: inline-flex; background: rgba(0, 0, 0, 0.04); border-radius: var(--radius-control); padding: 4px; gap: 2px; align-self: flex-start; }
.seg button { font-size: 13px; font-weight: 600; color: var(--c-text-2); padding: 6px 12px; border-radius: 9px; transition: 0.15s; }
.seg button.on { background: #fff; color: var(--c-primary); box-shadow: var(--shadow-card); }

.result-box {
  min-height: 200px; border: 1px dashed rgba(232, 89, 12, 0.3);
  border-radius: var(--radius-control); padding: var(--sp-md);
  font-size: 15px; line-height: 1.75; color: var(--c-text-1);
  background: rgba(255, 247, 242, 0.5); white-space: pre-wrap;
}
.actions { display: flex; gap: var(--sp-sm); margin-top: var(--sp-xs); }
.btn-soft {
  background: #fff; color: var(--c-text-2);
  border-radius: var(--radius-control); height: 40px; padding: 0 var(--sp-md);
  font-size: 14px; border: 1px solid rgba(0, 0, 0, 0.06);
  transition: 0.15s; display: inline-flex; align-items: center; gap: 6px;
}
.btn-soft:hover:not(:disabled) { border-color: rgba(232, 89, 12, 0.4); color: var(--c-primary); }
.btn-soft:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-soft svg { width: 16px; height: 16px; }

@media (max-width: 768px) {
  .polish { grid-template-columns: 1fr; }
}
</style>
