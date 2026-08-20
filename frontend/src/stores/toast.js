/**
 * 全局 Toast：组件处 toast(msg) 即可在底部弹出 1.6s 的气泡。
 * 用 ref + watch 实现，避免引入额外依赖。
 */
import { ref } from 'vue'

const msg = ref('')

export function useToast() {
  return { msg }
}
