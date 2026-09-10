"""
Step 2 — Create 3 independent signer wallets and export their xpubs.

Each signer wallet holds its own private keys, simulating a separate
person/device. Only the xpub descriptor (never a private key) gets
shared with the other participants.
"""

from src.rpc import node_rpc, wallet_rpc

SIGNERS = ["signer_a", "signer_b", "signer_c"]
DERIVATION_PATH = "84h/1h/0h"


def create_signer_wallet(node, name: str):
    if name not in node.listwallets():
        node.createwallet(wallet_name=name)
    return wallet_rpc(name)


def get_signer_xpub(wallet, account_path: str = DERIVATION_PATH) -> str:
    """Pull the external (receive) descriptor for this wallet at the
    given path — this is the ranged xpub we'll share for the multisig."""
    descriptors = wallet.listdescriptors()["descriptors"]
    for d in descriptors:
        if account_path in d["desc"] and "/0/*" in d["desc"]:
            return d["desc"]
    raise RuntimeError(f"No descriptor found for path {account_path}")


def setup_all_signers() -> dict:
    node = node_rpc()
    descriptors = {}
    for name in SIGNERS:
        wallet = create_signer_wallet(node, name)
        descriptors[name] = get_signer_xpub(wallet)
        print(f"[{name}] {descriptors[name]}")
    return descriptors


if __name__ == "__main__":
    setup_all_signers()