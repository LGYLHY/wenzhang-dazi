"""M0+M1 阶段前端 smoke / 单测：覆盖输入校验、复制、骨架屏。"""
import json


def _set_v_model(page, selector, value):
    page.eval_on_selector(
        selector,
        '(el, v) => { const t = Object.getOwnPropertyDescriptor(el.__proto__, "value").set; t.call(el, v); el.dispatchEvent(new Event("input", { bubbles: true })); }',
        value,
    )


def test_page_renders(serve_app):
    page = serve_app.goto("/")
    page.wait_for_selector("textarea", timeout=5000)
    assert page.is_visible("textarea")
    assert page.is_visible("button.btn-primary")


def test_empty_submit_shows_toast(serve_app):
    page = serve_app.goto("/#/generate")
    page.wait_for_selector("textarea")
    # 主按钮在空提交时应禁用
    btn = page.query_selector("button.btn-primary")
    assert btn.get_attribute("disabled") is not None


def test_type_text_and_enable_button(serve_app):
    page = serve_app.goto("/#/generate")
    page.wait_for_selector("textarea")
    _set_v_model(page, "textarea", "海边")
    # 等 v-model 同步
    page.wait_for_function("document.querySelector('textarea').value === '海边'")
    btn = page.query_selector("button.btn-primary")
    assert btn.get_attribute("disabled") is None


def test_click_generate_triggers_request(serve_app):
    page = serve_app.goto("/#/generate")
    page.wait_for_selector("textarea")
    _set_v_model(page, "textarea", "海边")
    page.click("button.btn-primary")
    # 骨架屏应出现
    page.wait_for_selector(".skeleton.show", timeout=2000)
    # 结果出现（M1 mock 也能在 1~3s 内返回）
    page.wait_for_selector(".result-card", timeout=6000)


def test_copy_button(serve_app):
    page = serve_app.goto("/#/generate")
    page.wait_for_selector("textarea")
    _set_v_model(page, "textarea", "海边")
    page.click("button.btn-primary")
    page.wait_for_selector(".result-card", timeout=6000)
    page.evaluate("() => navigator.clipboard.writeText = async () => {}")  # mock
    page.click(".result-card .act.copy")
    # 出现 toast
    page.wait_for_selector(".toast.show", timeout=2000)
