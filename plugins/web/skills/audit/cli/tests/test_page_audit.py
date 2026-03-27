"""Regression coverage for stateful interaction audits."""

from __future__ import annotations

from audit_cli.crawl.page import (
    ViewportSpec,
    _probe_home_logo_behavior,
    _probe_modal_backdrop,
    audit_page,
)
from audit_cli.drive.browser import BrowserDriverError
from audit_cli.crawl.queue import CrawlQueue
from audit_cli.types import InteractionCandidate, InteractionPlan


class _FakeDriver:
    def __init__(self) -> None:
        self.calls: list[tuple[object, ...]] = []

    def resize(self, width: int, height: int) -> None:
        self.calls.append(("resize", width, height))

    def navigate(self, url: str) -> None:
        self.calls.append(("navigate", url))

    def wait_for_fn(self, expression: str, *, timeout_ms: int = 3000) -> None:
        self.calls.append(("wait_for_fn", expression, timeout_ms))

    def snapshot(self) -> dict[str, object]:
        self.calls.append(("snapshot",))
        return {"refs": {"e4": {"name": "Open navigation menu", "role": "button"}}}

    def get_url(self) -> str:
        self.calls.append(("get_url",))
        return "http://127.0.0.1:3200/"

    def click(self, uid: int) -> None:
        self.calls.append(("click", uid))

    def hover(self, target: int | str) -> None:
        self.calls.append(("hover", target))

    def evaluate(self, expression: str) -> _EvalResult:
        self.calls.append(("evaluate", expression))
        return _EvalResult(
            '[{"result":{"result":"false"},"success":true,"error":null}]'
        )


class _EvalResult:
    def __init__(self, stdout: str) -> None:
        self.stdout = stdout


class _ModalDriver(_FakeDriver):
    def evaluate(self, expression: str) -> _EvalResult:
        self.calls.append(("evaluate", expression))
        return _EvalResult(
            '[{"result":{"result":"false"},"success":true,"error":null}]'
        )


class _TruthyEvalDriver(_FakeDriver):
    def evaluate(self, expression: str) -> _EvalResult:
        self.calls.append(("evaluate", expression))
        return _EvalResult(
            '[{"result":{"result":"true"},"success":true,"error":null}]'
        )


class _LogoProbeDriver(_FakeDriver):
    def __init__(self, *, fail_wait: bool) -> None:
        super().__init__()
        self.fail_wait = fail_wait
        self._evaluate_count = 0

    def evaluate(self, expression: str) -> _EvalResult:
        self.calls.append(("evaluate", expression))
        self._evaluate_count += 1
        if self._evaluate_count == 1:
            return _EvalResult(
                '[{"result":{"result":"true"},"success":true,"error":null}]'
            )
        if self._evaluate_count == 2:
            return _EvalResult(
                '[{"result":{"result":"240"},"success":true,"error":null}]'
            )
        return _EvalResult(
            '[{"result":{"result":"true"},"success":true,"error":null}]'
        )

    def wait_for_fn(self, expression: str, *, timeout_ms: int = 3000) -> None:
        self.calls.append(("wait_for_fn", expression, timeout_ms))
        if self.fail_wait and "scrollY" in expression:
            raise BrowserDriverError("scroll did not return to top")


def test_audit_page_clears_hover_before_follow_up_audit(
    monkeypatch,
) -> None:
    from audit_cli.crawl import page as page_module

    driver = _FakeDriver()
    queue = CrawlQueue(origin="http://127.0.0.1:3200")
    viewport = ViewportSpec(
        label="Mobile 390x844",
        kind="mobile",
        width=390,
        height=844,
    )
    inject_calls = 0

    def fake_inject_and_run(*args, **kwargs):
        nonlocal inject_calls
        inject_calls += 1
        if inject_calls == 2:
            click_index = driver.calls.index(("click", 4))
            hover_index = driver.calls.index(("hover", "body"))
            assert hover_index > click_index
        return {"categories": {"text": {"issues": []}}}

    monkeypatch.setattr(page_module, "inject_and_run", fake_inject_and_run)
    monkeypatch.setattr(page_module, "_collect_anchor_hrefs", lambda _driver: [])
    monkeypatch.setattr(
        page_module,
        "discover_interactions",
        lambda snapshot, opts: InteractionPlan(
            candidates=(
                InteractionCandidate(
                    uid=4,
                    role="button",
                    name="Open navigation menu",
                    fingerprint="menu-button",
                ),
            ),
            cross_origin_candidates=(),
            dropped_social=(),
        ),
    )
    monkeypatch.setattr(page_module, "_count_visible_modals", lambda _driver: 0)
    monkeypatch.setattr(page_module, "_dismiss", lambda _driver: None)
    monkeypatch.setattr(page_module, "discover_hover_targets", lambda snapshot: ())
    monkeypatch.setattr(page_module, "_run_hover_pass", lambda _driver, _targets: [])

    audit_page(
        driver,
        server=object(),
        queue=queue,
        url="http://127.0.0.1:3200/",
        viewports=(viewport,),
        all_pages=False,
        same_origin_host="127.0.0.1:3200",
    )

    assert ("hover", "body") in driver.calls


def test_audit_page_reports_missing_modal_backdrop_blur(monkeypatch) -> None:
    from audit_cli.crawl import page as page_module

    driver = _ModalDriver()
    queue = CrawlQueue(origin="http://127.0.0.1:3200")
    viewport = ViewportSpec(
        label="Mobile 390x844",
        kind="mobile",
        width=390,
        height=844,
    )
    modal_counts = iter((0, 1))

    monkeypatch.setattr(
        page_module,
        "inject_and_run",
        lambda *args, **kwargs: {"categories": {"interaction": {"issues": []}}},
    )
    monkeypatch.setattr(page_module, "_collect_anchor_hrefs", lambda _driver: [])
    monkeypatch.setattr(
        page_module,
        "discover_interactions",
        lambda snapshot, opts: InteractionPlan(
            candidates=(
                InteractionCandidate(
                    uid=4,
                    role="button",
                    name="Open navigation menu",
                    fingerprint="menu-button",
                ),
            ),
            cross_origin_candidates=(),
            dropped_social=(),
        ),
    )
    monkeypatch.setattr(
        page_module, "_count_visible_modals", lambda _driver: next(modal_counts)
    )
    monkeypatch.setattr(page_module, "_run_modal_audit", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        page_module, "_probe_escape_dismissal", lambda *args, **kwargs: []
    )
    monkeypatch.setattr(page_module, "_dismiss", lambda _driver: None)
    monkeypatch.setattr(page_module, "discover_hover_targets", lambda snapshot: ())
    monkeypatch.setattr(page_module, "_run_hover_pass", lambda _driver, _targets: [])

    result = audit_page(
        driver,
        server=object(),
        queue=queue,
        url="http://127.0.0.1:3200/",
        viewports=(viewport,),
        all_pages=False,
        same_origin_host="127.0.0.1:3200",
    )

    assert any(
        issue.get("ruleId") == "DES-MODA-04" for issue in result.modal_findings
    )


def test_probe_modal_backdrop_accepts_visible_blurred_overlay() -> None:
    driver = _TruthyEvalDriver()

    issues = _probe_modal_backdrop(driver, selector_hint="modal@e4")

    assert issues == []


def test_probe_home_logo_behavior_reports_missing_scroll_to_top() -> None:
    driver = _LogoProbeDriver(fail_wait=True)

    issues = _probe_home_logo_behavior(
        driver,
        current_url="http://127.0.0.1:3200/",
        selector_hint="header-home-link",
    )

    assert any(issue.get("ruleId") == "DES-NAVI-04" for issue in issues)
