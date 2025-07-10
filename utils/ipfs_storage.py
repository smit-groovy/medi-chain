import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_SECRET_KEY = os.getenv("PINATA_SECRET_KEY")

PINATA_BASE_URL = "https://api.pinata.cloud/"
PIN_FILE_URL = PINATA_BASE_URL + "pinning/pinFileToIPFS"
LIST_PINS_URL = PINATA_BASE_URL + "data/pinList"
GATEWAY_URL = "https://ipfs.io/ipfs/"

HEADERS = {
    "pinata_api_key": PINATA_API_KEY,
    "pinata_secret_api_key": PINATA_SECRET_KEY
}


def upload_file_to_ipfs(filepath: str) -> str:
    try:
        filename = os.path.basename(filepath)

        # Extract folder-like metadata from local path
        relative_path = os.path.relpath(filepath, "data")  # strip off `data/`
        pinata_metadata = {
            "name": relative_path
        }

        with open(filepath, "rb") as f:
            files = {
                "file": (filename, f),
                "pinataMetadata": (None, json.dumps(pinata_metadata), "application/json")
            }

            response = requests.post(PIN_FILE_URL, files=files, headers=HEADERS)

        if response.status_code == 200:
            ipfs_hash = response.json()["IpfsHash"]
            print(f"📤 Uploaded to IPFS: {ipfs_hash}")
            return ipfs_hash
        else:
            print(f"❌ Upload failed: {response.text}")
            return "Upload failed"

    except Exception as e:
        print(f"⚠️ Upload error: {e}")
        return "Upload failed"


def list_user_appointment_files(wallet_address: str) -> list:
    """Fetch all pinned files matching the user's folder prefix."""
    folder_prefix = f"{wallet_address}_appointments/"
    try:
        params = {
            "status": "pinned",
            "pageLimit": 1000,
            "metadata[name]": folder_prefix
        }
        response = requests.get(LIST_PINS_URL, headers=HEADERS, params=params)

        if response.status_code != 200:
            print("⚠️ Could not fetch pinned files")
            return []

        pins = response.json().get("rows", [])
        return pins
    except Exception as e:
        print(f"⚠️ Error fetching files: {e}")
        return []


def download_json_from_cid(cid: str) -> dict:
    try:
        response = requests.get(f"{GATEWAY_URL}{cid}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ Failed to download from IPFS: {cid}")
            return {}
    except Exception as e:
        print(f"⚠️ Exception while downloading from IPFS: {e}")
        return {}
