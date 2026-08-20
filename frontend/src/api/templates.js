import { api } from './client'

export function listTemplates(category = 'all') {
  return api.get(`/api/templates?category=${encodeURIComponent(category)}`)
}
