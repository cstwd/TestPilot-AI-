
"""Compute measured ratios from independent evidence, retaining all denominators."""


def ratio(numerator, denominator):
    if not 0 <= numerator <= denominator:
        raise ValueError(f"Invalid ratio: {numerator}/{denominator}")
    return {"numerator": numerator, "denominator": denominator,
            "percentage": round(100 * numerator / denominator, 2) if denominator else None}


def summarize(rows, regressions, campaigns):
    evaluated = [row for row in rows if row["evaluated"]]
    good = [row for row in evaluated if row["tier"] == "good"]
    completed = [row["report"]["before"] for row in campaigns if row.get("report", {}).get("status") == "completed"
                 and row["report"].get("before")]
    regression_runs = [row["workflow"] for row in regressions if "workflow" in row]
    return {
        "bug_detection_rate": ratio(sum(len(row["detected"]) for row in evaluated),
                                    sum(len(row["defects"]) for row in evaluated)),
        "test_pass_rate": ratio(sum(row["counts"]["passed"] for row in good),
                                sum(row["counts"]["passed"] + row["counts"]["failed"] for row in good)),
        "false_positive_rate": ratio(sum(bool(row["false_alarm_nodes"]) for row in good), len(good)),
        "boundary_test_coverage": ratio(sum(len(row["covered_boundaries"]) for row in evaluated),
                                        sum(len(row["boundaries"]) for row in evaluated)),
        "regression_pass_rate": ratio(sum(row["updated_bug"]["status"] == "resolved" and
                                          row["regression"]["status"] == "passed" for row in regression_runs),
                                      len(regression_runs)),
        "mutation_score": ratio(sum(row["killed"] for row in completed), sum(row["total"] for row in completed)),
    }
