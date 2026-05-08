from fastmcp import FastMCP, FastMCPApp

from prefab_ui.app import PrefabApp
from prefab_ui.components import (
    Column,
    Heading,
    Text,
    Form,
    Input,
    Button
)

from prefab_ui.actions.mcp import CallTool
from prefab_ui.actions import SetState
from prefab_ui.rx import RESULT

# Create MCP server
mcp = FastMCP("Aegis Anesthesia")

# Create App
app = FastMCPApp("Preop Assessment")


# -----------------------------
# Backend Tool
# -----------------------------
@app.tool()
def airway_risk(
    mallampati: str,
    mouth_opening: str,
    neck_mobility: str
) -> str:

    risks = []

    if mallampati in ["III", "IV"]:
        risks.append("Potential difficult airway")

    if mouth_opening == "Limited":
        risks.append("Restricted mouth opening")

    if neck_mobility == "Reduced":
        risks.append("Reduced cervical mobility")

    if len(risks) == 0:
        return "Airway assessment appears low risk"

    return " | ".join(risks)

# -----------------------------
# UI App
# -----------------------------
@app.ui()
def preop_app():

    with Column(gap=4, css_class="p-6") as view:

        Heading("Aegis Preoperative Assessment")

        Text("Airway Assessment")

        with Form(
            on_submit=CallTool(
                "airway_risk",
                on_success=SetState("result", RESULT)
            )
        ):

            Input(
                name="mallampati",
                label="Mallampati Grade (I/II/III/IV)"
            )

            Input(
                name="mouth_opening",
                label="Mouth Opening (Normal/Limited)"
            )

            Input(
                name="neck_mobility",
                label="Neck Mobility (Normal/Reduced)"
            )

            Button("Assess Airway")

        Text("Assessment Result:")

        Text("{result}")

    return PrefabApp(
        view=view,
        state={
            "result": "Waiting for assessment..."
        }
    )


# Add app to server
mcp.add_provider(app)

# Run server
if __name__ == "__main__":
    mcp.run()