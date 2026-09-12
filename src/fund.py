"""
Step 3: Fund the multisig wallet (regtest only).

Creates a throwaway "faucet" wallet, mines blocks so it has spendable
coins (regtest requires 100 confirmations for coinbase maturity, hence
101 blocks to mature the first one), then sends test funds to the
multisig address.
"""

from src.rpc import node_rpc, wallet_rpc, ensure_wallet

FAUCET_WALLET = "faucet"


def ensure_faucet_wallet(node):
    return ensure_wallet(node, FAUCET_WALLET)


def fund_multisig(multisig_address: str, amount_btc: float = 0.5) -> str:
    node = node_rpc()
    faucet = ensure_faucet_wallet(node)

    faucet_address = faucet.getnewaddress()
    node.generatetoaddress(101, faucet_address)  # mature coinbase funds

    txid = faucet.sendtoaddress(multisig_address, amount_btc)
    node.generatetoaddress(1, faucet_address)  # confirm the funding tx

    print(f"Sent {amount_btc} BTC to {multisig_address}")
    print(f"Funding txid: {txid}")
    return txid


if __name__ == "__main__":
    import sys
    fund_multisig(sys.argv[1])