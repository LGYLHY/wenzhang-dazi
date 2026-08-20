import { api } from './client'
import { getDeviceId } from '../stores/deviceId'

/**
 * 调生成接口：真实 LLM 生成 3 条文案通常 3~10s，前端放宽到 16s
 * （后端 15s 超时 + 1s 余量）
 */
export function generate({ text, tones, imageBase64, template, swapText }) {
  return api.post(
    '/api/generate',
    {
      text: text || '',
      tones: tones || [],
      image_base64: imageBase64 || null,
      template: template || null,
      swap_text: swapText || null,
      device_id: getDeviceId(),
    },
    { timeout: 16000 },
  )
}

export function listEmotions() {
  return api.get('/api/emotions')
}
