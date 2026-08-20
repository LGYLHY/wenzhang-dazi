<template>
  <article class="card card-hover result-card">
    <div class="strip" :style="{ background: color }" />
    <div class="body">
      <div class="meta">
        <span class="pill" :style="pillStyle">{{ emotionLabel }}</span>
        <span class="field-hint" v-if="styleLabel">· {{ styleLabel }}</span>
      </div>
      <div class="text">{{ textOverride || copy.text }}</div>
      <div class="actions">
        <button class="act copy" :disabled="!interactive" @click="$emit('copy', copy)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="9" y="9" width="13" height="13" rx="2" />
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
          </svg>
          复制
        </button>
        <button class="act fav" :class="{ on: favored }" :disabled="!interactive" @click="$emit('toggle-fav', copy)">
          <svg viewBox="0 0 24 24" :fill="favored ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
          </svg>
          {{ favored ? '已收藏' : '收藏' }}
        </button>
        <button class="act swap spacer" :disabled="!interactive" @click="$emit('swap', copy)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="17 1 21 5 17 9" />
            <path d="M3 11V9a4 4 0 0 1 4-4h14" />
            <polyline points="7 23 3 19 7 15" />
            <path d="M21 13v2a4 4 0 0 1-4 4H3" />
          </svg>
          换一条
        </button>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  copy: { type: Object, required: true },     // { style, emotion, text }
  color: { type: String, default: '#E8590C' },
  emotionLabel: { type: String, default: '' },
  styleLabel: { type: String, default: '' },
  favored: { type: Boolean, default: false },
  textOverride: { type: String, default: '' }, // 流式打字中覆盖全文显示
  interactive: { type: Boolean, default: true },
})
defineEmits(['copy', 'swap', 'toggle-fav'])

const pillStyle = computed(() => ({
  color: props.color,
  background: hexToRgba(props.color, 0.14),
}))

function hexToRgba(hex, alpha) {
  const m = /^#?([0-9a-f]{6})$/i.exec(hex)
  if (!m) return `rgba(0,0,0,${alpha})`
  const n = parseInt(m[1], 16)
  const r = (n >> 16) & 255
  const g = (n >> 8) & 255
  const b = n & 255
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}
</script>
