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

def safe_float(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def safe_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def calculate_wireless_comm(data):
    try:
        bandwidth_khz = safe_float(data.get("bandwidth"))
        if bandwidth_khz is None or bandwidth_khz <= 0:
            return {"error": "Bandwidth must be greater than 0."}
        bandwidth_hz = bandwidth_khz * 1e3

        sampling_rate = safe_float(data.get("samplingRate"), 2 * bandwidth_hz)
        if sampling_rate <= 0:
            return {"error": "Sampling rate must be greater than 0."}

        quant_bits = safe_int(data.get("quantBits"))
        if quant_bits is None or not (1 <= quant_bits <= 32):
            return {"error": "Quantization bits must be between 1 and 32."}

        source_enc_rate = safe_float(data.get("sourceEncoderRate"))
        if source_enc_rate is None or not (0 < source_enc_rate <= 1):
            return {"error": "Source encoder rate must be between 0 and 1."}

        channel_enc_rate = safe_float(data.get("channelEncoderRate"))
        if channel_enc_rate is None or not (0 < channel_enc_rate <= 1):
            return {"error": "Channel encoder rate must be between 0 and 1."}

        interleaver_rate = safe_float(data.get("interleaverRate"), 1)
        if interleaver_rate < 1:
            return {"error": "Interleaver rate must be ≥ 1."}

        burst_length = safe_float(data.get("burstLength"))
        if burst_length is None or burst_length <= 0:
            return {"error": "Burst length must be > 0."}

        # Step-by-step computation
        rate_sampler = sampling_rate
        rate_quantizer = rate_sampler * quant_bits
        rate_source_encoder = rate_quantizer * source_enc_rate
        rate_channel_encoder = rate_source_encoder / channel_enc_rate
        rate_interleaver = rate_channel_encoder * interleaver_rate
        rate_burst_formatter = rate_interleaver * burst_length

        return {
            "sampler_rate_bps": rate_sampler,
            "quantizer_rate_bps": rate_quantizer,
            "source_encoder_rate_bps": rate_source_encoder,
            "channel_encoder_rate_bps": rate_channel_encoder,
            "interleaver_rate_bps": rate_interleaver,
            "burst_formatter_rate_bps": rate_burst_formatter
        }

    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}



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
        return JSONResponse({"calculation": calculation, "gemini": gemini_response})

    elif scenario == "ofdm":
        calculation = calculate_ofdm(data)
        summary = f"OFDM Calculation Results: {calculation}"
        gemini_response = ask_gemini(f"Discuss the following results for OFDM: {summary}")
        return JSONResponse({"calculation": calculation, "gemini": gemini_response})

    elif scenario == "wireless_comm":
        calculation = calculate_wireless_comm(data)

        if "error" in calculation:
            return JSONResponse({"error": calculation["error"], "gemini": None})

        # Compose rich Gemini prompt
        prompt = f"""
            You are a communication systems expert. A wireless communication system has passed through several blocks. Based on the following inputs and their corresponding computed data rates, provide a detailed explanation of how the data rate changes at each block and why.

            User Inputs:
            - Bandwidth: {data.get("bandwidth")} kHz
            - Sampling Rate: {data.get("samplingRate") or 'Auto (2×Bandwidth)'} Hz
            - Quantization Bits: {data.get("quantBits")}
            - Source Encoder Rate: {data.get("sourceEncoderRate")}
            - Channel Encoder Rate: {data.get("channelEncoderRate")}
            - Interleaver Rate: {data.get("interleaverRate")}
            - Burst Length: {data.get("burstLength")}

            Computed Output Rates:
            - Sampler Rate: {calculation['sampler_rate_bps']:.2f} bps
            - Quantizer Rate: {calculation['quantizer_rate_bps']:.2f} bps
            - Source Encoder Rate: {calculation['source_encoder_rate_bps']:.2f} bps
            - Channel Encoder Rate: {calculation['channel_encoder_rate_bps']:.2f} bps
            - Interleaver Rate: {calculation['interleaver_rate_bps']:.2f} bps
            - Burst Formatter Rate: {calculation['burst_formatter_rate_bps']:.2f} bps

            Explain the role of each block and how the rate evolves through the pipeline.
            """
        gemini_response = ask_gemini(prompt)
        return JSONResponse({"gemini": gemini_response})

    elif scenario == "cellular":
        calculation = calculate_cellular(data)
        summary = f"Cellular Calculation Results: {calculation}"
        gemini_response = ask_gemini(f"Discuss the following results for cellular: {summary}")
        return JSONResponse({"calculation": calculation, "gemini": gemini_response})

    else:
        return JSONResponse({"error": "Unknown scenario", "gemini": None})
