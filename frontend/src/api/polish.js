import { api } from './client'
import { getDeviceId } from '../stores/deviceId'

export function polish({ text, mode }) {
  return api.post(
    '/api/polish',
    {
      text,
      mode,
      device_id: getDeviceId(),
    },
    { timeout: 15000 },
  )
}
