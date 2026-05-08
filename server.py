from fastmcp import FastMCP

mcp = FastMCP("Aegis Anesthesia MCP")


@mcp.tool()
def assess_preop_risk(
    age: int,
    spo2: int,
    bmi: float,
    diabetes: bool,
    hypertension: bool,
    airway_grade: int
) -> str:
    """
    Comprehensive preoperative anesthesia risk assessment
    """

    risk_score = 0
    findings = []

    # Age
    if age > 65:
        risk_score += 2
        findings.append("Elderly patient")

    # Oxygenation
    if spo2 < 90:
        risk_score += 3
        findings.append("Hypoxemia")

    # BMI
    if bmi > 30:
        risk_score += 2
        findings.append("Obesity")

    # Comorbidities
    if diabetes:
        risk_score += 1
        findings.append("Diabetes")

    if hypertension:
        risk_score += 1
        findings.append("Hypertension")

    # Airway
    if airway_grade >= 3:
        risk_score += 3
        findings.append("Potential difficult airway")

    # Risk category
    if risk_score <= 2:
        category = "LOW RISK"
    elif risk_score <= 5:
        category = "MODERATE RISK"
    else:
        category = "HIGH RISK"

    recommendation = []

    if spo2 < 90:
        recommendation.append("Optimize oxygenation preoperatively")

    if airway_grade >= 3:
        recommendation.append("Prepare difficult airway cart")

    if bmi > 30:
        recommendation.append("Consider ramp positioning")

    if risk_score > 5:
        recommendation.append("Postoperative ICU observation advised")

    result = f"""
=== PREOPERATIVE RISK ASSESSMENT ===

Risk Category: {category}

Clinical Findings:
- {" | ".join(findings)}

Recommendations:
- {" | ".join(recommendation)}

Total Risk Score: {risk_score}
"""

    return result


if __name__ == "__main__":
    mcp.run()