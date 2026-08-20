/**
 * deviceId：MVP 不引入登录，用 localStorage 存的随机 ID 区分用户。
 * 符合 PIPL "数据最小化、避免 PII"。
 */
const KEY = 'wenzhang_dazi_device_id'

function uuid() {
  return 'd-' + Math.random().toString(36).slice(2, 10) + Date.now().toString(36)
}

export function getDeviceId() {
  let id = localStorage.getItem(KEY)
  if (!id) {
    id = uuid()
    localStorage.setItem(KEY, id)
  }
  return id
}
