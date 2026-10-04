def evaluate_policy(config: dict, policy: dict, incidents: list) -> dict:
    """
    Đánh giá policy trên danh sách incidents và trả về metrics.
    Tính toán cost, kiểm tra budget violation, min_ttl violation.
    Tính recoverable khi không mất hạ tầng và target_age_days <= TTL.
    """
    ttl_days = policy.get("ttl_days", {})
    budget_gb = policy.get("budget_gb", 0)
    
    profiles = config.get("profiles", [])
    
    # Cost = sum(h_i * ttl_i)
    cost_gb = sum(p["history_gb_per_day"] * ttl_days.get(p["table_id"], 0) for p in profiles)
    
    budget_violations = 1 if cost_gb > budget_gb else 0
    min_ttl_violations = sum(1 for p in profiles if ttl_days.get(p["table_id"], 0) < p["min_ttl_days"])
    
    total = len(incidents)
    recoverable = 0
    coverage_by_profile = {p["table_id"]: {"recoverable": 0, "total": 0} for p in profiles}
    
    logical_total = 0
    logical_recoverable = 0
    infra_loss_total = 0
    infra_loss_recoverable = 0
    
    for inc in incidents:
        table_id = inc["table_id"]
        ttl = ttl_days.get(table_id, 0)
        
        a = inc.get("anchor_gap_days", 0)
        d = inc.get("detect_delay_days", 0)
        l = inc.get("response_lag_days", 0)
        h = inc.get("target_age_days", 0)
        
        # Validate schema logic: H = A + D + L
        if abs(h - (a + d + l)) > 1e-6:
            raise ValueError(f"Input sai: target_age_days ({h}) != A + D + L ({a + d + l}) cho incident {inc.get('incident_id')}")
            
        infra_lost = inc.get("infrastructure_lost", False)
        
        # Mô hình lý tưởng: không mất hạ tầng và H <= TTL
        is_recoverable = (not infra_lost) and (h <= ttl)
        
        if is_recoverable:
            recoverable += 1
            if table_id in coverage_by_profile:
                coverage_by_profile[table_id]["recoverable"] += 1
            
        if table_id in coverage_by_profile:
            coverage_by_profile[table_id]["total"] += 1
        
        if infra_lost:
            infra_loss_total += 1
            if is_recoverable:
                infra_loss_recoverable += 1
        else:
            logical_total += 1
            if is_recoverable:
                logical_recoverable += 1
                
    is_valid = (budget_violations == 0) and (min_ttl_violations == 0) and policy.get("feasible", True)
    status = "valid" if is_valid else "invalid"
    
    return {
        "status": status, # invalid nếu vượt budget, vi phạm min ttl hoặc không feasible
        "metrics": {
            "coverage_total": recoverable / total if total > 0 else 0.0,
            "coverage_by_profile": {
                tid: (counts["recoverable"] / counts["total"] if counts["total"] > 0 else 0.0)
                for tid, counts in coverage_by_profile.items()
            },
            "recoverable": recoverable,
            "total": total,
            "coverage_logical_only": logical_recoverable / logical_total if logical_total > 0 else 0.0,
            "coverage_infra_loss": infra_loss_recoverable / infra_loss_total if infra_loss_total > 0 else 0.0,
            "cost_gb": float(cost_gb),
            "budget_violations": budget_violations,
            "min_ttl_violations": min_ttl_violations
        }
    }
