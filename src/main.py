import json
import os
import sys
from src.generator import generate_incidents
from src.policies_optimizer import get_baseline_policy, optimize_policy
from src.evaluate import evaluate_policy
from src.report import export_report

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "experiment.sample.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    budget_gb = config.get("budget", {}).get("main_gb", 810)
    
    # Để minh họa prototype, chúng ta chạy 1 seed của S0_main và 1 seed của S1_infra_loss
    routes_to_run = [
        ("holdout", "S0_main", 2001, "S0_main", 1001),
        ("holdout", "S1_infra_loss", 2001, "S1_infra_loss", 1001)
    ]
    
    print("Bắt đầu chạy thí nghiệm Retention Policy Optimizer (Prototype)...")
    
    for eval_split, eval_scen, eval_seed, dev_scen, dev_seed in routes_to_run:
        print(f"\n--- Đang xử lý: {eval_split} | {eval_scen} | Seed: {eval_seed} ---")
        
        # 1. Sinh dữ liệu
        dev_incs = generate_incidents(config, "development", dev_scen, dev_seed)
        eval_incs = generate_incidents(config, eval_split, eval_scen, eval_seed)
        print(f"Đã sinh {len(dev_incs)} dev incidents và {len(eval_incs)} eval incidents.")
        
        # 2. Baseline policy
        baseline = get_baseline_policy(config, budget_gb, dev_scen, dev_seed)
        print(f"Baseline TTL: {baseline['ttl_days']}")
        
        # 3. Optimized policy (Grid Search)
        print("Đang tìm chính sách tối ưu bằng Exhaustive Grid Search...")
        optimized = optimize_policy(config, dev_incs, budget_gb, dev_scen, dev_seed)
        print(f"Optimized TTL: {optimized['ttl_days']}")
        
        policies = {
            baseline["policy_id"]: baseline,
            optimized["policy_id"]: optimized
        }
        
        # 4. Đánh giá trên tập Holdout/Shift
        print(f"Đang đánh giá trên tập {eval_split}...")
        res_baseline = evaluate_policy(config, baseline, eval_incs)
        res_optimized = evaluate_policy(config, optimized, eval_incs)
        
        metrics = {
            "split": eval_split,
            "scenario": eval_scen,
            "seed": eval_seed,
            "budget_gb": budget_gb,
            "policies": {
                baseline["policy_id"]: res_baseline["metrics"],
                optimized["policy_id"]: res_optimized["metrics"]
            },
            "paired": {"delta_pp": {}},
            "failure_cases": []
        }
        
        delta = res_optimized["metrics"]["coverage_total"] - res_baseline["metrics"]["coverage_total"]
        metrics["paired"]["delta_pp"]["Optimized vs Baseline"] = delta * 100
        
        metrics["status"] = "valid" if (res_baseline["status"] == "valid" and res_optimized["status"] == "valid") else "invalid"
        
        if eval_scen == "S1_infra_loss":
            metrics["failure_cases"].append("Sự cố S1 (Mất hạ tầng hoàn toàn): Time travel của Delta/Iceberg không phải là backup. Không thể khôi phục dù H <= TTL do mất cả current state lẫn history.")
            
        print("Đang xuất báo cáo HTML và gọi LLM...")
        run_id, html_path, json_path = export_report(config, metrics, policies)
        print(f"Hoàn thành! Run ID: {run_id}")
        print(f"Báo cáo HTML: {html_path}")
        print(f"Dữ liệu JSON: {json_path}")

if __name__ == "__main__":
    main()
