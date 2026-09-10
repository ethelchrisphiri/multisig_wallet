"""
CLI entry point for the 2-of-3 multisig wallet.

Usage:
    python cli.py setup-signers
    python cli.py create-multisig
    python cli.py fund [--amount 0.5]
    python cli.py spend --to <address> --amount 0.1
"""

import argparse

from src.setup_signers import setup_all_signers
from src.create_multisig import create_multisig
from src.fund import fund_multisig
from src.spend import spend


def main():
    parser = argparse.ArgumentParser(description="2-of-3 multisig wallet demo")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("setup-signers", help="Create 3 independent signer wallets")
    sub.add_parser("create-multisig", help="Build the 2-of-3 descriptor + coordinator wallet")

    fund_p = sub.add_parser("fund", help="Mine + send test coins to the multisig address (regtest)")
    fund_p.add_argument("address", help="Multisig address to fund")
    fund_p.add_argument("--amount", type=float, default=0.5)

    spend_p = sub.add_parser("spend", help="Build, sign, and broadcast a spend")
    spend_p.add_argument("--to", required=True, help="Destination address")
    spend_p.add_argument("--amount", type=float, required=True)

    args = parser.parse_args()

    if args.command == "setup-signers":
        setup_all_signers()
    elif args.command == "create-multisig":
        create_multisig()
    elif args.command == "fund":
        fund_multisig(args.address, args.amount)
    elif args.command == "spend":
        spend(args.to, args.amount)


if __name__ == "__main__":
    main()