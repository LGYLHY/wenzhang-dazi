/**
 * 顶部错误条：用于网络异常、生成失败等需要"用户能再次看到"的提示。
 * 不同于 Toast：会持续 4s 或等待用户手动关闭。
 */
import { ref } from 'vue'

const msg = ref('')

export function useErrorBar() {
  return { msg }
}
