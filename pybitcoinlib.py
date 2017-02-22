#!/usr/bin/env python3

# Copyright (C) 2014 The python-bitcoinlib developers
#
# This file is part of python-bitcoinlib.
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of python-bitcoinlib, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE file.

"""Low-level example of how to spend a standard pay-to-pubkey-hash (P2PKH) txout"""

import sys
# if sys.version_info.major < 3:
#     sys.stderr.write('Sorry, Python 3.x required by this example.\n')
#     sys.exit(1)

import hashlib
import gcoin as pygcoinlib

from bitcoin import SelectParams
from bitcoin.core import b2x, lx, COIN, COutPoint, CMutableTxOut, CMutableTxIn, CMutableTransaction, Hash160
from bitcoin.core.script import CScript, OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG, SignatureHash, SIGHASH_ALL
from bitcoin.core.scripteval import VerifyScript, SCRIPT_VERIFY_P2SH
from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret

SelectParams('mainnet')

def make_signed_tx(ins, outs, priv):
	print ('####### in make_signed_tx #######')
	print('ins: {}'.format(ins))
	print('outs: {}'.format(outs))
	print('priv: {}'.format(priv))
	txins = []
	txouts = []
	txin_scriptPubKeys = []
	# txin_scriptPubKeys = []
	for i, inp in enumerate(ins):
		print('inp[tx_id]: {}'.format(inp['tx_id']))
		txin = CMutableTxIn(COutPoint(lx(inp['tx_id']), inp['index']))
		seckey = CBitcoinSecret.from_secret_bytes(pygcoinlib.script_to_address(inp['script']).encode('utf-8'))
		txin_scriptPubKeys.append(CScript([OP_DUP, OP_HASH160, Hash160(seckey.pub), OP_EQUALVERIFY, OP_CHECKSIG]))
		# txin_scriptPubKeys.append(CScript([OP_DUP, OP_HASH160, Hash160(seckey.pub), OP_EQUALVERIFY, OP_CHECKSIG]))
		txins.append(txin)
	for o, out in enumerate(outs):
		# print('out[\'address\']: {}'.format(out['address']))
		if 'script' in out:
			# txouts.append(CMutableTxOut(0, CScript([bytes(out['script'], encoding='UTF-8')]), 2))
			print('song')
		else:
			txouts.append(CMutableTxOut(out['value'], CBitcoinAddress(out['address']).to_scriptPubKey(), out['color']))
		# print('address: {}'.format(pygcoinlib.script_to_address(spk['script'])))
	tx = CMutableTransaction(txins, txouts)
	for i, inp in enumerate(ins):
		sighash = SignatureHash(txin_scriptPubKeys[i], tx, i, SIGHASH_ALL)
		sig = seckey.sign(sighash) + bytes([SIGHASH_ALL])
		txins[i].scriptSig = CScript([sig, seckey.pub])
	# VerifyScript(txin.scriptSig, txin_scriptPubKey, tx, 0, (SCRIPT_VERIFY_P2SH,))
	return b2x(tx.serialize())

# Create the (in)famous correct brainwallet secret key.
h = hashlib.sha256(b'48C').digest()
seckey = CBitcoinSecret.from_secret_bytes(h)
print ('seckey: {}'.format(seckey))
print ('seckey.pub: {}'.format(seckey.pub))

# Same as the txid:vout the createrawtransaction RPC call requires
#
# lx() takes *little-endian* hex and converts it to bytes; in Bitcoin
# transaction hashes are shown little-endian rather than the usual big-endian.
# There's also a corresponding x() convenience function that takes big-endian
# hex and converts it to bytes.
txid = lx('7e195aa3de827814f172c362fcf838d92ba10e3f9fdd9c3ecaf79522b311b22d')
vout = 0

# Create the txin structure, which includes the outpoint. The scriptSig
# defaults to being empty.
txin = CMutableTxIn(COutPoint(txid, vout))
print ('txin: {}'.format(txin))
# We also need the scriptPubKey of the output we're spending because
# SignatureHash() replaces the transaction scriptSig's with it.
#
# Here we'll create that scriptPubKey from scratch using the pubkey that
# corresponds to the secret key we generated above.
txin_scriptPubKey = CScript([OP_DUP, OP_HASH160, Hash160(seckey.pub), OP_EQUALVERIFY, OP_CHECKSIG])
print ('txin_scriptPubKey: {}'.format(txin_scriptPubKey))
# Create the txout. This time we create the scriptPubKey from a Bitcoin
# address.
txout = CMutableTxOut(0.001*COIN, CBitcoinAddress('1C7zdTfnkzmr13HfA2vNm5SJYRK6nEKyq8').to_scriptPubKey(), 2)
print ('txout: {}'.format(txout))

# Create the unsigned transaction.
tx = CMutableTransaction([txin], [txout])
print ('tx: {}'.format(tx))

# Calculate the signature hash for that transaction.
sighash = SignatureHash(txin_scriptPubKey, tx, 0, SIGHASH_ALL)

# Now sign it. We have to append the type of signature we want to the end, in
# this case the usual SIGHASH_ALL.
sig = seckey.sign(sighash) + bytes([SIGHASH_ALL])

# Set the scriptSig of our transaction input appropriately.
txin.scriptSig = CScript([sig, seckey.pub])

# Verify the signature worked. This calls EvalScript() and actually executes
# the opcodes in the scripts to see if everything worked out. If it doesn't an
# exception will be raised.
VerifyScript(txin.scriptSig, txin_scriptPubKey, tx, 0, (SCRIPT_VERIFY_P2SH,))

# Done! Print the transaction to standard output with the bytes-to-hex
# function.
print(b2x(tx.serialize()))
