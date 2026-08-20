import { createRouter, createWebHashHistory } from 'vue-router'

import GenerateView from './views/GenerateView.vue'

const routes = [
  { path: '/', redirect: '/generate' },
  { path: '/generate', name: 'generate', component: GenerateView },
  // M2：我的收藏
  {
    path: '/favorites',
    name: 'favorites',
    component: () => import('./views/CollectionView.vue'),
  },
  // M3：模板广场 / AI 润色 / 帮助中心
  {
    path: '/square',
    name: 'square',
    component: () => import('./views/TemplateSquareView.vue'),
  },
  {
    path: '/polish',
    name: 'polish',
    component: () => import('./views/PolishView.vue'),
  },
  {
    path: '/help',
    name: 'help',
    component: () => import('./views/HelpView.vue'),
  },
]

export default createRouter({
  history: createWebHashHistory(),
  routes,
})
