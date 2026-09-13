"""
Unit tests for the pure descriptor string logic in create_multisig.py.
These need no running bitcoind they just test string transformations.
"""

import pytest
from src.create_multisig import extract_key_expression, build_multisig_descriptor


def test_extract_key_expression_strips_wrapper_and_checksum():
    descriptor = "wpkh([186a20d7/84h/1h/0h]tpubDCiYoT7RZC6MebU7HV7cS4XwquTePZuzaQmL9e3aY5jdX5VLmZ4PQ1FEQNpXtQCJvZi9dHPCz4B5zRynVVBRhFrpMos3QH5Vcm4oyTUouKh/0/*)#l2w56jkz"
    result = extract_key_expression(descriptor)

    assert result.startswith("[186a20d7/84h/1h/0h]tpub")
    assert result.endswith("/0/*")
    assert "wpkh(" not in result
    assert "#l2w56jkz" not in result


def test_build_multisig_descriptor_combines_three_keys():
    signer_descriptors = {
        "signer_a": "wpkh([186a20d7/84h/1h/0h]tpubAAA/0/*)#aaa1111",
        "signer_b": "wpkh([9550ad1a/84h/1h/0h]tpubBBB/0/*)#bbb2222",
        "signer_c": "wpkh([1a456d0c/84h/1h/0h]tpubCCC/0/*)#ccc3333",
    }
    result = build_multisig_descriptor(signer_descriptors)

    assert result.startswith("wsh(sortedmulti(2,")
    assert result.endswith("))")
   
    assert result.count("/0/*") == 3
    assert "[186a20d7/84h/1h/0h]tpubAAA/0/*" in result
    assert "[9550ad1a/84h/1h/0h]tpubBBB/0/*" in result
    assert "[1a456d0c/84h/1h/0h]tpubCCC/0/*" in result


def test_build_multisig_descriptor_uses_sortedmulti_not_multi():
    signer_descriptors = {
        "a": "wpkh([fp1/84h/1h/0h]tpub1/0/*)#c1",
        "b": "wpkh([fp2/84h/1h/0h]tpub2/0/*)#c2",
    }
    result = build_multisig_descriptor(signer_descriptors)
    assert "sortedmulti(" in result
    assert result.split("sortedmulti(")[0].endswith("wsh(")