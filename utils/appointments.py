import os
import json
from datetime import datetime

from utils.ipfs_storage import upload_file_to_ipfs, list_user_appointment_files, download_json_from_cid

DATA_DIR = "data"

def get_user_folder(wallet_address):
    folder = os.path.join(DATA_DIR, f"{wallet_address}_appointments")
    os.makedirs(folder, exist_ok=True)
    return folder

def get_user_file_path(wallet_address: str) -> str:
    folder = get_user_folder(wallet_address)
    timestamp = datetime.now().isoformat().replace(":", "-").replace(".", "-")
    return os.path.join(folder, f"appointment_{timestamp}.json")

def save_appointment(wallet: str, **appointment):
    filepath = get_user_file_path(wallet)
    
    # Save locally
    with open(filepath, "w") as f:
        json.dump(appointment, f, indent=2)

    # Upload to Pinata
    cid = upload_file_to_ipfs(filepath)
    return cid

def load_appointments_by_wallet(wallet_address: str) -> list:
    pins = list_user_appointment_files(wallet_address)
    appointments = []

    for pin in pins:
        cid = pin.get("ipfs_pin_hash")
        if not cid:
            continue
        data = download_json_from_cid(cid)
        if isinstance(data, dict):
            appointments.append(data)

    return appointments
