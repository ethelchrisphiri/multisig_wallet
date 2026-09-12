"""
Thin helper for connecting to bitcoind's JSON-RPC interface, scoped to a
specific wallet. Bitcoin Core exposes each loaded wallet at its own RPC
path: http://<host>:<port>/wallet/<wallet_name>
"""

import os
from bitcoinrpc.authproxy import AuthServiceProxy

RPC_USER = os.environ.get("RPC_USER", "user")
RPC_PASSWORD = os.environ.get("RPC_PASSWORD", "password")
RPC_HOST = os.environ.get("RPC_HOST", "127.0.0.1")
RPC_PORT = os.environ.get("RPC_PORT", "18443")


def _base_url() -> str:
    return f"http://{RPC_USER}:{RPC_PASSWORD}@{RPC_HOST}:{RPC_PORT}"


def node_rpc() -> AuthServiceProxy:
    """RPC connection with no wallet context (for node-level calls)."""
    return AuthServiceProxy(_base_url())


def wallet_rpc(wallet_name: str) -> AuthServiceProxy:
    """RPC connection scoped to a specific loaded wallet."""
    return AuthServiceProxy(f"{_base_url()}/wallet/{wallet_name}")


def ensure_wallet(node, name: str, *create_args) -> AuthServiceProxy:
    """
    Make sure a wallet is loaded and ready to use, regardless of whether
    it's brand new or already exists on disk from a previous run.

    Handles three cases:
    - Wallet already loaded -> just use it.
    - Wallet exists on disk but isn't loaded (e.g. after restarting
      bitcoind) -> load it.
    - Wallet genuinely doesn't exist yet -> create it.

    create_args are passed positionally to createwallet, e.g.
    ensure_wallet(node, "multisig_coordinator", True, True) for the
    (disable_private_keys, blank) flags.
    """
    if name in node.listwallets():
        return wallet_rpc(name)

    try:
        node.loadwallet(name)
    except Exception as e:
        # Error code -18 means "wallet not found" genuinely new, create it.
        # Any other error (corrupt file, already loading, etc.) should
        # surface rather than being silently swallowed.
        if "-18" in str(e) or "not found" in str(e).lower():
            node.createwallet(name, *create_args)
        else:
            raise

    return wallet_rpc(name)