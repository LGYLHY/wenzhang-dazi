<template>
  <section>
    <div class="page-head">
      <h2>帮助中心</h2>
      <p>使用说明与隐私说明</p>
    </div>

    <div class="help-grid">
      <!-- 左侧导航 -->
      <nav class="help-nav">
        <button
          v-for="tab in TABS"
          :key="tab.key"
          class="g"
          :class="{ on: active === tab.key }"
          @click="active = tab.key"
        >{{ tab.label }}</button>
      </nav>

      <!-- 右侧内容 -->
      <div class="help-content" v-html="CONTENT[active]"></div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'

const TABS = [
  { key: 'use', label: '使用说明' },
  { key: 'privacy', label: '隐私说明' },
  { key: 'faq', label: '常见问题' },
]
const active = ref('use')

const CONTENT = {
  use: `
    <h3>使用说明</h3>
    <p>文案搭子帮你把图片和心情，变成能直接发朋友圈的文案。</p>
    <ul>
      <li>在生成页输入心情或上传图片，选 1–多个语气，点「生成文案」。</li>
      <li>AI 会给出 3–5 条不同风格候选，每条带情绪色条，一眼区分氛围。</li>
      <li>点「复制」直接进剪贴板；点「收藏」星标存入我的收藏；点「换一条」重新生成该条。</li>
      <li>没灵感时去模板广场，按场景挑一个一键带入生成页。</li>
      <li>写好的文案也能贴到 AI 润色，切换「更文艺 / 更简短 / 加 emoji」。</li>
    </ul>
    <div class="note">提示：微信暂未开放自动发布，文案需手动复制后粘贴到朋友圈。</div>`,
  privacy: `
    <h3>隐私说明</h3>
    <p>我们重视你的隐私，遵循《个人信息保护法》（PIPL）设计：</p>
    <ul>
      <li><b>本地优先</b>：历史文案与收藏默认存储在你的浏览器本地（localStorage）。</li>
      <li><b>图片处理</b>：上传图片仅用于本次识别生成，不上云留存。</li>
      <li><b>人脸数据</b>：不采集、不留存任何人脸信息。</li>
      <li><b>不二次训练</b>：除非你明确同意，你的内容不会用于模型训练。</li>
    </ul>
    <div class="note">如你希望清除全部本地数据，可在浏览器设置中清除本站存储。</div>`,
  faq: `
    <h3>常见问题</h3>
    <ul>
      <li><b>生成的文案能直接发到朋友圈吗？</b><br/>目前微信未开放发布接口，需复制后手动粘贴。</li>
      <li><b>为什么有时风格偏雷同？</b><br/>开启「人设记忆」后，AI 会参考你历史偏好，越用越像你。</li>
      <li><b>图片太大传不上？</b><br/>单张请控制在 10MB 以内，建议 JPG/PNG/WEBP。</li>
    </ul>`,
}
</script>

<style scoped>
.page-head h2 { font-size: 20px; font-weight: 600; }
.page-head p { color: var(--c-text-2); font-size: 14px; margin-top: 4px; }

.help-grid {
  display: grid; grid-template-columns: 220px 1fr;
  gap: var(--sp-2xl); align-items: start; margin-top: var(--sp-xl);
}
.help-nav { position: sticky; top: 88px; display: flex; flex-direction: column; gap: 4px; }
.help-nav .g {
  padding: 10px 14px; border-radius: var(--radius-control);
  color: var(--c-text-2); font-size: 14px; font-weight: 600;
  text-align: left; transition: 0.15s;
}
.help-nav .g:hover { background: rgba(232, 89, 12, 0.06); color: var(--c-text-1); }
.help-nav .g.on { background: var(--c-primary); color: #fff; }

.help-content :deep(h3) { font-size: 18px; font-weight: 600; margin-bottom: var(--sp-md); }
.help-content :deep(p) { color: var(--c-text-2); margin-bottom: var(--sp-md); }
.help-content :deep(ul) {
  color: var(--c-text-2); padding-left: 20px;
  display: flex; flex-direction: column; gap: 6px; margin-bottom: var(--sp-md);
}
.help-content :deep(.note) {
  background: rgba(13, 148, 136, 0.08); border-left: 3px solid var(--c-secondary);
  padding: var(--sp-md) var(--sp-lg); border-radius: 8px;
  color: var(--c-text-1); font-size: 14px;
}

@media (max-width: 768px) {
  .help-grid { grid-template-columns: 1fr; gap: var(--sp-lg); }
  .help-nav { position: static; flex-direction: row; overflow-x: auto; padding-bottom: 4px; }
  .help-nav .g { white-space: nowrap; flex: none; }
}
@media (min-width: 769px) and (max-width: 1199px) {
  .help-grid { grid-template-columns: 200px 1fr; }
}
</style>
