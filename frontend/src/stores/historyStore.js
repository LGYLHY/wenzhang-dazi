/**
 * historyStore：本地收藏（localStorage，支持 1000+ 条）
 * - 对应 PRD FR6（历史记录：列表/删除/清空）与 FR7（人设记忆前置）
 * - 单条结构：{ id, text, emotion, style, createdAt }
 * - 隐私：只存文案文本，不存图片 base64 / 人脸信息
 */
import { ref } from 'vue'

const KEY = 'wenzhang_dazi_favorites'
const MAX = 2000 // 上限（PRD ≥1000 即可满足）

const items = ref([])

function read() {
  try {
    const raw = localStorage.getItem(KEY)
    const arr = raw ? JSON.parse(raw) : []
    return Array.isArray(arr) ? arr : []
  } catch (_) {
    return []
  }
}

function write(list) {
  items.value = list
  try {
    localStorage.setItem(KEY, JSON.stringify(list))
  } catch (e) {
    // 容量超限：丢弃最老的 1/3，保留最新
    if (e && (e.name === 'QuotaExceededError' || e.code === 22)) {
      const trimmed = list.slice(Math.floor(list.length / 3))
      try {
        localStorage.setItem(KEY, JSON.stringify(trimmed))
        items.value = trimmed
      } catch (_) {}
    }
  }
}

/** 首次调用加载 */
function ensure() {
  if (!items._loaded) {
    items.value = read()
    items._loaded = true
  }
}

/** 收藏（按 text 去重；已存在则返回 null） */
function add({ text, emotion = '日常', style = '日常' }) {
  ensure()
  const t = (text || '').trim()
  if (!t) return null
  if (items.value.some((i) => i.text === t)) return null
  if (items.value.length >= MAX) {
    // 达到上限：移除最旧的 5% 再入队（保证收藏永远可用）
    write(items.value.slice(Math.floor(MAX * 0.05)))
  }
  const item = {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    text: t,
    emotion: emotion || '日常',
    style: style || '日常',
    createdAt: Date.now(),
  }
  write([item, ...items.value])
  return item
}

/** 是否已收藏（按 text） */
function has(text) {
  ensure()
  return items.value.some((i) => i.text === text)
}

/** 删除（按 id） */
function remove(id) {
  ensure()
  write(items.value.filter((i) => i.id !== id))
}

/** 清空全部 */
function clear() {
  write([])
}

/** 全部收藏（新→旧） */
function list() {
  ensure()
  return items.value
}

/** 按情绪分组后的计数（用于左侧分组栏） */
function groupCounts() {
  ensure()
  const map = {}
  for (const i of items.value) map[i.emotion] = (map[i.emotion] || 0) + 1
  return map
}

export const historyStore = {
  items,
  add,
  has,
  remove,
  clear,
  list,
  groupCounts,
}
