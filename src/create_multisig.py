"""
Step 3: Build the 2 of 3 multi
sig descriptor from the three signers'
xpubs and import it into a watch only coordinator wallet that holds no
private keys of its own.
"""

from src.rpc import node_rpc, wallet_rpc
from src.setup_signers import setup_all_signers

COORDINATOR_WALLET = "multisig_coordinator"
THRESHOLD = 2
def extract_key_expression(descriptor: str) -> str:
    """Turn 'wpkh([fp/84h/1h/0h]tpub.../0/*)#checksum' into
    '[fp/84h/1h/0h]tpub.../0/*' keeping the range marker this time,
    just stripping the wpkh() wrapper and the checksum."""
    inner = descriptor.split("(", 1)[1]      
    inner = inner.rsplit(")", 1)[0]       
    return inner


def build_multisig_descriptor(signer_descriptors: dict) -> str:
    keys = [extract_key_expression(d) for d in signer_descriptors.values()]
    return f"wsh(sortedmulti({THRESHOLD},{','.join(keys)}))"

def import_multisig_descriptors(coordinator, descriptor: str):
    results = []
    for branch, is_internal in [("0", False), ("1", True)]:
        branch_descriptor = descriptor.replace("/0/*", f"/{branch}/*")
        info = coordinator.getdescriptorinfo(branch_descriptor)
        checksummed = branch_descriptor + "#" + info["checksum"]
        result = coordinator.importdescriptors([{
            "desc": checksummed,
            "active": True,
            "internal": is_internal,
            "range": [0, 1000],
            "timestamp": "now",
        }])
        if not result[0]["success"]:
            raise RuntimeError(f"Import failed for branch {branch}: {result}")
        print(f"Imported ({'internal' if is_internal else 'external'}): {checksummed}")
        results.append(checksummed)
    return results
def create_coordinator_wallet(node):
    if COORDINATOR_WALLET not in node.listwallets():
        node.createwallet(COORDINATOR_WALLET, True, True)
    return wallet_rpc(COORDINATOR_WALLET)
def create_multisig() -> str:
    node = node_rpc()
    signer_descriptors = setup_all_signers()
    descriptor = build_multisig_descriptor(signer_descriptors)
    print(f"Combined descriptor: {descriptor}")

    coordinator = create_coordinator_wallet(node)
    import_multisig_descriptors(coordinator, descriptor)  

    address = coordinator.getnewaddress("", "bech32")
    print(f"Multisig address: {address}")
    return address


if __name__ == "__main__":
    create_multisig()