<template>
  <div class="uploader">
    <button class="upload" @click="picker.click()" :disabled="disabled">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
        <polyline points="17 8 12 3 7 8" />
        <line x1="12" y1="3" x2="12" y2="15" />
      </svg>
      {{ previewUrl ? '更换图片' : '上传图片' }}
    </button>
    <input
      ref="picker"
      type="file"
      accept="image/jpeg,image/jpg,image/png,image/webp"
      hidden
      @change="onPick"
    />
    <div class="thumb" :class="{ show: !!previewUrl }">
      <img v-if="previewUrl" :src="previewUrl" alt="待生成图片" />
      <span class="x" @click="remove">×</span>
    </div>
    <span class="field-hint">可选 · 支持 JPG/PNG/WEBP · ≤10MB</span>
    <span class="field-error" v-if="errorMsg">{{ errorMsg }}</span>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['change'])
const props = defineProps({
  disabled: { type: Boolean, default: false },
})

const picker = ref(null)
const previewUrl = ref('')
const errorMsg = ref('')

const ALLOWED = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
const MAX = 10 * 1024 * 1024

function reset() {
  errorMsg.value = ''
  if (picker.value) picker.value.value = ''
}

function onPick(ev) {
  const f = ev.target.files && ev.target.files[0]
  if (!f) return
  errorMsg.value = ''
  if (!ALLOWED.includes(f.type)) {
    errorMsg.value = '仅支持 JPG/PNG/WEBP 格式'
    reset()
    return
  }
  if (f.size > MAX) {
    errorMsg.value = '图片超过 10MB，请压缩后重试'
    reset()
    return
  }
  const reader = new FileReader()
  reader.onload = () => {
    previewUrl.value = String(reader.result)
    emit('change', { base64: previewUrl.value, file: f })
  }
  reader.onerror = () => {
    errorMsg.value = '图片读取失败，请重试'
  }
  reader.readAsDataURL(f)
}

function remove() {
  previewUrl.value = ''
  if (picker.value) picker.value.value = ''
  emit('change', { base64: '', file: null })
}
</script>

<style scoped>
.uploader { display: flex; align-items: center; gap: var(--sp-md); flex-wrap: wrap; }
</style>
