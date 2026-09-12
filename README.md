# 2-of-3 Multisig Wallet Tool

A working demonstration of 2-of-3 multisig custody using Bitcoin Core's
descriptor wallets and PSBTs (BIP174) the same pattern used by
exchanges and custodians to secure cold storage funds.

Rather than reimplementing signing cryptography, this project
**orchestrates** Bitcoin Core's own wallet RPCs: independent key
generation, watch-only multisig coordination, and multi-party PSBT
signing the part that actually matters when building custody tooling.

## Status

Signer wallet creation and xpub extraction
2-of-3 multisig descriptor construction and coordinator wallet
Funding + full PSBT signing walkthrough (build → sign → sign → broadcast)
Unit tests (pure logic) and integration test (full flow, real bitcoind)
CI (GitHub Actions)
Frontend

## Architecture

```
signer_a  ─┐
signer_b  ─┼── xpubs only ──▶  multisig_coordinator (watch-only, 0 keys)
signer_c  ─┘                          │
                                       ▼
                          builds unsigned PSBT
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                      ▼
              signer_a signs                        (signer_c's key
              (walletprocesspsbt)                    never touched)
                    │
                    ▼
              signer_b signs
              (threshold met → auto-finalized)
                    │
                    ▼
              broadcast
```

**Why descriptor wallets, not legacy multisig.**
`wsh(sortedmulti(2,xpub1,xpub2,xpub3))` is the modern standard
(BIP380/381) Bitcoin Core itself recommends over the deprecated
`addmultisigaddress` flow. `sortedmulti` specifically (not plain
`multi`) sorts the keys into a canonical order, so the resulting address
is identical no matter which participant assembles the descriptor or
what order they list the keys in.

**Why native segwit (P2WSH).** Lower fees, no legacy script quirks.

**Why a watch-only coordinator.** The coordinator wallet
(`multisig_coordinator`) is created with `disable_private_keys=True` 
it can see incoming funds and build unsigned transactions, but
literally cannot hold or use a private key. This mirrors a real
finance/ops team monitoring and initiating payments without any one
person having unilateral signing power.

**Why PSBTs.** A PSBT (Partially Signed Bitcoin Transaction) is exactly
what hardware wallets and real multi-party custody setups pass between
devices or people it can be written to a file, put on a USB stick, or
emailed. Nothing in this design requires signers to be online
simultaneously, even though the demo signs everything in-process for
convenience.

## Threat model (why 2-of-3)

| Scenario | Outcome with 2-of-3 |
|---|---|
| One key lost (device destroyed) | Funds still recoverable with the remaining 2 keys |
| One key compromised (stolen/hacked) | Attacker alone cannot move funds — needs a 2nd key |
| One signer unavailable | Transaction can still be authorized by the other 2 |
| Two keys lost or compromised | Funds are unrecoverable / at risk — the accepted trade-off of 2-of-3 |

In production, the 3 keys should live in genuinely independent
locations and media e.g. one on a hardware wallet, one on an offline
laptop that's never touched the internet, one in a safety deposit box 
not on the same machine, which is the only thing this demo can offer
without real hardware.

## Known limitations

- **Regtest only.** Never point this at mainnet without a full security
  review key handling here is intentionally simplified (all 3 signer
  wallets live in one `bitcoind` instance on one machine) for
  demonstration purposes.
- **No hardware wallet integration.** A real deployment would sign via
  actual air gapped hardware, not another wallet on the same node.
- **No key backup/recovery flow.** Losing a signer wallet's data
  directory in this demo loses that key permanently a real system
  needs a seed phrase backup process.

## Prerequisites

- `bitcoind` (Bitcoin Core) installed, reachable via RPC
- Python 3.9+

## Setup

```bash
pip install -r requirements.txt

# Add bitcoind to PATH if not already (see troubleshooting below)
bitcoind -regtest -daemon
```

`~/.bitcoin/bitcoin.conf`:
```
regtest=1
server=1
rpcuser=user
rpcpassword=password
fallbackfee=0.0001
```

## Usage

```bash
python cli.py setup-signers
python cli.py create-multisig
python cli.py fund <multisig-address-from-previous-step>
python cli.py spend --to <destination-address> --amount 0.1
```

## Testing

```bash
# Unit tests:pure logic, no bitcoind needed, runs anywhere
python -m pytest tests/test_create_multisig.py -v

# Integration test: full flow, requires bitcoind running in regtest
python -m pytest tests/test_integration.py -v
```

## Bugs hit while building this (kept intentionally: see them as documentation)

- **`bitcoin-cli: command not found`**: the extracted binaries weren't
  on `PATH`. Fixed by exporting the bin folder's path directly rather
  than needing `sudo` to move them into `/usr/local/bin`.
- **`ModuleNotFoundError` after a successful-looking `pip install`** 
  `pip` and `python` were pointed at two different Python installs.
  Fixed by always using `python -m pip install ...` instead of bare
  `pip install ...`.
- **Multisig descriptor rejected as "not a valid descriptor function"**
  each key inside `sortedmulti(...)` needs its own `/0/*` range
  marker; a single range tacked onto the very end of the whole
  expression isn't valid syntax.
- **"Transaction needs a change address, but we can't generate it"** 
  only the external (receiving) descriptor branch was imported; the
  internal (change) branch is required too for the wallet to generate
  change addresses when spending.
- **"new range must include current range"** Bitcoin Core silently
  grows a descriptor's cached address range every time it's used, so
  re-importing with any fixed range eventually becomes too small.
  Fixed by checking whether a descriptor is already imported and
  skipping re-import entirely, rather than guessing a "big enough"
  number.
- **`createwallet` failing after a `bitcoind` restart**  wallets that
  already exist on disk aren't automatically reloaded into memory.
  Fixed with a shared `ensure_wallet()` helper: load if present, create
  only if genuinely new.

## Project structure

```
multisig-wallet/
├── README.md
├── requirements.txt
├── pytest.ini
├── cli.py
├── src/
│   ├── rpc.py               # RPC helpers, including ensure_wallet()
│   ├── setup_signers.py     # create 3 independent signer wallets
│   ├── create_multisig.py   # build descriptor, create coordinator wallet
│   ├── fund.py               # regtest funding helper
│   └── spend.py              # PSBT build → sign → sign → finalize → broadcast
└── tests/
    ├── test_create_multisig.py  # unit tests, no bitcoind required
    └── test_integration.py       # full flow, requires bitcoind
```