<template>
  <div class="tones">
    <button
      v-for="t in options"
      :key="t"
      class="tone"
      :class="{ on: props.modelValue.includes(t) }"
      @click="toggle(t)"
    >{{ t }}</button>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  options: { type: Array, default: () => ['文艺', '幽默', '带货', '日常', '治愈', '凡尔赛'] },
})
const emit = defineEmits(['update:modelValue'])

function toggle(t) {
  const next = props.modelValue.includes(t)
    ? props.modelValue.filter((x) => x !== t)
    : [...props.modelValue, t]
  emit('update:modelValue', next)
}
</script>
