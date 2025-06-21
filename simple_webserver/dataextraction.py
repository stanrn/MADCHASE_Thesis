import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo


def extract_cfr_from_json(data, tx_id=0, rx_id=1):
    """
    Extract channel frequency response and metadata from a raw measurement JSON.
    This is just used to send measurement data to user, more post processing is needed later
    
    Parameters:
        data (dict): The raw measurement JSON.
        tx_id (int): Transmitter device ID.
        rx_id (int): Receiver device ID.
    
    Returns:
        dict: Processed result containing metadata and complex CFR.
    """
    # Extract baseband I/Q samples
    i_local = np.array(data["i_local"])
    q_local = np.array(data["q_local"])
    i_remote = np.array(data["i_remote"])
    q_remote = np.array(data["q_remote"])

    # Reconstruct complex signals
    local_complex = i_local + 1j * q_local
    remote_complex = i_remote + 1j * q_remote

    # Normalize to float32 (if needed)
    max_val = 8192.0  # Based on 13-bit signed fixed point range
    local_complex = local_complex / max_val
    remote_complex = remote_complex / max_val

    # Reorder using hopping sequence
    hopping_sequence = data["hopping_sequence"]
    H_f = np.full(80, np.nan, dtype=np.complex64)  # Initialize CFR array

    for i, ch in enumerate(hopping_sequence):
        if 0 <= ch < 80:
            H_f[ch] = remote_complex[i] / local_complex[i] if local_complex[i] != 0 else np.nan

    # Corresponding frequency vector in Hz (BLE: 2402 + 2*k MHz)
    freqs = np.array([2402e6 + 2e6 * k for k in range(80)])

    # Extract metadata
    result = {
        "tx_id": tx_id,
        "rx_id": rx_id,
        "timestamp" : datetime.now(ZoneInfo("Europe/Brussels")).strftime("%d-%m-%Y %H:%M:%S.%f"),
        "frequencies": freqs.tolist(),
        "cfr_real": H_f.real.tolist(),
        "cfr_imag": H_f.imag.tolist(),
        "rssi_local_dB": data.get("rssi_local[dB]", None),
        "rssi_remote_dB": data.get("rssi_remote[dB]", None),
        "txpwr_local_dB": data.get("txpwr_local[dB]", None),
        "txpwr_remote_dB": data.get("txpwr_remote[dB]", None),
        "link_loss_dB": data.get("link_loss[dB]", None),
        "delay_spread_ns": data.get("duration[us]", 0) * 1e3,
        "estimated_distance_mm": data.get("best[mm]", None),
        "quality": data.get("quality", None)
    }

    return result
