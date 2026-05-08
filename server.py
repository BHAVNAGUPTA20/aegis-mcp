from fastmcp import FastMCP

mcp = FastMCP("Aegis MCP")


@mcp.tool()
def assess_patient(age: int, spo2: int) -> str:
    """
    Simple anesthesia risk assessment
    """

    if spo2 < 90:
        return f"High risk patient. Age: {age}, SpO2: {spo2}"

    return f"Stable patient. Age: {age}, SpO2: {spo2}"


if __name__ == "__main__":
    mcp.run()