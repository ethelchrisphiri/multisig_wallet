"""
Integration test runs the FULL multisig flow against a real regtest
bitcoind. Unlike test_create_multisig.py, this actually creates wallets,
funds an address, and broadcasts a transaction.

It Requires bitcoind running in regtest mode.
"""

import pytest
from src.setup_signers import setup_all_signers
from src.create_multisig import create_multisig, COORDINATOR_WALLET
from src.fund import fund_multisig
from src.spend import spend
from src.rpc import wallet_rpc


@pytest.mark.integration
def test_full_multisig_flow():
    # Step 1: create the 3 signer wallets and confirm we got 3 back
    descriptors = setup_all_signers()
    assert len(descriptors) == 3

    # Step 2: build the multisig and confirm we got a real regtest address
    address = create_multisig()
    assert address.startswith("bcrt1")

    # Step 3: fund it and confirm the coordinator sees the money
    fund_multisig(address, amount_btc=1.0)
    coordinator = wallet_rpc(COORDINATOR_WALLET)
    assert coordinator.getbalance() >= 1.0

    # Step 4: spend using only 2 of the 3 signers, confirm it broadcasts
    destination = coordinator.getnewaddress()
    txid = spend(destination, 0.1)
    assert len(txid) == 64  