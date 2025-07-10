import streamlit as st
import datetime
from graph.appointment_flow import run_appointment_chain
from utils.wallet import connect_wallet, disconnect_wallet
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
        st.header("Welcome to MediChain")
        st.markdown("Connect your MetaMask wallet to access your medical assistant and appointments.")
        connect_wallet()

    st.stop()

# ---- Connected UI ----
st.title("🩺 MediChain - AI Assist & Booking")
st.success(f"✅ Wallet connected: {wallet_address}")
if st.button("🔌 Disconnect Wallet"):
    disconnect_wallet()
    st.stop()
    

# ---- State Tracking ----
if "appointment_submitted" not in st.session_state:
    st.session_state.appointment_submitted = False
    st.session_state.last_result = {}

# ---- Tabs ----
tab1, tab2 = st.tabs(["📅 Book Appointment", "📋 View Appointments"])

# ---- Tab 1: Booking ----
with tab1:
    st.header("📅 Book an Appointment")

    warning_msg = ""
    user = st.text_input("Your Name", placeholder="Enter your name")
    doctor = st.selectbox("Doctor's Name", ["Dr. Mehta", "Dr. Patel", "Dr. Sharma"])
    symptoms = st.text_area("Describe your symptoms", placeholder="Enter your symptoms")

    appointment_date = st.date_input("Choose appointment date", min_value=datetime.date.today())
    appointment_time = st.time_input("Choose appointment time", value=datetime.time(10, 0))
    appointment_datetime = datetime.datetime.combine(appointment_date, appointment_time)

    if st.button("📩 Book Appointment") and not st.session_state.appointment_submitted:
        if not user.strip():
            warning_msg = "Please enter your name."
        elif not symptoms.strip():
            warning_msg = "Please describe your symptoms."
        elif not doctor:
            warning_msg = "Please select a doctor."

        if warning_msg:
            st.toast(warning_msg, icon="⚠️")
        else:
            with st.spinner("Booking..."):
                # Construct state
                state = {
                    "user": user,
                    "doctor": doctor,
                    "symptoms": symptoms,
                    "datetime": appointment_datetime.isoformat(),
                    "wallet": wallet_address,
                }

                result = run_appointment_chain(state)
                cid = result.get("cid", "")
                result["cid"] = cid

                st.session_state.last_result = result
                st.session_state.appointment_submitted = True
                st.rerun()

# ---- Show Result After Rerun ----
if st.session_state.appointment_submitted:
    result = st.session_state.last_result
    explanation = result.get("explanation", "")
    cid = result.get("cid", "")

    st.success("✅ Appointment booked!")

    if explanation:
        st.subheader("🧠 AI Medical Explanation")
        st.info(explanation)

    if cid and "Upload failed" not in cid:
        st.success("✅ File uploaded to IPFS successfully!")
        st.subheader("🆔 IPFS CID")
        st.code(cid, language="text")
    else:
        st.warning("⚠️ Upload to IPFS failed.")

# ---- Tab 2: View ----
with tab2:
    # Clear result after switching tab
    if st.session_state.get("appointment_submitted", False):
        st.session_state.appointment_submitted = False
        st.session_state.last_result = {}

    st.header("📋 Your Appointments")

    appointments = load_appointments_by_wallet(wallet_address)

    if not appointments:
        st.info("No appointments found for your wallet.")
    else:
        st.subheader("🔍 Summary Table")
        summary_data = []
        for idx, appt in enumerate(appointments, 1):
            summary_data.append({
                "No.": idx,
                "Doctor": appt.get("doctor", "-"),
                "Date & Time": appt.get("datetime", "-"),
                "Symptoms": appt.get("symptoms", "-"),
            })

        st.dataframe(summary_data, use_container_width=True)

        st.subheader("📂 Detailed View")
        for idx, appt in enumerate(appointments, 1):
            with st.expander(f"🩺 Appointment #{idx} with {appt.get('doctor')}"):
                st.write(f"📅 **Date & Time:** {appt.get('datetime', '-')}")
                st.write(f"🤒 **Symptoms:** {appt.get('symptoms', '-')}")
                st.markdown("🧠 **AI Medical Explanation:**")
                st.write(appt.get("explanation", "-"))
