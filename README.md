## 🩺 MediChain - Decentralized AI Medical Assistant & Appointment Booking

MediChain is a decentralized medical assistant and appointment booking system powered by Streamlit, LangChain, IPFS (via Pinata), and MetaMask. It leverages Web3 technology to ensure patient data privacy and transparency while offering AI-based medical explanations.

---

## 📁 Project Structure

```text
medichain/
├── app.py                  # Streamlit UI
├── data/
│   └── {wallet}_appointments/
│       └── appointment_<timestamp>.json
├── graph/
│   └── appointment_flow.py # LangGraph-based appointment logic
├── utils/
│   ├── appointments.py     # Save/load appointment files
│   ├── ipfs_storage.py     # Upload/download via Pinata IPFS
│   └── wallet.py           # MetaMask wallet connect/disconnect
├── agent/
│   └── medical_agent.py    # AI medical explanation using LangChain
├── .env                    # Pinata API keys
├── requirements.txt        # Python dependencies
└── README.md               # You're reading this
```

> Each user has their own folder inside `data/`, named after their wallet address (e.g., `0xabc123..._appointments/`). All appointment files for that user are stored there and synced to IPFS.

---

## 🚀 Features

- 🔐 **MetaMask Wallet Login**: Authenticate users via their crypto wallet.
- 📅 **AI-Assisted Appointment Booking**: Capture patient symptoms and get an AI-generated explanation.
- 💾 **Decentralized Storage**: Save each appointment file on IPFS via Pinata.
- 📂 **Per-User Data Storage**: Appointments are stored in `data/{wallet_address}_appointments/`
- 📬 **User-Based Viewing**: View only your booked appointments securely.
- ✅ **No Paid APIs**: Uses free and privacy-respecting infrastructure.

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/smit-groovy/medi-chain.git
cd medi-chain
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env` File

```ini
LANGCHAIN_API_KEY=your_langchain_api_key
TOGETHER_API_KEY=your_together_api_key
PINATA_API_KEY=your_pinata_api_key
PINATA_SECRET_KEY=your_pinata_secret_key
```

Get your Pinata API keys from: [https://app.pinata.cloud/keys](https://app.pinata.cloud/keys)

---

## ▶️ Run the App

```bash
streamlit run app.py
```

---

## 🗃 Folder Structure

Each user has their own folder:

```
data/
├── 0x1234...abcd_appointments/
│   ├── appointment_2025-07-09T15-45-30.json
│   ├── appointment_2025-07-10T09-10-00.json
```

Each file is uploaded to IPFS via Pinata and a CID is returned.

---

## 🔐 How Data Security Works

- Each user logs in via MetaMask — no usernames or passwords needed.
- Appointment data is stored in JSON format, locally and on IPFS.
- CID (Content Identifier) ensures content integrity.
- Optionally, users can sign the CID in future to verify authenticity.

---

## 📦 Tech Stack

- **Frontend**: Streamlit
- **AI Agent**: LangChain (custom chain using LangGraph)
- **Wallet**: MetaMask + `streamlit-js-eval`
- **Storage**: Pinata IPFS
- **Backend**: Python

---

## 📚 Learnings & Notes

- All IPFS files are public by design. Do not store sensitive info without encryption.
- IPFS CIDs are immutable. Every change results in a new CID.
- We currently do **not** track versions — this can be added later for production.

---

## 💡 Future Ideas

- CID signing using MetaMask private key
- Versioning of appointment logs
- Integration with Web3 health records
- Email/SMS reminders for upcoming appointments

---

## 👨‍💻 Maintainer

**Smit Prajapati**  
_Made with ❤️ to learn Web3 + AI + IPFS integration_

---

## 🛡 Disclaimer

This is a **learning project** and **not for production use**. 
No sensitive patient data should be stored in unencrypted form.

---

## License

This project is licensed under the [MIT License](LICENSE).
