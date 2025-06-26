from fastapi import APIRouter, Query, Request
from app.core.ai_agent import ask_gemini
from fastapi.responses import JSONResponse
import math

router = APIRouter()

@router.get("/ai")
def ask(prompt: str = Query(..., description="Prompt to Gemini")):
    response = ask_gemini(prompt)
    return {"gemini_response": response}

import math

def db_to_linear(db):
    return 10 ** (db / 10)

def calculate_link_budget(data):
    # Constants
    k = 1.38e-23  # Boltzmann constant (J/K)

    # Extract inputs from user (match frontend input names)
    print("Link budget data received:", data)  # Add this line for debugging
    link_margin_db = float(data.get("link_margin_db", 0))     # dB
    temperature = float(data.get("temperature_k", 290))       # Kelvin
    noise_figure_db = float(data.get("noise_figure_db", 0))   # dB
    bitrate = float(data.get("bitrate", 1e6))                 # bps
    eb_no_db = float(data.get("eb_n0_db", 0))                 # dB

    distance_km = float(data.get("distance", 1))              # km
    frequency_mhz = float(data.get("frequency", 2400))        # MHz
    tx_gain = float(data.get("tx_gain", 0))                   # dBi
    rx_gain = float(data.get("rx_gain", 0))                   # dBi
    system_loss = float(data.get("system_loss_db", 0))        # dB

    # Convert dB values to linear
    link_margin = db_to_linear(link_margin_db)
    nf_linear = db_to_linear(noise_figure_db)
    eb_no_linear = db_to_linear(eb_no_db)

    # Step 1: Calculate Received Power in Watts
    pr_watts = link_margin * k * temperature * nf_linear * bitrate * eb_no_linear

    # Step 2: Convert Pr to dBm
    pr_dbm = 10 * math.log10(pr_watts) + 30

    # Step 3: Calculate FSPL in dB (Free Space)
    fspl = 32.45 + 20 * math.log10(distance_km) + 20 * math.log10(frequency_mhz)

    # Step 4: Calculate required Transmit Power
    pt_dbm = pr_dbm + fspl + system_loss - tx_gain - rx_gain

    return {
        "received_power_dbm": round(pr_dbm, 2),
        "transmit_power_dbm": round(pt_dbm, 2),
        "fspl_db": round(fspl, 2),
        "link_margin_db": round(link_margin_db, 2),
        "noise_figure_db": round(noise_figure_db, 2),
        "bitrate_bps": round(bitrate),
        "eb_no_db": round(eb_no_db, 2),
        "temperature_K": round(temperature),
        "distance_km": round(distance_km, 2),
        "frequency_mhz": round(frequency_mhz, 2),
        "tx_gain_dbi": round(tx_gain, 2),
        "rx_gain_dbi": round(rx_gain, 2),
        "system_loss_db": round(system_loss, 2)
    }

def calculate_ofdm(data):
    # Parse inputs
    bandwidth_khz = float(data.get("bandwidth", 0))
    subcarrier_spacing_khz = float(data.get("subcarrierSpacing", 0))
    print("OFDM data received:", data)  # Add this line for debugging
    modulation = str(data.get("modulation", "QAM"))
    num_symbols_per_rb = int(data.get("numSymbols", 0))
    rb_duration_us = float(data.get("duration_of_RB", 0))
    parallel_rbs = int(data.get("parallelRB", 0))

    # Map modulation to bits per symbol
    modulation_bits_per_symbol = {
        "BPSK": 1,
        "QPSK": 2,
        "8": 3,
        "16": 4,
        "32": 5,
        "64": 6,
        "128": 7,
        "256": 8,
        "1024": 10,
        "4096": 12
        }.get(modulation, 2)  # Default to QPSK if unknown

    # 1. Subcarriers per RB
    rb_bandwidth_hz = bandwidth_khz * 1e3
    subcarrier_spacing_hz = subcarrier_spacing_khz * 1e3
    subcarriers_per_rb = int(rb_bandwidth_hz // subcarrier_spacing_hz) if subcarrier_spacing_hz > 0 else 0

    # 2. Bits per Resource Element (RE)
    bits_per_re = modulation_bits_per_symbol

    # 3. Bits per OFDM Symbol
    bits_per_ofdm_symbol = subcarriers_per_rb * bits_per_re

    # 4. Bits per Resource Block
    bits_per_rb = bits_per_ofdm_symbol * num_symbols_per_rb

    # 5. Max Transmission Rate with Parallel RBs
    total_bits = bits_per_rb * parallel_rbs
    rb_duration_sec = rb_duration_us * 1e-3 if rb_duration_us > 0 else 1  # avoid division by zero
    max_data_rate_bps = total_bits / rb_duration_sec

    # 6. Spectral Efficiency
    total_bandwidth = rb_bandwidth_hz * parallel_rbs
    spectral_efficiency = total_bits / (total_bandwidth * rb_duration_sec) if total_bandwidth > 0 else 0

    return {
        "bandwidth_khz": bandwidth_khz,
        "subcarrier_spacing_khz": subcarrier_spacing_khz,
        "modulation": modulation,
        "modulation_bits_per_symbol": modulation_bits_per_symbol,
        "num_symbols_per_rb": num_symbols_per_rb,
        "rb_duration_us": rb_duration_us,
        "parallel_rbs": parallel_rbs,
        "subcarriers_per_rb": subcarriers_per_rb,
        "bits_per_re": bits_per_re,
        "bits_per_ofdm_symbol": bits_per_ofdm_symbol,
        "bits_per_rb": bits_per_rb,
        "total_bits": total_bits,
        "rb_duration_sec": rb_duration_sec,
        "max_data_rate_bps": max_data_rate_bps,
        "total_bandwidth_hz": total_bandwidth,
        "spectral_efficiency_bps_per_hz": spectral_efficiency
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
    bandwidth_mhz = safe_float(data.get("bandwidth"))
    carrier_freq_mhz = safe_float(data.get("carrierFreq"))
    cell_radius_km = safe_float(data.get("cellRadius"))
    num_cells = safe_int(data.get("numCells"))
    tx_power_dbm = safe_float(data.get("txPower"))
    tx_gain_dbi = safe_float(data.get("txGain"))
    reuse_factor = safe_int(data.get("reuseFactor"), 1)
    user_density = safe_float(data.get("userDensity"))
    user_data_rate_kbps = safe_float(data.get("userDataRate"))
    snr_db = safe_float(data.get("snr"))
    ci_db = safe_float(data.get("ci"))
    traffic_demand_erlangs = safe_float(data.get("trafficDemand"))

    # Derived/calculated values
    area_per_cell_km2 = 3 * math.pi * (cell_radius_km ** 2) / 2  # Hexagonal cell area
    total_area_km2 = area_per_cell_km2 * num_cells
    total_users = user_density * total_area_km2
    users_per_cell = user_density * area_per_cell_km2

    # Frequency reuse
    total_bandwidth_hz = bandwidth_mhz * 1e6
    bandwidth_per_cell_hz = total_bandwidth_hz / reuse_factor if reuse_factor > 0 else 0

    # Cell capacity (Shannon, theoretical, for reference)
    snr_linear = 10 ** (snr_db / 10) if snr_db is not None else 0
    if snr_linear > 0 and bandwidth_per_cell_hz > 0:
        shannon_capacity_bps = bandwidth_per_cell_hz * (math.log2(1 + snr_linear))
    else:
        shannon_capacity_bps = 0

    # User support per cell (based on data rate per user)
    user_data_rate_bps = user_data_rate_kbps * 1e3
    if user_data_rate_bps > 0:
        max_users_per_cell = shannon_capacity_bps // user_data_rate_bps
    else:
        max_users_per_cell = 0

    # C/I margin (for frequency planning)
    ci_linear = 10 ** (ci_db / 10) if ci_db is not None else 0

    # Traffic calculations (Erlang B, simple estimate)
    traffic_per_cell = traffic_demand_erlangs

    return {
        "bandwidth_mhz": bandwidth_mhz,
        "carrier_freq_mhz": carrier_freq_mhz,
        "cell_radius_km": cell_radius_km,
        "num_cells": num_cells,
        "tx_power_dbm": tx_power_dbm,
        "tx_gain_dbi": tx_gain_dbi,
        "reuse_factor": reuse_factor,
        "user_density_per_km2": user_density,
        "user_data_rate_kbps": user_data_rate_kbps,
        "snr_db": snr_db,
        "ci_db": ci_db,
        "traffic_demand_erlangs": traffic_demand_erlangs,
        "area_per_cell_km2": area_per_cell_km2,
        "total_area_km2": total_area_km2,
        "total_users": total_users,
        "users_per_cell": users_per_cell,
        "bandwidth_per_cell_hz": bandwidth_per_cell_hz,
        "shannon_capacity_bps": shannon_capacity_bps,
        "max_users_per_cell": int(max_users_per_cell),
        "traffic_per_cell_erlangs": traffic_per_cell,
        "ci_linear": ci_linear
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
        # Compose rich Gemini prompt for link budget
        prompt = f"""
            You are a wireless link budget analysis expert. Based on the following user inputs and computed results, provide a detailed explanation of how each parameter and result affects the received power, transmit power, and link performance. Explain the significance of each metric and how the configuration impacts the reliability and performance of the wireless link.

            User Inputs:
            - Link Margin (dB): {calculation['link_margin_db']}
            - Temperature (K): {calculation['temperature_K']}
            - Noise Figure (dB): {calculation['noise_figure_db']}
            - Bitrate (bps): {calculation['bitrate_bps']}
            - Eb/N0 (dB): {calculation['eb_no_db']}
            - Distance (km): {calculation['distance_km']}
            - Frequency (MHz): {calculation['frequency_mhz']}
            - Transmitter Gain (dBi): {calculation['tx_gain_dbi']}
            - Receiver Gain (dBi): {calculation['rx_gain_dbi']}
            - System Loss (dB): {calculation['system_loss_db']}

            Computed Results:
            - Received Power (dBm): {calculation['received_power_dbm']}
            - Required Transmit Power (dBm): {calculation['transmit_power_dbm']}
            - Free Space Path Loss (FSPL, dB): {calculation['fspl_db']}

            Discuss how these values are derived and their importance in wireless link design.
            """
        gemini_response = ask_gemini(prompt)
        return JSONResponse({"calculation": calculation, "gemini": gemini_response})

    elif scenario == "ofdm":
        calculation = calculate_ofdm(data)
        if "error" in calculation:
            return JSONResponse({"error": calculation["error"], "gemini": None})
        # Compose updated Gemini prompt for OFDM
        prompt = f"""
            You are an OFDM systems expert. Based on the following user inputs and computed results, provide a detailed explanation of how each parameter and result affects the data rates, resource allocation, and spectral efficiency in the OFDM system. Explain the significance of each metric and how the configuration impacts the maximum transmission capacity and efficiency.

            User Inputs:
            - Bandwidth: {data.get('bandwidth')} kHz
            - Subcarrier Spacing: {data.get('subcarrierSpacing')} kHz
            - Modulation: {data.get('modulation')}
            - Number of OFDM Symbols per RB: {data.get('numSymbols')}
            - Duration of RB: {data.get('duration_of_RB')} ms
            - Parallel RBs: {data.get('parallelRB')}

            Computed Results:
            - Subcarriers per RB: {calculation['subcarriers_per_rb']}
            - Bits per Resource Element: {calculation['bits_per_re']}
            - Bits per OFDM Symbol: {calculation['bits_per_ofdm_symbol']}
            - Bits per Resource Block: {calculation['bits_per_rb']}
            - Total Bits (all parallel RBs): {calculation['total_bits']}
            - RB Duration (s): {calculation['rb_duration_sec']:.6f}
            - Max Data Rate: {calculation['max_data_rate_bps']:.2f} bps
            - Total Bandwidth: {calculation['total_bandwidth_hz'] / 1e3:.2f} kHz
            - Spectral Efficiency: {calculation['spectral_efficiency_bps_per_hz']:.4f} bps/Hz

            Discuss how these values are derived and their importance in OFDM system design.
            """
        gemini_response = ask_gemini(prompt)
        return JSONResponse({"result": calculation, "gemini": gemini_response})

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
        if "error" in calculation:
            return JSONResponse({"error": calculation["error"], "gemini": None})
        # Compose rich Gemini prompt for cellular
        prompt = f"""
            You are a cellular network design expert. Based on the following user inputs and computed results, provide a detailed explanation of how each parameter and result affects the design, capacity, and performance of the cellular system. Explain the significance of each metric and how the configuration impacts user support, area coverage, and spectral efficiency.

            User Inputs:
            - Bandwidth: {data.get('bandwidth')} MHz
            - Carrier Frequency: {data.get('carrierFreq')} MHz
            - Cell Radius: {data.get('cellRadius')} km
            - Number of Cells: {data.get('numCells')}
            - Transmission Power: {data.get('txPower')} dBm
            - Transmit Antenna Gain: {data.get('txGain')} dBi
            - Frequency Reuse Factor: {data.get('reuseFactor')}
            - User Density: {data.get('userDensity')} users/km²
            - User Data Rate: {data.get('userDataRate')} kbps
            - SNR: {data.get('snr')} dB
            - C/I: {data.get('ci')} dB
            - Traffic Demand: {data.get('trafficDemand')} Erlangs

            Computed Results:
            - Area per Cell: {calculation['area_per_cell_km2']:.2f} km²
            - Total Area: {calculation['total_area_km2']:.2f} km²
            - Total Users: {calculation['total_users']:.2f}
            - Users per Cell: {calculation['users_per_cell']:.2f}
            - Bandwidth per Cell: {calculation['bandwidth_per_cell_hz'] / 1e6:.2f} MHz
            - Shannon Capacity per Cell: {calculation['shannon_capacity_bps'] / 1e6:.2f} Mbps
            - Max Users per Cell: {calculation['max_users_per_cell']}
            - Traffic per Cell: {calculation['traffic_per_cell_erlangs']:.2f} Erlangs
            - C/I (linear): {calculation['ci_linear']:.2f}

            Discuss how these values are derived and their importance in cellular network design.
            """
        gemini_response = ask_gemini(prompt)
        return JSONResponse({"calculation": calculation, "gemini": gemini_response})

    else:
        return JSONResponse({"error": "Unknown scenario", "gemini": None})
