import streamlit as st
from src.setup_signers import setup_all_signers
from src.create_multisig import create_multisig
from src.spend import spend

st.title("2-of-3 Multisig Wallet")

if st.button("Create Signer Wallets"):
    with st.spinner("Creating 3 independent signer wallets..."):
        try:
            descriptors = setup_all_signers()
            st.success("Signer wallets ready")
            st.json(descriptors)
        except Exception as e:
            st.error(f"Failed to create signer wallets: {e}")

if st.button("Build Multisig"):
    with st.spinner("Building 2-of-3 descriptor and coordinator wallet..."):
        try:
            address = create_multisig()
            st.success(f"Multisig address: {address}")
        except Exception as e:
            st.error(f"Failed to build multisig: {e}")

st.divider()

to_address = st.text_input("Destination address")
amount = st.number_input("Amount (BTC)", value=0.1, min_value=0.0, step=0.01)

if st.button("Spend"):
    if not to_address.strip():
        st.warning("Enter a destination address before spending.")
    elif amount <= 0:
        st.warning("Amount must be greater than 0.")
    else:
        with st.spinner("Building PSBT, signing with 2 of 3 keys, and broadcasting..."):
            try:
                txid = spend(to_address.strip(), amount)
                st.success(f"Broadcast! txid: {txid}")
            except Exception as e:
                st.error(f"Spend failed: {e}")