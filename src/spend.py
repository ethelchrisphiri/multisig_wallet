"""
Step 4: Spend from the multisig via a real PSBT signing walkthrough.

- Coordinator (watch-only, no private keys) proposes the spend as an
  unsigned, funded PSBT.
- signer_a signs independently.
- signer_b signs on top of signer_a's result. Since this is 2-of-3,
  Bitcoin Core recognizes the threshold is met and marks the PSBT
  complete right away — signer_c's key is never touched.
- Finalize (converts the PSBT into a broadcastable raw transaction) and
  broadcast it.
"""

from src.rpc import node_rpc, wallet_rpc
from src.create_multisig import COORDINATOR_WALLET

SIGNER_A = "signer_a"
SIGNER_B = "signer_b"


def build_unsigned_psbt(to_address: str, amount_btc: float) -> str:
    coordinator = wallet_rpc(COORDINATOR_WALLET)
    result = coordinator.walletcreatefundedpsbt(
        [],                              
        [{to_address: amount_btc}],
        0,                               
        {"includeWatching": True},       
    )
    return result["psbt"]


def signer_process_psbt(wallet_name: str, psbt: str):
    signer = wallet_rpc(wallet_name)
    result = signer.walletprocesspsbt(psbt)
    print(f"[{wallet_name}] complete={result['complete']}")
    return result["psbt"], result["complete"]


def finalize_and_broadcast(node, psbt: str) -> str:
    finalized = node.finalizepsbt(psbt)
    if not finalized["complete"]:
        raise RuntimeError("PSBT is not complete — need more signatures")
    return node.sendrawtransaction(finalized["hex"])


def spend(to_address: str, amount_btc: float) -> str:
    node = node_rpc()

    print("Coordinator building unsigned, funded PSBT...")
    psbt = build_unsigned_psbt(to_address, amount_btc)

    print("Signer A signing independently...")
    psbt, complete = signer_process_psbt(SIGNER_A, psbt)

    print("Signer B signing independently (Signer C's key is never used)...")
    psbt, complete = signer_process_psbt(SIGNER_B, psbt)

    if not complete:
        raise RuntimeError("Expected the PSBT to be complete after 2 of 3 signatures")

    print("Finalizing and broadcasting...")
    txid = finalize_and_broadcast(node, psbt)
    print(f"Broadcast! txid: {txid}")
    return txid


if __name__ == "__main__":
    import sys
    spend(sys.argv[1], float(sys.argv[2]))