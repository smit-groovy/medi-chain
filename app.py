import streamlit as st
import datetime
from graph.appointment_flow import run_appointment_chain, get_flow_mermaid_png_bytes
from utils.wallet import connect_wallet, disconnect_wallet, sign_message_with_wallet, verify_signature
from utils.appointments import load_appointments_by_wallet

st.set_page_config(page_title="MediChain", page_icon="🩺", layout="wide")

# ---- Wallet Connection Logic ----
if "wallet_address" not in st.session_state:
    st.session_state.wallet_address = None

wallet_address = st.session_state.wallet_address

# ---- Not Connected UI ----
if wallet_address is None:
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://seeklogo.com/images/M/metamask-logo-09EDE53DBD-seeklogo.com.png", width=100)
        st.markdown("## 👋 Welcome to MediChain")
        st.markdown("Connect your MetaMask wallet to access your medical assistant and appointments.")
        connect_wallet()
    st.stop()

# ---- Connected UI ----
st.markdown("# 🩺 MediChain - AI assist & Booking")
st.success("✅ Wallet connected!")
st.markdown("#### 🦊 Connected Wallet Address")
st.code(wallet_address, language="text")

col1, col2 = st.columns([1, 5])
with col1:
    if st.button("🔌 Disconnect"):
        disconnect_wallet()
        st.stop()

# ---- Session State Defaults ----
st.session_state.setdefault("appointment_submitted", False)
st.session_state.setdefault("last_result", {})
st.session_state.setdefault("sign_cid_clicked", False)
st.session_state.setdefault("signature_result", None)

# ---- Tabs ----
tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Book Appointment", 
    "📋 View Appointments", 
    "✅ Verify Signature", 
    "🧩 Flow Graph"
])

# ---- Tab 1: Booking ----
# ---- Tab 1: Booking ----
with tab1:
    st.markdown("### 📅 Book an Appointment")

    with st.container():
        st.markdown("#### 🧑‍⚕️ Fill in Your Details")

        # Name and Doctor side-by-side
        col1, col2 = st.columns(2)
        with col1:
            user = st.text_input("Your Name", placeholder="Enter your name")
        with col2:
            doctor = st.selectbox("Select Doctor", ["Dr. Mehta", "Dr. Patel", "Dr. Sharma"])

        symptoms = st.text_area("Symptoms", placeholder="Describe your symptoms")

        col3, col4 = st.columns(2)
        with col3:
            appointment_date = st.date_input("Appointment Date", min_value=datetime.date.today())
        with col4:
            appointment_time = st.time_input("Appointment Time", value=datetime.time(10, 0))

        submit = st.button("🤖 Get AI Assist & Book Appointment")

    if submit:
        appointment_datetime = datetime.datetime.combine(appointment_date, appointment_time)

        if not user.strip():
            st.warning("⚠️ Please enter your name.")
        elif not symptoms.strip():
            st.warning("⚠️ Please describe your symptoms.")
        elif not doctor:
            st.warning("⚠️ Please select a doctor.")
        else:
            with st.spinner("Processing appointment with AI..."):
                state = {
                    "user": user,
                    "doctor": doctor,
                    "symptoms": symptoms,
                    "datetime": appointment_datetime.isoformat(),
                    "wallet": wallet_address,
                }
                result = run_appointment_chain(state)

                if result.get("valid") is False:
                    st.warning("⚠️ The entered symptoms don’t seem medically valid. Please try again.")
                else:
                    result["cid"] = result.get("cid", "")
                    st.session_state.last_result = result
                    st.session_state.appointment_submitted = True
                    st.session_state.sign_cid_clicked = False
                    st.session_state.signature_result = None
                    st.rerun()

    # ---- Show Result ----
    if st.session_state.appointment_submitted:
        result = st.session_state.last_result
        explanation = result.get("explanation", "")
        cid = result.get("cid", "")

        st.success("✅ Appointment booked!")

        if explanation:
            st.markdown("#### 🧠 AI Medical Explanation")
            st.info(explanation)

        if cid and "Upload failed" not in cid:
            st.success("✅ Appointment uploaded to IPFS!")
            st.markdown("#### 🆔 IPFS CID")
            st.code(cid, language="text")

            if not st.session_state.get("sign_cid_clicked", False):
                if st.button("🔏 Sign CID with Wallet"):
                    st.session_state.sign_cid_clicked = True
                    st.rerun()

            elif st.session_state.get("signature_result") is None:
                with st.spinner("Requesting signature from MetaMask..."):
                    signature = sign_message_with_wallet(cid)

                if signature:
                    st.session_state.signature_result = signature
                    st.success("✅ CID signed successfully!")
                    st.markdown("#### 🔐 Signature")
                    st.code(signature, language="text")
                else:
                    st.warning("❌ Signature failed or was denied.")
            else:
                st.markdown("#### 🔐 Signature")
                st.code(st.session_state.signature_result, language="text")
        else:
            st.warning("⚠️ Upload to IPFS failed.")
            
# ---- Tab 2: View Appointments ----
with tab2:
    st.markdown("### 📋 Your Appointments")

    appointments = load_appointments_by_wallet(wallet_address)

    if not appointments:
        st.info("No appointments found for your wallet.")
    else:
        with st.container():
            st.markdown("#### 📊 Summary Table")

            summary_data = []
            for idx, appt in enumerate(appointments, 1):
                summary_data.append({
                    "No.": idx,
                    "Doctor": appt.get("doctor", "-"),
                    "Date & Time": appt.get("datetime", "-"),
                    "Symptoms": appt.get("symptoms", "-"),
                })

            st.dataframe(summary_data, use_container_width=True)

        st.markdown("#### 📂 Detailed View")

        for idx, appt in enumerate(appointments, 1):
            with st.expander(f"🩺 Appointment #{idx} with {appt.get('doctor')}"):
                st.markdown(f"**📅 Date & Time:** {appt.get('datetime', '-')}")
                st.markdown(f"**🤒 Symptoms:** {appt.get('symptoms', '-')}")
                st.markdown("**🧠 AI Medical Explanation:**")
                st.info(appt.get("explanation", "-"))

# ---- Tab 3: Verify Signature ----
with tab3:
    st.markdown("### 🔎 Verify CID Signature")
    st.info("Enter CID, signature, and wallet address to verify its authenticity.")

    with st.container():
        with st.form("verify_signature_form"):
            cid_to_verify = st.text_input("🆔 IPFS CID", placeholder="Enter the CID that was signed")
            signature_to_verify = st.text_area("🔐 Signature", placeholder="Paste the signature string", height=100)
            wallet_to_verify = st.text_input("🦊 Wallet Address", placeholder="Enter the wallet address that signed it")

            submitted = st.form_submit_button("✅ Verify Signature")

        if submitted:
            if not cid_to_verify.strip() or not signature_to_verify.strip() or not wallet_to_verify.strip():
                st.warning("⚠️ All fields are required.")
            else:
                with st.spinner("Verifying..."):
                    is_valid = verify_signature(
                        cid_to_verify.strip(),
                        signature_to_verify.strip(),
                        wallet_to_verify.strip()
                    )
                    if is_valid:
                        st.success("✅ Signature is valid and matches the wallet.")
                    else:
                        st.error("❌ Signature is invalid or does not match the wallet.")

with tab4:
    st.header("📊 Appointment Booking Flow")
    png_bytes = get_flow_mermaid_png_bytes()

    if png_bytes:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(png_bytes, caption="🧠 LangGraph Flow")
    else:
        st.warning("Unable to render Mermaid flow diagram.")