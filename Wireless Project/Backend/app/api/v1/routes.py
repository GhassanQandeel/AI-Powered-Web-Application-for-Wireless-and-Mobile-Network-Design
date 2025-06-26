from fastapi import APIRouter, Query, Request
from app.core.ai_agent import ask_gemini
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/ai")
def ask(prompt: str = Query(..., description="Prompt to Gemini")):
    response = ask_gemini(prompt)
    return {"gemini_response": response}

def calculate_link_budget(data):
    tx_gain = float(data.get("txGain", 0))
    rx_gain = float(data.get("rxGain", 0))
    frequency = float(data.get("frequency", 0))
    distance = float(data.get("distance", 0))
    system_loss = float(data.get("systemLoss", 0))
    # ... add more as needed
    return {
        "tx_gain": tx_gain,
        "rx_gain": rx_gain,
        "frequency": frequency,
        "distance": distance,
        "system_loss": system_loss,
        "example_result": tx_gain + rx_gain - system_loss  # placeholder
    }

def calculate_ofdm(data):
    num_subcarriers = int(data.get("numSubcarriers", 0))
    symbol_duration = float(data.get("symbolDuration", 0))
    cyclic_prefix = float(data.get("cyclicPrefix", 0))
    bandwidth = float(data.get("bandwidth", 0))
    return {
        "num_subcarriers": num_subcarriers,
        "symbol_duration": symbol_duration,
        "cyclic_prefix": cyclic_prefix,
        "bandwidth": bandwidth,
        "example_result": num_subcarriers * bandwidth  # placeholder
    }

def calculate_wireless_comm(data):
    snr = float(data.get("snr", 0))
    bandwidth = float(data.get("bandwidth", 0))
    modulation = data.get("modulation", "")
    return {
        "snr": snr,
        "bandwidth": bandwidth,
        "modulation": modulation,
        "example_result": snr * bandwidth  # placeholder
    }

def calculate_cellular(data):
    cell_radius = float(data.get("cellRadius", 0))
    num_users = int(data.get("numUsers", 0))
    frequency_reuse = int(data.get("frequencyReuse", 1))
    return {
        "cell_radius": cell_radius,
        "num_users": num_users,
        "frequency_reuse": frequency_reuse,
        "example_result": num_users / frequency_reuse  # placeholder
    }

@router.post("/calculate")
async def calculate(request: Request):
    body = await request.json()
    scenario = body.get("scenario")
    data = body.get("data")
    calculation = None
    gemini_response = None

    if scenario == "link_budget":
        calculation = calculate_link_budget(data)
        summary = f"Link Budget Calculation Results: {calculation}"
        gemini_response = ask_gemini(f"Discuss the following results for link budget: {summary}")
    elif scenario == "ofdm":
        calculation = calculate_ofdm(data)
        summary = f"OFDM Calculation Results: {calculation}"
        gemini_response = ask_gemini(f"Discuss the following results for OFDM: {summary}")
    elif scenario == "wireless_comm":
        calculation = calculate_wireless_comm(data)
        summary = f"Wireless Communication Calculation Results: {calculation}"
        gemini_response = ask_gemini(f"Discuss the following results for wireless communication: {summary}")
    elif scenario == "cellular":
        calculation = calculate_cellular(data)
        summary = f"Cellular Calculation Results: {calculation}"
        gemini_response = ask_gemini(f"Discuss the following results for cellular: {summary}")
    else:
        calculation = {"error": "Unknown scenario"}
        gemini_response = None
    return JSONResponse({"calculation": calculation, "gemini": gemini_response})
