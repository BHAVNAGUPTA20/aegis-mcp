from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import uvicorn
import os

# -------------------------------------------------
# APP
# -------------------------------------------------
app = FastAPI(title="Aegis Anesthesia Risk App", version="1.0.0")


# -------------------------------------------------
# REQUEST MODEL
# -------------------------------------------------
class AssessmentRequest(BaseModel):
    age: int = Field(..., ge=1, le=120)
    spo2: int = Field(..., ge=1, le=100)
    bmi: float = Field(..., gt=0, le=100)
    diabetes: bool = False
    hypertension: bool = False
    copd: bool = False
    airway_grade: int = Field(..., ge=1, le=4)
    surgery_type: str = Field(..., min_length=1, max_length=200)


# -------------------------------------------------
# CLINICAL LOGIC
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

    # AGE
    if age >= 65:
        risk_score += 2
        findings.append("Elderly patient")

    # SPO2
    if spo2 < 90:
        risk_score += 4
        findings.append("Severe hypoxemia")
        alerts.append("CRITICAL: SpO2 below 90%")
        recommendations.append("Urgent evaluation of hypoxemia required")
    elif spo2 < 94:
        risk_score += 2
        findings.append("Borderline oxygenation")

    # BMI
    if bmi >= 30:
        risk_score += 2
        findings.append("Obesity")
        recommendations.append("Use ramped positioning during induction")

    # COMORBIDITIES
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

    # AIRWAY
    if airway_grade >= 3:
        risk_score += 4
        findings.append("Predicted difficult airway")
        alerts.append("Difficult airway anticipated")
        recommendations.append("Prepare difficult airway cart")
        recommendations.append("Consider awake fiberoptic intubation")

    # SURGERY RISK
    surgery_type = (surgery_type or "").lower()

    if "cardiac" in surgery_type:
        risk_score += 3
        findings.append("High-risk cardiac surgery")
    elif "emergency" in surgery_type:
        risk_score += 3
        findings.append("Emergency surgery")
    elif "major" in surgery_type:
        risk_score += 2
        findings.append("Major surgery")

    # ASA CLASS
    if risk_score <= 2:
        asa = "ASA I-II"
        category = "LOW RISK"
    elif risk_score <= 6:
        asa = "ASA III"
        category = "MODERATE RISK"
    else:
        asa = "ASA IV"
        category = "HIGH RISK"

    # POSTOP DESTINATION
    if risk_score >= 8:
        postop = "ICU"
        recommendations.append("Postoperative ICU monitoring advised")
    elif risk_score >= 5:
        postop = "HDU"
    else:
        postop = "Ward"

    # ANESTHESIA PLAN
    anesthesia_plan = []

    if airway_grade >= 3:
        anesthesia_plan.append("Advanced airway preparation required")

    if copd:
        anesthesia_plan.append("Lung protective ventilation strategy")

    if bmi >= 30:
        anesthesia_plan.append("Careful positioning and preoxygenation")

    if spo2 < 90:
        anesthesia_plan.append("Delay elective surgery until optimized")

    # LIMITATIONS
    limitations = [
        "Clinical judgment required",
        "Final decision depends on complete evaluation"
    ]

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


def quick_risk_logic(spo2: int):
    if spo2 < 90:
        return {
            "risk": "HIGH",
            "message": "Severe hypoxemia"
        }

    if spo2 < 94:
        return {
            "risk": "MODERATE",
            "message": "Borderline oxygenation"
        }

    return {
        "risk": "LOW",
        "message": "Acceptable oxygenation"
    }


# -------------------------------------------------
# WEB PAGE
# -------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Aegis Anesthesia Risk App</title>
        <style>
            :root {
                color-scheme: dark;
                --bg: #0f1220;
                --panel: #171a2b;
                --panel2: #1e2238;
                --text: #f3f4f6;
                --muted: #a9afc3;
                --accent: #8b5cf6;
                --good: #10b981;
                --warn: #f59e0b;
                --bad: #ef4444;
                --border: #2b314d;
            }
            * { box-sizing: border-box; }
            body {
                margin: 0;
                font-family: Inter, Segoe UI, Arial, sans-serif;
                background: radial-gradient(circle at top, #171a2b 0%, var(--bg) 55%);
                color: var(--text);
                min-height: 100vh;
            }
            .wrap {
                max-width: 1180px;
                margin: 0 auto;
                padding: 28px 18px 40px;
            }
            .hero {
                display: grid;
                grid-template-columns: 1.1fr 0.9fr;
                gap: 18px;
                align-items: stretch;
            }
            .card {
                background: rgba(23, 26, 43, 0.92);
                border: 1px solid var(--border);
                border-radius: 22px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.25);
                padding: 22px;
            }
            h1 {
                margin: 0 0 10px;
                font-size: 2rem;
                line-height: 1.1;
            }
            p {
                color: var(--muted);
                line-height: 1.6;
            }
            .badges {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-top: 14px;
            }
            .badge {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                border: 1px solid var(--border);
                background: var(--panel2);
                padding: 8px 12px;
                border-radius: 999px;
                font-size: 0.92rem;
                color: var(--text);
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 12px;
                margin-top: 16px;
            }
            .field {
                display: flex;
                flex-direction: column;
                gap: 7px;
            }
            .field label {
                font-size: 0.88rem;
                color: var(--muted);
            }
            .field input, .field select {
                border: 1px solid var(--border);
                background: #101425;
                color: var(--text);
                border-radius: 14px;
                padding: 12px 14px;
                font-size: 1rem;
                outline: none;
            }
            .field input:focus, .field select:focus {
                border-color: var(--accent);
                box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.18);
            }
            .checks {
                display: flex;
                gap: 14px;
                flex-wrap: wrap;
                margin-top: 2px;
            }
            .check {
                display: flex;
                align-items: center;
                gap: 8px;
                background: #101425;
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 10px 12px;
            }
            .check input {
                width: 18px;
                height: 18px;
                accent-color: var(--accent);
            }
            .full {
                grid-column: 1 / -1;
            }
            .actions {
                display: flex;
                gap: 12px;
                flex-wrap: wrap;
                margin-top: 16px;
            }
            button {
                border: none;
                border-radius: 14px;
                padding: 12px 16px;
                font-size: 0.98rem;
                font-weight: 600;
                cursor: pointer;
            }
            .primary {
                background: var(--accent);
                color: white;
            }
            .secondary {
                background: #2b314d;
                color: var(--text);
            }
            .output {
                margin-top: 18px;
                background: #0d1020;
                border: 1px solid var(--border);
                border-radius: 18px;
                padding: 16px;
                min-height: 360px;
                white-space: pre-wrap;
                overflow: auto;
                font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
                font-size: 0.92rem;
                line-height: 1.5;
            }
            .small {
                font-size: 0.88rem;
                color: var(--muted);
                margin-top: 10px;
            }
            .status {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 8px 12px;
                border-radius: 999px;
                background: rgba(16, 185, 129, 0.12);
                color: #7ee2bc;
                border: 1px solid rgba(16, 185, 129, 0.25);
                margin-bottom: 12px;
                font-size: 0.92rem;
            }
            .right h2 {
                margin: 0 0 12px;
                font-size: 1.15rem;
            }
            .list {
                margin: 0;
                padding-left: 18px;
                color: var(--muted);
                line-height: 1.7;
            }
            .footer {
                margin-top: 16px;
                color: var(--muted);
                font-size: 0.88rem;
            }
            @media (max-width: 900px) {
                .hero { grid-template-columns: 1fr; }
                .grid { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="wrap">
            <div class="hero">
                <div class="card">
                    <div class="status">Online • Aegis Anesthesia Risk App</div>
                    <h1>Preoperative anesthesia risk assessment</h1>
                    <p>
                        Enter the patient details below to generate a structured anesthesia risk summary.
                        The scoring logic includes age, oxygenation, BMI, comorbidities, airway grade, and surgery type.
                    </p>

                    <form id="assessmentForm">
                        <div class="grid">
                            <div class="field">
                                <label for="age">Age</label>
                                <input id="age" type="number" min="1" max="120" value="45" required />
                            </div>

                            <div class="field">
                                <label for="spo2">SpO2 (%)</label>
                                <input id="spo2" type="number" min="1" max="100" value="98" required />
                            </div>

                            <div class="field">
                                <label for="bmi">BMI</label>
                                <input id="bmi" type="number" min="0.1" step="0.1" value="24.5" required />
                            </div>

                            <div class="field">
                                <label for="airway_grade">Airway grade</label>
                                <select id="airway_grade" required>
                                    <option value="1">1</option>
                                    <option value="2" selected>2</option>
                                    <option value="3">3</option>
                                    <option value="4">4</option>
                                </select>
                            </div>

                            <div class="field full">
                                <label for="surgery_type">Surgery type</label>
                                <input id="surgery_type" type="text" value="Major abdominal surgery" required />
                            </div>

                            <div class="field full">
                                <label>Comorbidities</label>
                                <div class="checks">
                                    <div class="check">
                                        <input id="diabetes" type="checkbox" />
                                        <label for="diabetes">Diabetes</label>
                                    </div>
                                    <div class="check">
                                        <input id="hypertension" type="checkbox" />
                                        <label for="hypertension">Hypertension</label>
                                    </div>
                                    <div class="check">
                                        <input id="copd" type="checkbox" />
                                        <label for="copd">COPD</label>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="actions">
                            <button type="submit" class="primary">Assess Risk</button>
                            <button type="button" id="quickRiskBtn" class="secondary">Quick SpO2 Risk</button>
                        </div>
                    </form>

                    <div class="small">
                        API endpoints: <code>/health</code>, <code>/api/assess</code>, <code>/api/quick-risk/{spo2}</code>
                    </div>

                    <div id="output" class="output">Waiting for input...</div>
                </div>

                <div class="card right">
                    <h2>What this page does</h2>
                    <ul class="list">
                        <li>Uses the anesthesia scoring rules already in your file.</li>
                        <li>Shows ASA class, risk score, alerts, recommendations, and postoperative destination.</li>
                        <li>Returns a browser-friendly JSON summary for quick testing on Railway.</li>
                        <li>Gives Railway a clean root route and health check so the app stays up.</li>
                    </ul>

                    <div class="footer">
                        This is the stable browser-facing version. If you later want a true MCP transport again,
                        it should be added after the Railway deployment is stable.
                    </div>
                </div>
            </div>
        </div>

        <script>
            const output = document.getElementById("output");
            const form = document.getElementById("assessmentForm");

            function getPayload() {
                return {
                    age: Number(document.getElementById("age").value),
                    spo2: Number(document.getElementById("spo2").value),
                    bmi: Number(document.getElementById("bmi").value),
                    diabetes: document.getElementById("diabetes").checked,
                    hypertension: document.getElementById("hypertension").checked,
                    copd: document.getElementById("copd").checked,
                    airway_grade: Number(document.getElementById("airway_grade").value),
                    surgery_type: document.getElementById("surgery_type").value.trim()
                };
            }

            form.addEventListener("submit", async (e) => {
                e.preventDefault();
                output.textContent = "Running assessment...";

                try {
                    const response = await fetch("/api/assess", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify(getPayload())
                    });

                    const data = await response.json();

                    output.textContent = JSON.stringify(data, null, 2);
                } catch (error) {
                    output.textContent = "Error: " + error.message;
                }
            });

            document.getElementById("quickRiskBtn").addEventListener("click", async () => {
                const spo2 = Number(document.getElementById("spo2").value);
                output.textContent = "Checking quick SpO2 risk...";

                try {
                    const response = await fetch(`/api/quick-risk/${spo2}`);
                    const data = await response.json();
                    output.textContent = JSON.stringify(data, null, 2);
                } catch (error) {
                    output.textContent = "Error: " + error.message;
                }
            });
        </script>
    </body>
    </html>
    """


# -------------------------------------------------
# HEALTH
# -------------------------------------------------
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "Aegis Anesthesia Risk App"
    }


# -------------------------------------------------
# API
# -------------------------------------------------
@app.post("/api/assess")
async def assess(payload: AssessmentRequest):
    return generate_assessment(
        age=payload.age,
        spo2=payload.spo2,
        bmi=payload.bmi,
        diabetes=payload.diabetes,
        hypertension=payload.hypertension,
        copd=payload.copd,
        airway_grade=payload.airway_grade,
        surgery_type=payload.surgery_type
    )


@app.get("/api/quick-risk/{spo2}")
async def quick_risk(spo2: int):
    if spo2 < 1 or spo2 > 100:
        raise HTTPException(status_code=400, detail="SpO2 must be between 1 and 100")

    return quick_risk_logic(spo2)


# -------------------------------------------------
# RUN SERVER
# -------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("server:app", host="0.0.0.0", port=port)