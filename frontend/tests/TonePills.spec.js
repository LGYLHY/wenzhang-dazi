// 简单的 Vitest 单元测试：TonePills 多选逻辑
// 待 M2+M3 阶段补足 ResultCard.vue 与 GenerateView.vue 的单测。
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TonePills from '../src/components/TonePills.vue'

describe('TonePills', () => {
  it('多选切换', async () => {
    const wrapper = mount(TonePills, { props: { modelValue: [] } })
    await wrapper.findAll('button')[0].trigger('click')
    expect(wrapper.emitted('update:modelValue')[0][0]).toEqual(['文艺'])
    await wrapper.setProps({ modelValue: ['文艺'] })
    await wrapper.findAll('button')[0].trigger('click')
    expect(wrapper.emitted('update:modelValue')[1][0]).toEqual([])
  })
})
