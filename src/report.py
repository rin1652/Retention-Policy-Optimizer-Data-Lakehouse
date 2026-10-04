"""Render contract metrics as a self-contained offline HTML report."""

from __future__ import annotations

import argparse
import csv
import html
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from src.evaluate import config_hash


UTC_PLUS_7 = timezone(timedelta(hours=7))

EM_DASH = "\u2014"
MISSING_COMMENTARY = "Ch\u01b0a c\u00f3 nh\u1eadn x\u00e9t LLM: TASK-09 ch\u01b0a cung c\u1ea5p ph\u1ea3n h\u1ed3i."


def _validated_commentary(
    metrics: dict[str, Any], commentary: dict[str, Any] | None
) -> dict[str, Any]:
    if commentary is None:
        return {"status": "missing", "response": MISSING_COMMENTARY}
    if not isinstance(commentary, dict):
        raise ValueError("LLM commentary must be an object")
    status = commentary.get("status")
    if not isinstance(status, str) or not status:
        raise ValueError("LLM commentary needs a non-empty status")
    response = commentary.get("response")
    if response is not None and not isinstance(response, str):
        raise ValueError("LLM commentary response must be a string or null")
    if commentary.get("run_id") not in (None, metrics.get("run_id")):
        raise ValueError("LLM commentary run_id does not match metrics")
    if status == "success" and not response:
        raise ValueError("successful LLM commentary needs a response")
    return commentary


def _escape(value: Any) -> str:
    return html.escape(str(value))


def _percent(value: float | None) -> str:
    return EM_DASH if value is None else f"{value * 100:.2f}%"


def _bars(policies: dict[str, Any]) -> str:
    colors = ("#2563eb", "#059669", "#d97706", "#7c3aed")
    rows = []
    for index, (policy_id, result) in enumerate(policies.items()):
        coverage = result.get("coverage_total")
        width = 0 if coverage is None else max(0, min(100, coverage * 100))
        rows.append(
            f'<div class="bar-row"><span>{_escape(policy_id)}</span>'
            f'<div class="track"><div class="bar" style="width:{width:.2f}%;'
            f'background:{colors[index % len(colors)]}"></div></div>'
            f'<strong>{_percent(coverage)}</strong></div>'
        )
    return "".join(rows)


def _policy_rows(policies: dict[str, Any]) -> str:
    rows = []
    for policy_id, result in policies.items():
        recoverable = result.get("recoverable")
        count = (
            EM_DASH
            if recoverable is None
            else f"{recoverable}/{result.get('total', 0)}"
        )
        rows.append(
            "<tr>"
            f"<td>{_escape(policy_id)}</td>"
            f"<td>{'H&#7907;p l&#7879;' if result.get('valid') else 'Kh&#244;ng h&#7907;p l&#7879;'}</td>"
            f"<td>{count}</td>"
            f"<td>{_percent(result.get('coverage_total'))}</td>"
            f"<td>{_escape(result.get('cost_gb'))}/{_escape(result.get('budget_gb'))} GB</td>"
            f"<td>{_escape('; '.join(result.get('invalid_reasons', [])) or EM_DASH)}</td>"
            "</tr>"
        )
    return "".join(rows)


def _profile_table(policies: dict[str, Any]) -> str:
    profiles = sorted({
        profile
        for result in policies.values()
        for profile in result.get("coverage_by_profile", {})
    })
    headers = "".join(f"<th>{_escape(policy_id)}</th>" for policy_id in policies)
    rows = "".join(
        "<tr>"
        f"<td>{_escape(profile)}</td>"
        + "".join(
            f"<td>{_percent(result.get('coverage_by_profile', {}).get(profile))}</td>"
            for result in policies.values()
        )
        + "</tr>"
        for profile in profiles
    )
    return f"<table><thead><tr><th>Profile</th>{headers}</tr></thead><tbody>{rows}</tbody></table>"


def render_report(
    metrics: dict[str, Any], commentary: dict[str, Any] | None = None, has_config: bool = False
) -> str:
    policies = metrics.get("policies", {})
    commentary = _validated_commentary(metrics, commentary)
    paired = metrics.get("paired", {})
    delta = paired.get("delta_pp")
    delta_text = "\u2014" if delta is None else f"{delta:+.2f} \u0111i\u1ec3m ph\u1ea7n tr\u0103m"
    ttl_json = json.dumps(
        {policy_id: result.get("ttl_days", {}) for policy_id, result in policies.items()},
        ensure_ascii=False,
        indent=2,
    )
    failures = "".join(
        f"<li>{_escape(item)}</li>" for item in metrics.get("failure_cases", [])
    ) or "<li>Ch&#432;a ghi nh&#7853;n.</li>"
    status_class = "ok" if metrics.get("status") == "valid" else "bad"
    invalid_reasons = "".join(
        f"<li>{_escape(item)}</li>" for item in metrics.get("invalid_reasons", [])
    ) or f"<li>{EM_DASH}</li>"
    artifacts = ["metrics.json", "results.csv", "llm_commentary.json"]
    if has_config:
        artifacts.append("config.json")
    artifact_text = ", ".join(f"<code>{name}</code>" for name in artifacts)

    generated = datetime.now(UTC_PLUS_7).isoformat(timespec="seconds")
    fixture_note = (
        "<p><strong>FIXTURE DATA - NOT EXPERIMENT RESULTS</strong></p>"
        if str(metrics.get("run_id", "")).startswith("fixture-") else ""
    )
    return f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Retention evaluation {_escape(metrics.get('run_id', ''))}</title>
<style>
body{{font:15px system-ui,sans-serif;max-width:1080px;margin:32px auto;padding:0 18px;color:#172033;background:#f8fafc}}
h1,h2{{color:#0f172a}}section{{background:#fff;padding:18px;margin:16px 0;border:1px solid #dbe3ee;border-radius:10px}}
table{{width:100%;border-collapse:collapse}}th,td{{padding:9px;border-bottom:1px solid #e2e8f0;text-align:left}}th{{background:#f1f5f9}}
code,pre{{background:#f1f5f9;border-radius:6px}}pre{{padding:12px;overflow:auto}}.muted{{color:#64748b}}
.badge{{display:inline-block;padding:4px 9px;border-radius:999px;color:#fff}}.ok{{background:#047857}}.bad{{background:#b91c1c}}
.bar-row{{display:grid;grid-template-columns:220px 1fr 70px;gap:10px;align-items:center;margin:10px 0}}
.track{{height:18px;background:#e2e8f0;border-radius:9px;overflow:hidden}}.bar{{height:100%}}
@media(max-width:700px){{.bar-row{{grid-template-columns:100px 1fr 60px}}table{{font-size:13px}}}}
</style></head><body>
<h1>Retention Policy Evaluation</h1>
{fixture_note}
<p><span class="badge {status_class}">{_escape(metrics.get('status', 'unknown'))}</span></p>
<section><h2>Validation</h2><ul>{invalid_reasons}</ul></section>
<section><h2>Th&#244;ng tin l&#7847;n ch&#7841;y</h2><p>
<b>Run ID:</b> {_escape(metrics.get('run_id'))}<br>
<b>Th&#7901;i gian t&#7841;o report (UTC+7):</b> {_escape(generated)}<br>
<b>Config hash:</b> <code>{_escape(metrics.get('config_hash'))}</code><br>
<b>Split / scenario / seed:</b> {_escape(metrics.get('split'))} / {_escape(metrics.get('scenario'))} / {_escape(metrics.get('seed'))}<br>
<b>Incident / profile:</b> {_escape(metrics.get('incident_count'))} / {_escape(metrics.get('profile_count'))}</p>
<p class="muted">{_escape(metrics.get('model_assumption'))}</p></section>
<section><h2>K&#7871;t qu&#7843; ch&#237;nh</h2><table><thead><tr><th>Policy</th><th>Tr&#7841;ng th&#225;i</th><th>Recoverable</th><th>Coverage</th><th>Cost / budget</th><th>Violations</th></tr></thead>
<tbody>{_policy_rows(policies)}</tbody></table><p><b>Ch&#234;nh l&#7879;ch coverage:</b> {_escape(delta_text)}</p>{_bars(policies)}</section>
<section><h2>Coverage theo profile</h2>{_profile_table(policies)}</section>
<section><h2>TTL</h2><pre>{_escape(ttl_json)}</pre></section>
<section><h2>Nh&#7853;n x&#233;t LLM</h2><p><b>Tr&#7841;ng th&#225;i:</b> {_escape(commentary.get('status', 'missing'))}</p>
<p>{_escape(commentary.get('response') or MISSING_COMMENTARY)}</p><p class="muted">Model: {_escape(commentary.get('model', EM_DASH))}</p></section>
<section><h2>Failure case v&#224; gi&#7899;i h&#7841;n</h2><ul>{failures}</ul></section>
<section><h2>T&#225;i l&#7853;p</h2><p>D&#7919; li&#7879;u k&#232;m theo: {artifact_text}.</p></section>
</body></html>"""


def write_report(
    metrics: dict[str, Any],
    output_root: Path,
    commentary: dict[str, Any] | None = None,
    config: dict[str, Any] | None = None,
) -> Path:
    run_id = metrics.get("run_id")
    if not isinstance(run_id, str) or not run_id or run_id in {".", ".."} or Path(run_id).name != run_id:
        raise ValueError("run_id must be a safe, non-empty directory name")
    commentary = _validated_commentary(metrics, commentary)
    if config is not None:
        if not isinstance(config, dict):
            raise ValueError("config must be an object")
        if config_hash(config) != metrics.get("config_hash"):
            raise ValueError("config hash does not match metrics")

    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (run_dir / "llm_commentary.json").write_text(
        json.dumps(commentary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if config is not None:
        (run_dir / "config.json").write_text(
            json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    with (run_dir / "results.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "run_id", "split", "scenario", "seed", "policy_id", "valid",
            "recoverable", "total", "coverage_total", "coverage_logical_only",
            "coverage_infra_loss", "cost_gb", "budget_gb", "budget_remaining_gb",
            "budget_violations", "min_ttl_violations", "grid_violations",
            "ttl_days", "coverage_by_profile", "invalid_reasons",
        ])
        for policy_id, result in metrics.get("policies", {}).items():
            writer.writerow([
                run_id,
                metrics.get("split"),
                metrics.get("scenario"),
                metrics.get("seed"),
                policy_id,
                result.get("valid"),
                result.get("recoverable"),
                result.get("total"),
                result.get("coverage_total"),
                result.get("coverage_logical_only"),
                result.get("coverage_infra_loss"),
                result.get("cost_gb"),
                result.get("budget_gb"),
                result.get("budget_remaining_gb"),
                result.get("budget_violations"),
                result.get("min_ttl_violations"),
                result.get("grid_violations"),
                json.dumps(result.get("ttl_days", {}), ensure_ascii=False, sort_keys=True),
                json.dumps(
                    result.get("coverage_by_profile", {}),
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                "; ".join(result.get("invalid_reasons", [])),
            ])
    report_path = run_dir / "report.html"
    report_path.write_text(render_report(metrics, commentary, config is not None), encoding="utf-8")
    return report_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render metrics as an offline HTML report")
    parser.add_argument("metrics", type=Path)
    parser.add_argument("--output-root", type=Path, default=Path("reports"))
    parser.add_argument("--llm-commentary", type=Path)
    parser.add_argument("--config", type=Path)
    args = parser.parse_args()
    metrics = json.loads(args.metrics.read_text(encoding="utf-8"))
    commentary = (
        json.loads(args.llm_commentary.read_text(encoding="utf-8"))
        if args.llm_commentary else None
    )
    config = (
        json.loads(args.config.read_text(encoding="utf-8")) if args.config else None
    )
    print(write_report(metrics, args.output_root, commentary, config))


if __name__ == "__main__":
    main()
