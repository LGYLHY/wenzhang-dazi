import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import './assets/styles/tokens.css'
import './assets/styles/layout.css'
import './assets/styles/components.css'

createApp(App).use(router).mount('#app')
