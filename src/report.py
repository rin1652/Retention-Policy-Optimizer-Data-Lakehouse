import os
import json
import uuid
import datetime
import hashlib
from jinja2 import Environment, FileSystemLoader
from src.llm_commentary import generate_commentary

def generate_run_id(config_hash: str) -> str:
    # {YYYYMMDD}T{HHMMSS}-{config_hash8}-{uuid4_hex}, giờ UTC+7
    tz = datetime.timezone(datetime.timedelta(hours=7))
    now = datetime.datetime.now(tz)
    ts = now.strftime("%Y%m%dT%H%M%S")
    hash8 = config_hash[:8] if config_hash else "nohash00"
    uid = uuid.uuid4().hex
    return f"{ts}-{hash8}-{uid}"

def compute_config_hash(config: dict) -> str:
    # SHA-256 của JSON chuẩn tắc UTF-8
    config_copy = json.loads(json.dumps(config))
    if "meta" in config_copy:
        config_copy["meta"].pop("status", None)
        config_copy["meta"].pop("note", None)
    
    canon_json = json.dumps(config_copy, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canon_json.encode('utf-8')).hexdigest()

def create_report_directory(run_id: str) -> str:
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    run_dir = os.path.join(reports_dir, run_id)
    try:
        os.makedirs(run_dir, exist_ok=False)
        return run_dir
    except FileExistsError:
        # Nếu trùng UUID, sinh lại UUID mới
        return create_report_directory(run_id.rsplit('-', 1)[0] + "-" + uuid.uuid4().hex)

def export_report(config: dict, metrics: dict, policies: dict):
    """
    Render metrics JSON thành report HTML, lưu báo cáo và JSON vào reports/<run_id>/
    """
    config_hash = compute_config_hash(config)
    run_id = generate_run_id(config_hash)
    
    run_dir = create_report_directory(run_id)
    
    # Bổ sung policy details vào metrics
    enriched_policies = {}
    for pid, m in metrics.get("policies", {}).items():
        pol = policies.get(pid, {})
        m_copy = dict(m)
        m_copy["kind"] = pol.get("kind", "unknown")
        m_copy["ttl_days"] = pol.get("ttl_days", {})
        enriched_policies[pid] = m_copy
        
    metrics["policies"] = enriched_policies
    metrics["run_id"] = run_id
    metrics["config_hash"] = config_hash
    
    # Gọi LLM (TASK-09)
    llm_result = generate_commentary(metrics, run_id)
    metrics["llm_commentary"] = llm_result
    
    # Render HTML (TASK-10)
    env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
    template = env.get_template('report.html')
    
    tz = datetime.timezone(datetime.timedelta(hours=7))
    timestamp_str = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    
    budget_gb = config.get("budget", {}).get("main_gb", "N/A")
    if "budget_gb" in metrics:
        budget_gb = metrics["budget_gb"]
        
    html_content = template.render(
        run_id=run_id,
        timestamp=timestamp_str,
        status=metrics.get("status", "unknown"),
        budget_gb=budget_gb,
        llm_status=llm_result["status"],
        llm_response=llm_result["response"],
        llm_error=llm_result["error_message"],
        llm_model=llm_result["model"],
        policies=enriched_policies,
        paired_delta_pp=metrics.get("paired", {}).get("delta_pp", {}),
        failure_cases=metrics.get("failure_cases", [])
    )
    
    # Ghi file
    html_path = os.path.join(run_dir, "report.html")
    json_path = os.path.join(run_dir, "metrics.json")
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
        
    return run_id, html_path, json_path
