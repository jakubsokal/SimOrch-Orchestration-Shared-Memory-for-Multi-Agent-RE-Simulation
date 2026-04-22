import json
import os
import sys
import difflib
import statistics
import yaml
from datetime import datetime
from pathlib import Path

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity as sk_cosine
    import numpy as np
    SKLEARN_OK = True
except ImportError:
    SKLEARN_OK = False

try:
    from sentence_transformers import SentenceTransformer, util as sbert_util
    _SBERT_MODEL    = SentenceTransformer("all-MiniLM-L6-v2")
    SBERT_AVAILABLE = True
    print("SBERT loaded (all-MiniLM-L6-v2) semantic similarity will use embeddings.")
except ImportError:
    SBERT_AVAILABLE = False
    print("sentence-transformers not installed falling back to difflib for semantic similarity.")


THRESHOLDS = {
    "excellent":    90,
    "good":         75,
    "satisfactory": 60,
}

SBERT_TRACE_THRESHOLD = 0.45
TFIDF_TRACE_THRESHOLD = 0.20
GT_THRESHOLDS = [0.45, 0.60, 0.70]


def grade(score: float) -> str:
    if score >= THRESHOLDS["excellent"]:
        return "Excellent"
    elif score >= THRESHOLDS["good"]:
        return "Good"
    elif score >= THRESHOLDS["satisfactory"]:
        return "Satisfactory"
    else:
        return "Needs Improvement"

def _sd(values: list) -> float | None:
    return round(statistics.pstdev(values), 4) if len(values) >= 2 else None


def load_run(run_dir: Path) -> dict:
    result = {
        "path": str(run_dir), "valid": False, "errors": [],
        "warnings": [], "transcript": [], "requirements": [],
        "issues": [], "run_details": {},
    }

    transcript_path = run_dir / "messages_log.json"
    if not transcript_path.exists():
        result["errors"].append("Missing messages_log.json")
    else:
        try:
            with open(transcript_path, encoding="utf-8") as f:
                result["transcript"] = json.load(f)
        except json.JSONDecodeError as e:
            result["errors"].append(f"Malformed messages_log.json: {e}")

    req_path = run_dir / "requirements_log.json"
    if not req_path.exists():
        result["warnings"].append(
            "requirements_log.json not found traceability cannot be scored for this run")
    else:
        try:
            with open(req_path, encoding="utf-8") as f:
                result["requirements"] = json.load(f)
        except json.JSONDecodeError as e:
            result["warnings"].append(f"Malformed requirements_log.json: {e}")

    issues_path = run_dir / "issues_log.json"
    if not issues_path.exists():
        result["issues"] = []
    else:
        try:
            with open(issues_path, encoding="utf-8") as f:
                result["issues"] = json.load(f)
        except json.JSONDecodeError as e:
            result["warnings"].append(f"Malformed issues_log.json: {e}")

    details_path = run_dir / "run_details.json"
    if details_path.exists():
        try:
            with open(details_path, encoding="utf-8") as f:
                result["run_details"] = json.load(f)
        except json.JSONDecodeError:
            pass

    result["valid"] = (len(result["errors"]) == 0 and len(result["transcript"]) > 0)
    return result


def load_all_runs(runs_dir: str = "runs") -> list:
    runs_path = Path(runs_dir)
    if not runs_path.exists():
        raise FileNotFoundError(f"Runs directory '{runs_dir}' not found.")
    dirs = sorted([d for d in runs_path.iterdir() if d.is_dir()])
    if not dirs:
        raise ValueError(f"No run directories found inside '{runs_dir}'.")
    return [load_run(d) for d in dirs]


def load_scenario_config(scenario_path: str) -> dict:
    """Load ground truths and configured stakeholder names from a scenario YAML."""
    with open(scenario_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    ground_truths = [
        {"id": t["id"], "type": t.get("type", ""), "statement": t["statement"]}
        for t in data.get("scenarioTruths", [])
    ]
    stakeholder_names = [
        agent["name"]
        for agent in data.get("user_agents", [])
        if agent.get("name")
    ]
    return {"ground_truths": ground_truths, "stakeholder_names": stakeholder_names}


def _text_sim(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a.strip(), b.strip()).ratio()

def _sbert_sim(a: str, b: str) -> float:
    emb_a = _SBERT_MODEL.encode(a, convert_to_tensor=True)
    emb_b = _SBERT_MODEL.encode(b, convert_to_tensor=True)
    return float(sbert_util.cos_sim(emb_a, emb_b))

def _tfidf_cosine_matrix(texts_a: list, texts_b: list):
    if not SKLEARN_OK or not texts_a or not texts_b:
        return None
    all_texts = texts_a + texts_b
    vec = TfidfVectorizer(ngram_range=(1, 2)).fit(all_texts)
    ea  = vec.transform(texts_a)
    eb  = vec.transform(texts_b)
    return sk_cosine(ea, eb)

def _sbert_cosine_matrix(texts_a: list, texts_b: list):
    if not SBERT_AVAILABLE or not texts_a or not texts_b:
        return None
    ea = _SBERT_MODEL.encode(texts_a, convert_to_numpy=True, show_progress_bar=False)
    eb = _SBERT_MODEL.encode(texts_b, convert_to_numpy=True, show_progress_bar=False)
    ea = ea / (np.linalg.norm(ea, axis=1, keepdims=True) + 1e-9)
    eb = eb / (np.linalg.norm(eb, axis=1, keepdims=True) + 1e-9)
    return ea @ eb.T


def _check_behavioural_validity(
    transcript: list,
    requirements: list,
    configured_stakeholders: list = None,
) -> dict:
    """
    Five automated behavioural checks (B1-B5).

    B1. all_agents_contributed      RE (role=1) and ALL configured stakeholders (role=2) spoke
    B2. turn_alternation            RE and stakeholder alternate without repetition
    B3. no_consecutive_duplicates   no agent sends identical consecutive messages
    B4. re_question_rate            >=50% of RE messages end with '?'
    B5. extraction_coverage         requirements extracted from >=75% of stakeholder turns
    """
    checks = {
        "B1_all_agents_contributed":    False,
        "B2_turn_alternation":          False,
        "B3_no_consecutive_duplicates": False,
        "B4_re_question_rate":          False,
        "B5_extraction_coverage":       False,
    }
    notes = []

    if not transcript:
        notes.append("Empty transcript all checks failed.")
        return {"checks": checks, "passed": 0, "total": 5, "notes": notes}

    roles    = [m.get("role")        for m in transcript]
    messages = [m.get("message", "") for m in transcript]
    re_flags = [1 if (r == 1 or str(r).lower() in ("re", "1", "requirement engineer"))
                else 0 for r in roles]

    # --- B1: all configured agents contributed
    has_re = any(f == 1 for f in re_flags)
    transcript_stakeholder_names = {
        m.get("agent") for m in transcript
        if m.get("role") == 2 and m.get("agent")
    }
    if configured_stakeholders:
        missing = [s for s in configured_stakeholders if s not in transcript_stakeholder_names]
        all_stakeholders_contributed = len(missing) == 0
        if not all_stakeholders_contributed:
            notes.append(f"B1 FAIL: Stakeholders not contributing: {missing}")
    else:
        all_stakeholders_contributed = bool(transcript_stakeholder_names)
        if not all_stakeholders_contributed:
            notes.append("B1 FAIL: No stakeholder messages found in transcript.")

    if has_re and all_stakeholders_contributed:
        checks["B1_all_agents_contributed"] = True
    elif not has_re:
        notes.append("B1 FAIL: RE Agent did not contribute.")

    # --- B2: turn alternation
    consecutive_same = any(re_flags[i] == re_flags[i + 1] for i in range(len(re_flags) - 1))
    if not consecutive_same:
        checks["B2_turn_alternation"] = True
    else:
        bad = [(i, i + 1) for i in range(len(re_flags) - 1) if re_flags[i] == re_flags[i + 1]]
        notes.append(f"B2 FAIL: Same-role consecutive messages at pairs {bad[:3]}")

    # --- B3: no consecutive duplicates
    consecutive_dup = any(
        messages[i].strip() == messages[i + 1].strip() and messages[i].strip()
        for i in range(len(messages) - 1)
    )
    if not consecutive_dup:
        checks["B3_no_consecutive_duplicates"] = True
    else:
        notes.append("B3 FAIL: Consecutive duplicate messages detected.")

    # --- B4: RE question rate
    re_messages      = [messages[i] for i, f in enumerate(re_flags) if f == 1]
    re_question_rate = (
        sum(1 for m in re_messages if m.strip().endswith("?")) / max(len(re_messages), 1)
    )
    if re_question_rate >= 0.50:
        checks["B4_re_question_rate"] = True
    else:
        notes.append(
            f"B4 WARN: RE question rate {re_question_rate:.0%} < 50%. "
            "RE may be summarising instead of eliciting."
        )

    # --- B5: extraction coverage
    stakeholder_turns = {m.get("turn") for m in transcript if m.get("role") == 2}
    turns_with_reqs   = set()
    for req in requirements:
        tid = req.get("turn_id") or req.get("trace_message_id")
        if tid is not None:
            turns_with_reqs.add(tid)
    extraction_cov = len(stakeholder_turns & turns_with_reqs) / max(len(stakeholder_turns), 1)
    if extraction_cov >= 0.75:
        checks["B5_extraction_coverage"] = True
    else:
        notes.append(
            f"B5 WARN: Only {extraction_cov:.0%} of stakeholder turns "
            "produced requirements (>=75% expected)."
        )

    passed = sum(checks.values())
    total  = len(checks)
    return {
        "checks":              checks,
        "passed":              passed,
        "total":               total,
        "score_percent":       round(passed / total * 100, 2),
        "re_question_rate":    round(re_question_rate, 4),
        "extraction_coverage": round(extraction_cov, 4),
        "notes":               notes,
    }


def evaluate_feasibility(runs: list, configured_stakeholders: list = None) -> dict:
    total      = len(runs)
    successful = 0
    details    = []

    if total < 5:
        print(f"    WARNING: Only {total} runs provided. N>=5 recommended.")

    for run in runs:
        name         = Path(run["path"]).name
        transcript   = run.get("transcript", [])
        requirements = run.get("requirements", [])
        run_details  = run.get("run_details", {})

        if run_details:
            is_success = (
                bool(run_details.get("successful", False))
                and run_details.get("status", "") == "completed"
                and "error" not in run_details
            )
            status_str   = run_details.get("status", "unknown")
            status_src   = "run_details.json"
            seed         = run_details.get("seed")
            reproducible = run_details.get("reproducible")
        else:
            is_success   = run["valid"] and bool(transcript)
            status_str   = "completed" if is_success else "failed"
            status_src   = "inferred from transcript"
            seed         = None
            reproducible = None

        bv         = _check_behavioural_validity(transcript, requirements, configured_stakeholders)
        turn_count = max((m.get("turn", 0) for m in transcript), default=0)

        if is_success:
            successful += 1

        details.append({
            "run": name, "status": status_str, "status_source": status_src,
            "completed": is_success, "messages": len(transcript),
            "turns": turn_count, "seed": seed, "reproducible_flag": reproducible,
            "behavioural_validity": bv,
            "warnings": run.get("warnings", []), "errors": run.get("errors", []),
        })

    completion_percent = (successful / total * 100) if total > 0 else 0.0
    bv_scores = [
        d["behavioural_validity"]["score_percent"]
        for d in details
        if d["behavioural_validity"].get("score_percent") is not None
    ]
    bv_avg  = statistics.mean(bv_scores) if bv_scores else 0.0
    bv_sd   = _sd(bv_scores)
    overall = round((completion_percent + bv_avg) / 2, 2)

    return {
        "total_runs": total, "successful_runs": successful,
        "failed_runs": total - successful,
        "completion_rate_percent": round(completion_percent, 2),
        "behavioural_validity_avg_percent": round(bv_avg, 2),
        "behavioural_validity_sd": bv_sd,
        "score_percent": overall, "grade": grade(overall),
        "details": details,
    }


def _structural_sim(t1: list, t2: list) -> float:
    if not t1 or not t2:
        return 0.0
    max_len   = max(len(t1), len(t2))
    len_sim   = 1.0 - abs(len(t1) - len(t2)) / max_len
    seq1      = " ".join(m.get("agent", "") for m in t1)
    seq2      = " ".join(m.get("agent", "") for m in t2)
    agent_sim = _text_sim(seq1, seq2)
    return (len_sim + agent_sim) / 2


def _semantic_sim(t1: list, t2: list) -> dict:
    if not t1 or not t2:
        return {"lexical": 0.0, "semantic": None}
    pairs        = list(zip(t1, t2))
    lexical_sims = [_text_sim(a.get("message", ""), b.get("message", "")) for a, b in pairs]
    lexical      = statistics.mean(lexical_sims) if lexical_sims else 0.0
    if SBERT_AVAILABLE:
        sbert_sims = [_sbert_sim(a.get("message", ""), b.get("message", "")) for a, b in pairs]
        semantic   = statistics.mean(sbert_sims) if sbert_sims else 0.0
    else:
        semantic = None
    return {"lexical": lexical, "semantic": semantic}


def evaluate_reproducibility(runs: list) -> dict:
    valid = [r for r in runs if r["valid"] and r.get("transcript")]
    if len(valid) < 2:
        return {"note": "At least 2 successful runs are required.",
                "structural": None, "semantic": None, "lexical_reference": None}
    structural_scores, lexical_scores, sbert_scores, pair_details = [], [], [], []
    for i in range(len(valid)):
        for j in range(i + 1, len(valid)):
            r1, r2  = valid[i], valid[j]
            t1, t2  = r1["transcript"], r2["transcript"]
            n1, n2  = Path(r1["path"]).name, Path(r2["path"]).name
            struct  = _structural_sim(t1, t2)
            sem     = _semantic_sim(t1, t2)
            structural_scores.append(struct)
            lexical_scores.append(sem["lexical"])
            if sem["semantic"] is not None:
                sbert_scores.append(sem["semantic"])
            detail = {
                "pair": f"{n1} vs {n2}",
                "structural_similarity_percent": round(struct * 100, 2),
                "lexical_percent": round(sem["lexical"] * 100, 2),
                "messages_run_a": len(t1), "messages_run_b": len(t2),
                "turns_compared": min(len(t1), len(t2)),
            }
            if sem["semantic"] is not None:
                detail["sbert_percent"] = round(sem["semantic"] * 100, 2)
            pair_details.append(detail)
    avg_struct  = round(statistics.mean(structural_scores) * 100, 2)
    sd_struct   = _sd([s * 100 for s in structural_scores])
    avg_lexical = round(statistics.mean(lexical_scores) * 100, 2)
    avg_sbert   = round(statistics.mean(sbert_scores) * 100, 2) if sbert_scores else None
    sd_sbert    = _sd([s * 100 for s in sbert_scores]) if sbert_scores else None
    return {
        "runs_compared": len(valid), "pairs_evaluated": len(pair_details),
        "structural": {"average_percent": avg_struct, "sd": sd_struct,
                       "grade": grade(avg_struct),
                       "note": "Orchestrator determinism turn count and agent order."},
        "semantic": {"method": "SBERT (all-MiniLM-L6-v2)" if SBERT_AVAILABLE else "unavailable",
                     "average_percent": avg_sbert, "sd": sd_sbert,
                     "grade": grade(avg_sbert) if avg_sbert is not None else "N/A",
                     "note": "Primary metric meaning equivalence across runs."},
        "lexical_reference": {"method": "difflib", "average_percent": avg_lexical,
                              "note": "Reference baseline only therefore not graded."},
        "pair_details": pair_details,
    }


def _get_turn_ref(req):
    for key in ("turn_id", "source_turn", "trace_message_id", "turn"):
        if key in req and req[key] is not None:
            return req[key]
    return None

def _get_req_id(req):
    return req.get("req_id", req.get("id", "unknown"))

def _get_req_text(req) -> str:
    nested = req.get("requirement")
    if isinstance(nested, dict):
        text = nested.get("description", nested.get("text", ""))
        if text:
            return str(text)
    return str(req.get("text", req.get("description", "")))

def _get_evidence_quote(req) -> str:
    nested = req.get("requirement")
    if isinstance(nested, dict):
        eq = nested.get("evidence_quote", "")
        if eq:
            return str(eq)
    return str(req.get("evidence_quote", ""))


def evaluate_traceability(runs: list) -> dict:
    run_results = []
    for run in runs:
        if not run["valid"]:
            continue
        name         = Path(run["path"]).name
        requirements = run.get("requirements", [])
        transcript   = run.get("transcript", [])
        valid_turns  = {m.get("turn") for m in transcript}
        turn_to_msg  = {m.get("turn"): m.get("message", "") for m in transcript}
        if not requirements:
            run_results.append({"run": name, "note": "No requirements found.", "score_percent": 0.0})
            continue
        struct_ok = sem_ok = 0
        req_details, evidence_quotes, cited_messages, req_indices = [], [], [], []
        for req in requirements:
            req_id   = _get_req_id(req)
            turn_ref = _get_turn_ref(req)
            link_val = turn_ref is not None and turn_ref in valid_turns
            req_text = _get_req_text(req)
            if link_val:
                struct_ok += 1
                eq = _get_evidence_quote(req)
                cm = turn_to_msg.get(turn_ref, "")
                if eq and cm:
                    evidence_quotes.append(eq)
                    cited_messages.append(cm)
                    req_indices.append(len(req_details))
            req_details.append({"id": req_id, "text": req_text, "source_turn": turn_ref,
                                 "struct_traced": link_val, "sem_traced": False,
                                 "sbert": None, "tfidf": None})
        if evidence_quotes:
            sbert_mat = _sbert_cosine_matrix(evidence_quotes, cited_messages)
            tfidf_mat = _tfidf_cosine_matrix(evidence_quotes, cited_messages)
            for k, rd_idx in enumerate(req_indices):
                sbert_s = float(sbert_mat[k, k]) if sbert_mat is not None else 0.0
                tfidf_s = float(tfidf_mat[k, k]) if tfidf_mat is not None else 0.0
                traced  = sbert_s >= SBERT_TRACE_THRESHOLD or tfidf_s >= TFIDF_TRACE_THRESHOLD
                if traced:
                    sem_ok += 1
                req_details[rd_idx].update({"sem_traced": traced,
                                            "sbert": round(sbert_s, 4),
                                            "tfidf": round(tfidf_s, 4)})
        total = len(requirements)
        structural_pct = struct_ok / total * 100
        semantic_pct   = sem_ok / total * 100
        score_pct      = (structural_pct + semantic_pct) / 2
        sbert_vals = [r["sbert"] for r in req_details if r["sbert"] is not None]
        tfidf_vals = [r["tfidf"] for r in req_details if r["tfidf"] is not None]
        run_results.append({
            "run": name, "total_requirements": total,
            "struct_traced": struct_ok,
            "structural_traceability_percent": round(structural_pct, 2),
            "sem_traced": sem_ok,
            "semantic_similarity_percent": round(semantic_pct, 2),
            "avg_sbert": round(statistics.mean(sbert_vals), 4) if sbert_vals else None,
            "avg_tfidf": round(statistics.mean(tfidf_vals), 4) if tfidf_vals else None,
            "score_percent": round(score_pct, 2),
            "requirements": req_details,
        })
    if not run_results:
        return {"note": "No valid runs with requirements found.", "score_percent": None, "grade": "N/A"}
    scores    = [r["score_percent"] for r in run_results]
    avg_score = round(statistics.mean(scores), 2)
    return {"runs_evaluated": len(run_results), "score_percent": avg_score,
            "sd": _sd(scores), "grade": grade(avg_score), "run_details": run_results}


def evaluate_issues(runs: list) -> dict:
    run_results = []
    for run in runs:
        if not run["valid"]:
            continue
        name         = Path(run["path"]).name
        issues       = run.get("issues", [])
        transcript   = run.get("transcript", [])
        requirements = run.get("requirements", [])
        if not issues:
            run_results.append({"run": name, "note": "No issues found in issues_log.json",
                                "score_percent": None})
            continue
        valid_turns   = {m.get("turn") for m in transcript}
        valid_req_ids = {str(_get_req_id(r)) for r in requirements}
        turn_linked = req_linked = 0
        severity    = {"high": 0, "medium": 0, "low": 0, "unknown": 0}
        issue_detail = []
        for iss in issues:
            issue_body = iss.get("issue", {})
            turn_ref   = iss.get("turn_id")
            req_ref    = str(issue_body.get("related_requirement_id", ""))
            sev        = issue_body.get("severity", "unknown").lower()
            turn_ok    = turn_ref is not None and turn_ref in valid_turns
            req_ok     = bool(req_ref) and req_ref in valid_req_ids
            if turn_ok: turn_linked += 1
            if req_ok:  req_linked  += 1
            severity[sev if sev in severity else "unknown"] += 1
            issue_detail.append({
                "issue_id": iss.get("issue_id", "?"),
                "type": issue_body.get("type", "unknown"),
                "severity": sev, "status": issue_body.get("status", "unknown"),
                "turn_id": turn_ref, "turn_valid": turn_ok,
                "related_req_id": req_ref or None, "req_link_valid": req_ok,
                "description": str(issue_body.get("description", "")),
                "created_by": iss.get("createdBy", "unknown"),
            })
        total = len(issues)
        turn_cov_pct = round(turn_linked / total * 100, 2)
        req_link_pct = round(req_linked / total * 100, 2)
        score_pct    = round((turn_cov_pct + req_link_pct) / 2, 2)
        run_results.append({
            "run": name, "total_issues": total,
            "turn_coverage_percent": turn_cov_pct,
            "requirement_linkage_percent": req_link_pct,
            "score_percent": score_pct,
            "severity_breakdown": severity, "issues": issue_detail,
        })
    scoreable = [r["score_percent"] for r in run_results if r.get("score_percent") is not None]
    if not scoreable:
        return {"note": "No runs had issues_log.json issues evaluation skipped.",
                "score_percent": None, "grade": "N/A"}
    avg_score = round(statistics.mean(scoreable), 2)
    return {"runs_evaluated": len(run_results), "score_percent": avg_score,
            "sd": _sd(scoreable), "grade": grade(avg_score), "run_details": run_results}


def evaluate_ground_truth_coverage(runs: list, ground_truths: list) -> dict:
    if not ground_truths:
        return {"note": "No scenario YAML provided GT coverage skipped.",
                "score_percent": None, "grade": "N/A"}
    gt_statements = [g["statement"] for g in ground_truths]
    run_results   = []
    for run in runs:
        if not run["valid"] or not run.get("requirements"):
            continue
        name      = Path(run["path"]).name
        extracted = [_get_req_text(r) for r in run["requirements"] if _get_req_text(r)]
        if not extracted:
            run_results.append({"run": name, "note": "No requirements extracted.", "score_percent": 0.0})
            continue
        sbert_mat = _sbert_cosine_matrix(gt_statements, extracted)
        tfidf_mat = _tfidf_cosine_matrix(gt_statements, extracted)
        covered_by_threshold = {str(t): 0 for t in GT_THRESHOLDS}
        covered_tfidf = 0
        per_gt = []
        for i, gt in enumerate(ground_truths):
            best_s = float(sbert_mat[i].max()) if sbert_mat is not None else 0.0
            best_t = float(tfidf_mat[i].max()) if tfidf_mat is not None else 0.0
            threshold_results = {}
            for t in GT_THRESHOLDS:
                covered = best_s >= t
                threshold_results[str(t)] = covered
                if covered:
                    covered_by_threshold[str(t)] += 1
            ok_t = best_t >= TFIDF_TRACE_THRESHOLD
            if ok_t:
                covered_tfidf += 1
            per_gt.append({
                "id": gt["id"], "type": gt["type"], "ground_truth": gt["statement"],
                "best_sbert": round(best_s, 4), "best_tfidf": round(best_t, 4),
                "covered_tfidf": ok_t,
                **{f"covered_{t}": threshold_results[str(t)] for t in GT_THRESHOLDS},
            })
        m_gt = len(ground_truths)
        primary_covered = covered_by_threshold[str(GT_THRESHOLDS[0])]
        score_percent   = primary_covered / m_gt * 100
        run_results.append({
            "run": name, "total_gt": m_gt,
            "covered_tfidf": covered_tfidf,
            "tfidf_coverage_percent": round(covered_tfidf / m_gt * 100, 2),
            **{f"covered_sbert_{t}": covered_by_threshold[str(t)] for t in GT_THRESHOLDS},
            **{f"coverage_sbert_{t}_percent": round(covered_by_threshold[str(t)] / m_gt * 100, 2)
               for t in GT_THRESHOLDS},
            "score_percent": round(score_percent, 2),
            "per_gt": per_gt,
        })
    if not run_results:
        return {"note": "No valid runs to evaluate GT coverage.", "score_percent": None, "grade": "N/A"}
    scores    = [r["score_percent"] for r in run_results]
    avg_score = round(statistics.mean(scores), 2)
    return {
        "runs_evaluated": len(run_results), "score_percent": avg_score,
        "sd": _sd(scores), "grade": grade(avg_score),
        "thresholds_used": GT_THRESHOLDS, "primary_threshold": GT_THRESHOLDS[0],
        "note": ("Primary score = SBERT >= 0.45 coverage. "
                 "Coverage at 0.60 and 0.70 reported for sensitivity analysis. "
                 "TF-IDF reported as secondary reference only."),
        "run_details": run_results,
    }


def evaluate_requirement_reproducibility(runs: list) -> dict:
    valid_with_reqs = [r for r in runs if r["valid"] and r.get("requirements")]
    if len(valid_with_reqs) < 2:
        return {"note": "At least 2 runs with requirements_log.json are needed.",
                "score_percent": None, "grade": "N/A"}

    def req_texts(run):
        return [_get_req_text(r) for r in run["requirements"] if _get_req_text(r)]

    def best_match_score(texts_a, texts_b):
        if not texts_a or not texts_b:
            return 0.0
        scores = []
        for a in texts_a:
            sims = ([_sbert_sim(a, b) for b in texts_b] if SBERT_AVAILABLE
                    else [_text_sim(a, b) for b in texts_b])
            scores.append(max(sims))
        return statistics.mean(scores)

    pair_details, pair_scores = [], []
    for i in range(len(valid_with_reqs)):
        for j in range(i + 1, len(valid_with_reqs)):
            r1, r2 = valid_with_reqs[i], valid_with_reqs[j]
            n1, n2 = Path(r1["path"]).name, Path(r2["path"]).name
            t1, t2 = req_texts(r1), req_texts(r2)
            ab  = best_match_score(t1, t2)
            ba  = best_match_score(t2, t1)
            sym = (ab + ba) / 2
            pair_scores.append(sym)
            pair_details.append({
                "pair": f"{n1} vs {n2}",
                "reqs_run_a": len(t1), "reqs_run_b": len(t2),
                "ab_best_match_percent": round(ab * 100, 2),
                "ba_best_match_percent": round(ba * 100, 2),
                "symmetric_score_percent": round(sym * 100, 2),
                "method": "SBERT" if SBERT_AVAILABLE else "difflib",
            })
    avg = round(statistics.mean(pair_scores) * 100, 2)
    return {
        "runs_compared": len(valid_with_reqs), "pairs_evaluated": len(pair_details),
        "avg_score_percent": avg, "sd": _sd([s * 100 for s in pair_scores]),
        "grade": grade(avg),
        "method": "SBERT (all-MiniLM-L6-v2)" if SBERT_AVAILABLE else "difflib (lexical)",
        "interpretation": ("Measures whether the same requirements were elicited across runs, "
                           "regardless of wording."),
        "pair_details": pair_details,
    }


def _fmt(score) -> str:
    return f"{score}%" if score is not None else "N/A"


def print_report(results: dict):
    now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    print("\n")
    print("Evaluation Report")
    print(f"Generated : {now}")

    f = results["feasibility"]
    print("\n[1] FEASIBILITY")
    print(f"    Total runs               : {f['total_runs']}")
    print(f"    Successful runs          : {f['successful_runs']}")
    print(f"    Completion rate          : {_fmt(f['completion_rate_percent'])}")
    print(f"    Behavioural validity (BV): {_fmt(f['behavioural_validity_avg_percent'])}  "
          f"(SD={f.get('behavioural_validity_sd','N/A')})")
    print(f"    Overall score            : {_fmt(f['score_percent'])}    {f['grade']}")
    for d in f["details"]:
        sym = "✓" if d.get("completed") else "✗"
        bv  = d.get("behavioural_validity", {})
        print(f"\n  {sym} {d['run']}  "
              f"({d.get('messages','?')} messages  seed={d.get('seed','?')}  "
              f"BV {bv.get('passed',0)}/{bv.get('total',5)} checks)")
        for k, v in bv.get("checks", {}).items():
            sym2 = "✓" if v else "✗"
            print(f"         {sym2}  {k}")
        for note in bv.get("notes", []):
            print(f"          ↳ {note}")

    r = results["reproducibility"]
    print("\n[2] REPRODUCIBILITY")
    if r.get("structural") is None:
        print(f"    {r.get('note','N/A')}")
    else:
        print(f"    Runs compared       : {r['runs_compared']}")
        print(f"    Pairs evaluated     : {r['pairs_evaluated']}")
        s, sem, lex = r["structural"], r["semantic"], r["lexical_reference"]
        print(f"    Structural          : {_fmt(s['average_percent'])}  ±{s.get('sd','N/A')}  {s['grade']}")
        print(f"    {s['note']}")
        sem_val = _fmt(sem['average_percent']) if sem['average_percent'] is not None else "SBERT not installed"
        print(f"    Semantic (SBERT)    : {sem_val}  ±{sem.get('sd','N/A')}  {sem['grade']}")
        print(f"    {sem['note']}")
        print(f"    Lexical (ref)       : {_fmt(lex['average_percent'])}  [not graded]")
        for p in r.get("pair_details", []):
            sbert_str = f"  SBERT: {p['sbert_percent']}%" if "sbert_percent" in p else ""
            print(f"    {p['pair']}   Structural: {p['structural_similarity_percent']}%  "
                  f"Lexical: {p['lexical_percent']}%{sbert_str}")

    traceability = results["traceability"]
    print("\n[3] TRACEABILITY  (structural + semantic)")
    if traceability.get("score_percent") is None:
        print(f"    {traceability.get('note','N/A')}")
    else:
        print(f"    Runs evaluated   : {traceability['runs_evaluated']}")
        print(f"    Score            : {_fmt(traceability['score_percent'])}  "
              f"±{traceability.get('sd','N/A')}    {traceability['grade']}")
        for run in traceability.get("run_details", []):
            print(f"\n    Run : {run['run']}")
            if "note" in run:
                print(f"      {run['note']}")
            else:
                print(f"        Total requirements  : {run['total_requirements']}")
                print(f"        Structural traced   : {run['struct_traced']}  ({run['structural_traceability_percent']}%)")
                print(f"        Semantic traced     : {run['sem_traced']}  ({run['semantic_similarity_percent']}%)  "
                      f"[SBERT>={SBERT_TRACE_THRESHOLD} OR TF-IDF>={TFIDF_TRACE_THRESHOLD}]")
                if run.get("avg_sbert") is not None:
                    print(f"        Avg SBERT : {run['avg_sbert']}  TF-IDF : {run.get('avg_tfidf','N/A')}")

    issues = results["issues"]
    print("\n[4] ISSUES TRACEABILITY")
    if issues.get("score_percent") is None:
        print(f"    {issues.get('note','N/A')}")
    else:
        print(f"    Runs evaluated   : {issues['runs_evaluated']}")
        print(f"    Score            : {_fmt(issues['score_percent'])}  "
              f"±{issues.get('sd','N/A')}    {issues['grade']}")
        for run in issues.get("run_details", []):
            print(f"\n    Run : {run['run']}")
            if "note" in run:
                print(f"      {run['note']}")
            else:
                sev = run.get("severity_breakdown", {})
                print(f"        Total issues   : {run['total_issues']}")
                print(f"        Turn coverage  : {run['turn_coverage_percent']}%")
                print(f"        Req linkage    : {run['requirement_linkage_percent']}%")
                print(f"        Severity       : high={sev.get('high',0)}  "
                      f"medium={sev.get('medium',0)}  low={sev.get('low',0)}")

    gt = results.get("gt_coverage", {})
    print("\n[4b] GROUND-TRUTH COVERAGE")
    if gt.get("score_percent") is None:
        print(f"    {gt.get('note','No scenario YAML provided.')}")
    else:
        print(f"    Runs evaluated         : {gt['runs_evaluated']}")
        print(f"    Primary score (>=0.45)  : {_fmt(gt['score_percent'])}  "
              f"±{gt.get('sd','N/A')}    {gt['grade']}")
        print(f"    {gt.get('note','')}")
        for rd in gt.get("run_details", []):
            print(f"\n    Run : {rd['run']}")
            print(f"      Ground truths        : {rd['total_gt']}")
            for t in GT_THRESHOLDS:
                primary = " [PRIMARY]" if t == GT_THRESHOLDS[0] else ""
                print(f"      SBERT >= {t}  : {rd.get(f'covered_sbert_{t}','?')}  "
                      f"({rd.get(f'coverage_sbert_{t}_percent','?')}%){primary}")
            print(f"      TF-IDF ref   : {rd.get('covered_tfidf','?')}  "
                  f"({rd.get('tfidf_coverage_percent','?')}%)")
            for pg in rd.get("per_gt", []):
                sym = "✓" if pg.get(f"covered_{GT_THRESHOLDS[0]}") else "✗"
                print(f"      {sym}  [{pg['id']}] {pg['type']}  "
                      f"SBERT={pg['best_sbert']:.3f}  TFIDF={pg['best_tfidf']:.3f}  "
                      f"{pg['ground_truth'][:70]}")

    rr = results["req_reproducibility"]
    print("\n[5] REQUIREMENT CONTENT REPRODUCIBILITY")
    if rr.get("avg_score_percent") is None:
        print(f"    {rr.get('note','N/A')}")
    else:
        print(f"    Runs compared    : {rr['runs_compared']}")
        print(f"    Pairs evaluated  : {rr['pairs_evaluated']}")
        print(f"    Method           : {rr['method']}")
        print(f"    Avg score        : {_fmt(rr['avg_score_percent'])}  "
              f"±{rr.get('sd','N/A')}    {rr['grade']}")
        print(f"    {rr['interpretation']}")
        for p in rr.get("pair_details", []):
            print(f"    {p['pair']}  ({p['reqs_run_a']} vs {p['reqs_run_b']} reqs)  "
                  f"{p['symmetric_score_percent']}%")

    repro = results.get("reproducibility", {})
    semantic_pct   = (repro.get("semantic") or {}).get("average_percent")
    semantic_grade = (repro.get("semantic") or {}).get("grade", "N/A")
    gt_pct         = results.get("gt_coverage", {}).get("score_percent")
    gt_grade       = results.get("gt_coverage", {}).get("grade", "N/A")
    score_map = [
        ("Feasibility", results.get("feasibility", {}).get("score_percent"),
         results.get("feasibility", {}).get("grade", "N/A")),
        ("Structural reproducibility",
         (repro.get("structural") or {}).get("average_percent"),
         (repro.get("structural") or {}).get("grade", "N/A")),
        ("Semantic reproducibility (SBERT)", semantic_pct, semantic_grade),
        ("Req content reproducibility",
         results.get("req_reproducibility", {}).get("avg_score_percent"),
         results.get("req_reproducibility", {}).get("grade", "N/A")),
        ("Structural + semantic traceability",
         results.get("traceability", {}).get("score_percent"),
         results.get("traceability", {}).get("grade", "N/A")),
        ("Issues traceability",
         results.get("issues", {}).get("score_percent"),
         results.get("issues", {}).get("grade", "N/A")),
        ("GT coverage (SBERT >= 0.45)", gt_pct, gt_grade),
    ]
    scores  = [s for _, s, _ in score_map if s is not None]
    overall = statistics.mean(scores) if scores else 0.0
    print("\nOVERALL SUMMARY")
    print("-" * 60)
    for label, s, g in score_map:
        val = _fmt(s) if s is not None else "N/A"
        print(f"    {label:<40} : {val:<8}  [{g}]")
    print("-" * 60)
    print(f"    {'Overall (mean of above)':<40} : {round(overall,2):<8}%  [{grade(overall)}]")


def run_evaluation(
    runs_dir:    str = "runs",
    output_file: str = "evaluation_report.json",
    scenario_yaml: str = None,
) -> dict:
    print(f"\nLoading runs from: '{runs_dir}' ...")
    runs = load_all_runs(runs_dir)
    print(f"Found {len(runs)} run folder(s).")

    ground_truths        = []
    configured_stakeholders = []
    if scenario_yaml:
        config = load_scenario_config(scenario_yaml)
        ground_truths           = config["ground_truths"]
        configured_stakeholders = config["stakeholder_names"]
        print(f"Loaded {len(ground_truths)} ground truths from YAML.")
        print(f"Configured stakeholders: {configured_stakeholders}")

    results = {
        "generated_at":        datetime.now().isoformat(),
        "grading_thresholds":  THRESHOLDS,
        "runs_dir":            Path(runs_dir).name,
        "scenario_yaml":       Path(scenario_yaml).name if scenario_yaml else None,
        "feasibility":         evaluate_feasibility(runs, configured_stakeholders),
        "reproducibility":     evaluate_reproducibility(runs),
        "traceability":        evaluate_traceability(runs),
        "issues":              evaluate_issues(runs),
        "gt_coverage":         evaluate_ground_truth_coverage(runs, ground_truths),
        "req_reproducibility": evaluate_requirement_reproducibility(runs),
    }

    repro = results.get("reproducibility", {})
    sem_pct = (repro.get("semantic") or {}).get("average_percent")
    score_map = {
        "feasibility":                         results["feasibility"].get("score_percent"),
        "structural_reproducibility":          (repro.get("structural") or {}).get("average_percent"),
        "semantic_reproducibility_sbert":      sem_pct,
        "requirement_content_reproducibility": results["req_reproducibility"].get("avg_score_percent"),
        "traceability":                        results["traceability"].get("score_percent"),
        "issues_traceability":                 results["issues"].get("score_percent"),
        "gt_coverage_sbert_0_45":              results["gt_coverage"].get("score_percent"),
    }
    scores = [v for v in score_map.values() if v is not None]
    results["summary"] = {
        "dimension_scores":     score_map,
        "overall_mean_percent": round(statistics.mean(scores), 2) if scores else None,
        "overall_grade":        grade(statistics.mean(scores)) if scores else "N/A",
    }

    print_report(results)
    os.makedirs(Path(output_file).parent, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nFull report saved to: {output_file}\n")
    return results


if __name__ == "__main__":
    scenario_id = sys.argv[1] if len(sys.argv) > 1 else None
    if not scenario_id:
        print("Usage: python evaluator.py <scenario_id>  e.g. python evaluator.py 001")
        sys.exit(1)
    if not scenario_id.startswith("scenario_"):
        scenario_id = f"scenario_{scenario_id}"
    project_root  = Path(__file__).resolve().parent.parent
    runs_dir      = project_root / "runs" / scenario_id
    scenario_yaml = project_root / "scenarios" / f"{scenario_id}.yaml"
    results_dir   = project_root / "results"
    results_dir.mkdir(exist_ok=True)
    if not runs_dir.exists():
        print(f"ERROR: Runs folder not found: {runs_dir}")
        sys.exit(1)
    if not scenario_yaml.exists():
        print(f"WARNING: No scenario YAML found at {scenario_yaml} GT coverage will be skipped.")
        scenario_yaml = None
    existing    = list(results_dir.glob(f"{scenario_id}_eval_*.json"))
    eval_number = len(existing) + 1
    output_file = str(results_dir / f"{scenario_id}_eval_{eval_number}.json")
    run_evaluation(str(runs_dir), output_file, str(scenario_yaml) if scenario_yaml else None)