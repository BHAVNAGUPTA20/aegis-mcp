from fastmcp import FastMCP
import uvicorn
import asyncio

# -------------------------------------------------
# MCP Server
# -------------------------------------------------
mcp = FastMCP("Aegis Anesthesia MCP")


# -------------------------------------------------
# Clinical Logic
# -------------------------------------------------
def generate_assessment(
    age: int,
    spo2: int,
    bmi: float,
    diabetes: bool,
    hypertension: bool,
    copd: bool,
    airway_grade: int,
    surgery_type: str
):

    risk_score = 0
    findings = []
    alerts = []
    recommendations = []

    # ---------------------------------------------
    # AGE
    # ---------------------------------------------
    if age >= 65:
        risk_score += 2
        findings.append("Elderly patient")

    # ---------------------------------------------
    # SPO2
    # ---------------------------------------------
    if spo2 < 90:
        risk_score += 4
        findings.append("Severe hypoxemia")
        alerts.append("CRITICAL: SpO2 below 90%")
        recommendations.append("Urgent evaluation of hypoxemia required")

    elif spo2 < 94:
        risk_score += 2
        findings.append("Borderline oxygenation")

    # ---------------------------------------------
    # BMI
    # ---------------------------------------------
    if bmi >= 30:
        risk_score += 2
        findings.append("Obesity")
        recommendations.append("Use ramped positioning during induction")

    # ---------------------------------------------
    # COMORBIDITIES
    # ---------------------------------------------
    if diabetes:
        risk_score += 1
        findings.append("Diabetes mellitus")

    if hypertension:
        risk_score += 1
        findings.append("Hypertension")

    if copd:
        risk_score += 2
        findings.append("COPD")
        recommendations.append("Optimize bronchodilator therapy")

    # ---------------------------------------------
    # AIRWAY
    # ---------------------------------------------
    if airway_grade >= 3:
        risk_score += 4
        findings.append("Predicted difficult airway")
        alerts.append("Difficult airway anticipated")
        recommendations.append("Prepare difficult airway cart")
        recommendations.append("Consider awake fiberoptic intubation")

    # ---------------------------------------------
    # SURGERY RISK
    # ---------------------------------------------
    surgery_type = surgery_type.lower()

    if "cardiac" in surgery_type:
        risk_score += 3
        findings.append("High-risk cardiac surgery")

    elif "emergency" in surgery_type:
        risk_score += 3
        findings.append("Emergency surgery")

    elif "major" in surgery_type:
        risk_score += 2
        findings.append("Major surgery")

    # ---------------------------------------------
    # ASA CLASS
    # ---------------------------------------------
    if risk_score <= 2:
        asa = "ASA I-II"
        category = "LOW RISK"

    elif risk_score <= 6:
        asa = "ASA III"
        category = "MODERATE RISK"

    else:
        asa = "ASA IV"
        category = "HIGH RISK"

    # ---------------------------------------------
    # POSTOP DESTINATION
    # ---------------------------------------------
    if risk_score >= 8:
        postop = "ICU"
        recommendations.append("Postoperative ICU monitoring advised")

    elif risk_score >= 5:
        postop = "HDU"

    else:
        postop = "Ward"

    # ---------------------------------------------
    # ANESTHESIA PLAN
    # ---------------------------------------------
    anesthesia_plan = []

    if airway_grade >= 3:
        anesthesia_plan.append("Advanced airway preparation required")

    if copd:
        anesthesia_plan.append("Lung protective ventilation strategy")

    if bmi >= 30:
        anesthesia_plan.append("Careful positioning and preoxygenation")

    if spo2 < 90:
        anesthesia_plan.append("Delay elective surgery until optimized")

    # ---------------------------------------------
    # LIMITATIONS
    # ---------------------------------------------
    limitations = [
        "Clinical judgment required",
        "Final decision depends on complete evaluation"
    ]

    # ---------------------------------------------
    # RETURN
    # ---------------------------------------------
    return {
        "asa_class": asa,
        "risk_category": category,
        "risk_score": risk_score,
        "surgery_type": surgery_type,
        "key_findings": findings,
        "critical_alerts": alerts,
        "recommended_plan": anesthesia_plan,
        "recommendations": recommendations,
        "postoperative_destination": postop,
        "confidence": "MODERATE",
        "limitations": limitations
    }


# -------------------------------------------------
# MCP TOOL
# -------------------------------------------------
@mcp.tool()
async def assess_preop_risk(
    age: int,
    spo2: int,
    bmi: float,
    diabetes: bool,
    hypertension: bool,
    copd: bool,
    airway_grade: int,
    surgery_type: str
):
    """
    Advanced perioperative anesthesia risk assessment tool.
    """

    # ---------------------------------------------
    # VALIDATION
    # ---------------------------------------------
    if age <= 0:
        return {"error": "Invalid age"}

    if spo2 <= 0 or spo2 > 100:
        return {"error": "Invalid SpO2"}

    if bmi <= 0 or bmi > 100:
        return {"error": "Invalid BMI"}

    if airway_grade < 1 or airway_grade > 4:
        return {"error": "Airway grade must be between 1 and 4"}

    # tiny async pause
    await asyncio.sleep(0.05)

    result = generate_assessment(
        age,
        spo2,
        bmi,
        diabetes,
        hypertension,
        copd,
        airway_grade,
        surgery_type
    )

    return result


# -------------------------------------------------
# QUICK SCREEN TOOL
# -------------------------------------------------
@mcp.tool()
async def quick_risk(spo2: int):
    """
    Rapid oxygenation risk screening tool.
    """

    await asyncio.sleep(0.02)

    if spo2 < 90:
        return {
            "risk": "HIGH",
            "message": "Severe hypoxemia"
        }

    elif spo2 < 94:
        return {
            "risk": "MODERATE",
            "message": "Borderline oxygenation"
        }

    return {
        "risk": "LOW",
        "message": "Acceptable oxygenation"
    }


# -------------------------------------------------
# HTTP APP
# -------------------------------------------------
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

mcp_app = mcp.http_app(path="/")

app.mount("/mcp", mcp_app)


@app.get("/")
async def root():
    return JSONResponse({
        "status": "healthy",
        "service": "Aegis MCP Server"
    })

# -------------------------------------------------
# RUN SERVER
# -------------------------------------------------
if __name__ == "__main__":
    import os

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )