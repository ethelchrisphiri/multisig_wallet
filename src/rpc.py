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