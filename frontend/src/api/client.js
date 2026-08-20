/**
 * apiClient：fetch 封装 + 统一错误信封 {code, message}
 *
 * - 200: 正常返回 data
 * - 4xx/5xx: 抛出 { code, message, http }，调用方按 code 分支
 * - 断网：抛出 NETWORK_ERROR
 */
const DEFAULTS = {
  timeout: 8000,
  headers: { 'Content-Type': 'application/json' },
}

export class ApiError extends Error {
  constructor({ code, message, http = 0 }) {
    super(message)
    this.code = code
    this.http = http
  }
}

async function request(path, { method = 'GET', body, timeout, headers } = {}) {
  const ctrl = new AbortController()
  const t = setTimeout(() => ctrl.abort(), timeout || DEFAULTS.timeout)
  try {
    const resp = await fetch(path, {
      method,
      signal: ctrl.signal,
      headers: { ...DEFAULTS.headers, ...(headers || {}) },
      body: body ? JSON.stringify(body) : undefined,
    })
    clearTimeout(t)

    if (!resp.ok) {
      let payload = null
      try { payload = await resp.json() } catch (_) {}
      const detail = payload && (payload.detail || payload)
      const code = (detail && detail.code) || `HTTP_${resp.status}`
      const message = (detail && detail.message) || resp.statusText || '请求失败'
      throw new ApiError({ code, message, http: resp.status })
    }
    return await resp.json()
  } catch (e) {
    clearTimeout(t)
    if (e instanceof ApiError) throw e
    if (e.name === 'AbortError') {
      throw new ApiError({ code: 'NETWORK_ERROR', message: '网络异常，请重试' })
    }
    throw new ApiError({ code: 'NETWORK_ERROR', message: '网络异常，请检查网络' })
  }
}

export const api = {
  get: (path, opt) => request(path, { ...opt, method: 'GET' }),
  post: (path, body, opt) => request(path, { ...opt, method: 'POST', body }),
}
