import streamlit as st
from streamlit_js_eval import streamlit_js_eval
from eth_account.messages import encode_defunct
from eth_account import Account

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
    
def sign_message_with_wallet(message):
    """
    Trigger MetaMask signature request to sign the given message (CID in our case).
    """
    js_code = f"""
    (async function() {{
        const accounts = await window.ethereum.request({{ method: 'eth_requestAccounts' }});
        const from = accounts[0];
        const msg = `{message}`;
        const sign = await window.ethereum.request({{
            method: 'personal_sign',
            params: [msg, from],
        }});
        return sign;
    }})()
    """
    return streamlit_js_eval(js_expressions=js_code, key="sign_message")


def verify_signature(cid: str, signature: str, claimed_wallet: str) -> bool:
    """
    Verifies that the given signature is valid for the CID and matches the wallet.
    """
    try:
        message = encode_defunct(text=cid)
        recovered_address = Account.recover_message(message, signature=signature)
        return recovered_address.lower() == claimed_wallet.lower()
    except Exception as e:
        print(f"❌ Signature verification failed: {e}")
        return False
