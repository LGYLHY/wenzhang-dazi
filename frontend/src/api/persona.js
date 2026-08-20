import { api } from './client'
import { getDeviceId } from '../stores/deviceId'

/**
 * 采纳回流：用户收藏/复制的文案写入向量库（仅文本，不含图片/人脸）
 * 失败静默忽略，不影响主流程（本地收藏仍成功）。
 */
export async function upsertPersona({ text, emotion = '日常', tone = '日常' }) {
  try {
    return await api.post('/api/persona/upsert', {
      device_id: getDeviceId(),
      text,
      emotion,
      tone,
    })
  } catch (_) {
    return null
  }
}
