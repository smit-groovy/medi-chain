import streamlit as st
from streamlit_js_eval import streamlit_js_eval

def connect_wallet():
    if "wallet_requested" not in st.session_state:
        st.session_state.wallet_requested = False

    if not st.session_state.wallet_requested:
        if st.button("🦊 Connect Wallet"):
            st.session_state.wallet_requested = True
            st.rerun()
    else:
        js_code = """
        (async function() {
            if (window.ethereum) {
                try {
                    const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
                    return accounts[0];
                } catch (err) {
                    return null;
                }
            } else {
                alert("MetaMask is not installed.");
                return null;
            }
        })()
        """

        wallet_address = streamlit_js_eval(js_expressions=js_code, key="connect_wallet")

        if wallet_address:
            st.session_state.wallet_address = wallet_address
            st.session_state.wallet_connected = True
            st.session_state.wallet_requested = False
            st.rerun()
        else:
            st.info("👆 Please approve connection in MetaMask.")

def disconnect_wallet():
    st.session_state.wallet_address = None
    st.session_state.wallet_connected = False
    st.session_state.wallet_requested = False
    st.rerun()
