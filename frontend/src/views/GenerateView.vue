<template>
  <section class="gen-wrap">
    <div class="hero">
      <h1>一句话，生成你的朋友圈</h1>
      <p>上传图片或描述心情，AI 帮你写好 3 条不同风格文案</p>
    </div>

    <div class="card composer">
      <textarea
        v-model="text"
        placeholder="今天去了海边，想发条朋友圈…"
        :disabled="loading"
      />
      <div class="divider" />
      <ImageUploader :disabled="loading" @change="onImageChange" />
      <div style="height: var(--sp-lg);" />
      <span class="field-label">选择语气（可多选）</span>
      <TonePills v-model="tones" />
    </div>

    <button
      class="btn-primary"
      :class="{ loading: loading || streaming }"
      :disabled="loading || streaming || (!text.trim() && !imageBase64)"
      @click="generate"
    >
      <span class="spin" />
      <span class="txt">{{ loading || streaming ? '生成中…' : '生成文案' }}</span>
    </button>

    <!-- 骨架屏（仅请求等待时显示；流式打字时由结果卡展示） -->
    <div class="skeleton" :class="{ show: loading }">
      <div class="sk-card" />
      <div class="sk-card" />
      <div class="sk-card" />
    </div>

    <!-- 结果区 -->
    <div class="results" v-if="copies.length">
      <ResultCard
        v-for="(c, i) in copies"
        :key="c._key || i"
        :copy="{ style: c.style, emotion: c.emotion, text: c.text }"
        :color="c.color"
        :emotion-label="c.emotion"
        :style-label="c.style"
        :favored="historyStore.has(c.text)"
        :text-override="c.text.slice(0, typed[i] || 0)"
        :interactive="!streaming"
        @copy="onCopy"
        @swap="onSwap(i)"
        @toggle-fav="onToggleFav"
      />
    </div>

    <div class="empty-cta" v-if="!loading && !copies.length && everGenerated">
      没灵感？
      <a @click="$router.push('/square')">去模板广场 →</a>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import ImageUploader from '../components/ImageUploader.vue'
import TonePills from '../components/TonePills.vue'
import ResultCard from '../components/ResultCard.vue'
import { generate as apiGenerate, listEmotions } from '../api/generate'
import { upsertPersona } from '../api/persona'
import { ApiError } from '../api/client'
import { useToast } from '../stores/toast'
import { useErrorBar } from '../stores/errorBar'
import { historyStore } from '../stores/historyStore'

const text = ref('')
const tones = ref([])
const imageBase64 = ref('')
const templateKey = ref('')

const route = useRoute()

const loading = ref(false)
const streaming = ref(false)   // 流式打字中
const typed = ref([])          // 每条已显示字数
const copies = ref([])
const emotions = ref({
  日常: '#E8590C', 治愈: '#0D9488', 幽默: '#FFB703', 文艺: '#7F77DD',
  带货: '#A8763E', 凡尔赛: '#378ADD', 清新: '#5DCAA5', 情感: '#F2708A',
})

const toast = useToast()
const err = useErrorBar()
const everGenerated = computed(() => copies.value.length > 0)

// 模板预载：从模板广场带 query 跳转过来时，填入示例文案 + 设置模板 key
function applyTemplate(query) {
  if (query && query.example) {
    text.value = String(query.example)
    templateKey.value = String(query.key || '')
    toast.msg.value = `已带入模板：${query.tpl || '通用'}`
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

watch(
  () => route.query,
  (q) => applyTemplate(q),
  { immediate: true },
)

// 进入页面加载情绪色板
onMounted(async () => {
  try {
    const data = await listEmotions()
    if (data && typeof data === 'object') emotions.value = data
  } catch (_) {/* 用 fallback */}
})

function onImageChange({ base64 }) {
  imageBase64.value = base64 || ''
}

// 工具：把服务端回复包一层前端用的颜色 + 稳定 key
function withMeta(list, baseKey = '') {
  return list.map((c, i) => ({
    ...c,
    color: emotions.value[c.emotion] || '#E8590C',
    _key: `${baseKey}-${i}-${c.text.slice(0, 8)}`,
  }))
}

let typeTimer = null
function stopTyping() {
  if (typeTimer) {
    clearInterval(typeTimer)
    typeTimer = null
  }
  streaming.value = false
}

// 流式打字机：3 条文案并行逐字显示，打字期间禁止复制/收藏/换一条
function startTyping() {
  stopTyping()
  streaming.value = true
  typed.value = copies.value.map(() => 0)
  const SPEED = 22 // ms/字，3 条约 1.5~2s 打完
  typeTimer = setInterval(() => {
    let allDone = true
    const next = typed.value.map((n, i) => {
      const len = copies.value[i].text.length
      if (n < len) {
        allDone = false
        return Math.min(len, n + 1)
      }
      return n
    })
    typed.value = next
    if (allDone) stopTyping()
  }, SPEED)
}

async function generate() {
  if (!text.value.trim() && !imageBase64.value) {
    toast.msg.value = '请先上传图片或写一句话'
    return
  }
  stopTyping()
  loading.value = true
  // 保存上一轮结果：请求失败（如限流）时恢复显示，避免页面被清空
  const prevCopies = copies.value
  copies.value = []
  typed.value = []
  err.msg.value = ''

  try {
    const resp = await apiGenerate({
      text: text.value.trim(),
      tones: tones.value,
      imageBase64: imageBase64.value,
      template: templateKey.value || null,
    })
    copies.value = withMeta(resp.copies || [])
    startTyping()
    if (resp.used_persona) {
      toast.msg.value = '已参考你的历史风格 ✨'
    }
  } catch (e) {
    copies.value = prevCopies // 失败恢复旧结果
    handleError(e)
  } finally {
    loading.value = false
  }
}

onUnmounted(() => stopTyping())

function handleError(e) {
  if (!(e instanceof ApiError)) {
    err.msg.value = '生成失败，请重试'
    return
  }
  switch (e.code) {
    case 'EMPTY_INPUT':
      toast.msg.value = '请先上传图片或写一句话'
      break
    case 'INVALID_IMAGE':
      err.msg.value = e.message || '图片格式/大小不符'
      break
    case 'RECOGNITION_FAILED':
      err.msg.value = e.message || '未能识别图片，请换一张更清晰的图'
      break
    case 'MODEL_TIMEOUT':
      err.msg.value = '生成超时，请重试'
      break
    case 'RATE_LIMIT':
      // 限流是轻量打扰，用小 Toast 提示（不占顶部错误条）
      toast.msg.value = e.message || '操作过于频繁，请稍后再试'
      break
    case 'NETWORK_ERROR':
      // 网络异常属轻量打扰，用小 Toast 提示
      toast.msg.value = '网络异常，请重试'
      break
    default:
      err.msg.value = e.message || '生成失败，请重试'
  }
}

async function onCopy(copy) {
  try {
    await navigator.clipboard.writeText(copy.text)
    toast.msg.value = '已复制到剪贴板'
  } catch (_) {
    // 兜底：旧浏览器或非安全上下文
    const ta = document.createElement('textarea')
    ta.value = copy.text
    document.body.appendChild(ta)
    ta.select()
    try { document.execCommand('copy') } catch (_) {}
    document.body.removeChild(ta)
    toast.msg.value = '已复制到剪贴板'
  }
}

// 收藏切换：写入/移出本地收藏，同时把采纳文案回流到人设记忆（失败静默）
function onToggleFav(copy) {
  const t = (copy && copy.text) || ''
  if (!t) return
  if (historyStore.has(t)) {
    const item = historyStore.list().find((i) => i.text === t)
    if (item) historyStore.remove(item.id)
    toast.msg.value = '已取消收藏'
  } else {
    historyStore.add({ text: t, emotion: copy.emotion, style: copy.style })
    toast.msg.value = '已收藏 ⭐'
    upsertPersona({ text: t, emotion: copy.emotion, tone: copy.style })
  }
}

// "换一条"：重新调用 /api/generate，把当前文案作为 swap_text 传给后端，
// 后端会避开它、生成全新内容；前端挑一条与当前不同（尽量同风格）的替换该卡。
const swappingIndex = ref(-1)

async function onSwap(index) {
  if (!copies.value[index]) return
  if (swappingIndex.value >= 0) return // 防连点
  const current = copies.value[index]
  swappingIndex.value = index
  try {
    const resp = await apiGenerate({
      text: text.value.trim(),
      tones: tones.value,
      imageBase64: imageBase64.value,
      template: templateKey.value || null,
      swapText: current.text,
    })
    const fresh = withMeta(resp.copies || [])
    if (fresh.length === 0) {
      toast.msg.value = '暂时没有更多备选文案了'
      return
    }
    // 优先同风格、且文本不同于当前；否则任取一条不同的
    const sameStyle = fresh.find((c) => c.style === current.style && c.text !== current.text)
    const diff = fresh.find((c) => c.text !== current.text)
    const pick = sameStyle || diff || fresh[0]
    if (!pick || pick.text === current.text) {
      toast.msg.value = '暂时没有更多备选文案了'
      return
    }
    const next = [...copies.value]
    next[index] = {
      ...pick,
      color: emotions.value[pick.emotion] || '#E8590C',
      _key: `${Date.now()}-${index}-${pick.text.slice(0, 8)}`,
    }
    copies.value = next
    // 该卡直接显示，不打字动画（其余卡保持）
    const t = [...typed.value]
    t[index] = pick.text.length
    typed.value = t
    toast.msg.value = '已换一条'
  } catch (e) {
    handleError(e)
  } finally {
    swappingIndex.value = -1
  }
}
</script>
