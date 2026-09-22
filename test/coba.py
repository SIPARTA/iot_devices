# from web3 import Web3

# address = "0x68a1B7445A65a96B86B50Eb14C23c2b1a88B474E"

# rpcs = [
#     "https://polygon-amoy.drpc.org",
#     "https://rpc-amoy.polygon.technology",
#     "https://polygon-amoy-bor-rpc.publicnode.com",
# ]

# for rpc in rpcs:
#     print("\n===================================")
#     print("RPC:", rpc)

#     try:
#         w3 = Web3(Web3.HTTPProvider(rpc))

#         print("Connected:", w3.is_connected())
#         print("Chain ID:", w3.eth.chain_id)

#         code = w3.eth.get_code(
#             Web3.to_checksum_address(address)
#         )

#         print("Code length:", len(code))
#         print("Code:", code.hex()[:100])

#     except Exception as e:
#         print("ERROR:", e)


from web3 import Web3

RPC = "https://polygon-amoy.drpc.org"

TX_HASH = "0xceac5c8c67120457951412fdc8a73a8649fef92bee342d2526db92aea4a81407"

CONTRACT = "0x68a1B7445A65a96B86B50Eb14C23c2b1a88B474E"

w3 = Web3(Web3.HTTPProvider(RPC))

print("Connected :", w3.is_connected())
print("Chain ID  :", w3.eth.chain_id)

# -------------------------------------------------
# 1. Ambil transaction
# -------------------------------------------------

tx = w3.eth.get_transaction(TX_HASH)

print("\nTRANSACTION")
print("Hash      :", tx.hash.hex())
print("From      :", tx["from"])
print("To        :", tx["to"])
print("Value     :", tx["value"])
print("Block     :", tx["blockNumber"])
print("Input len :", len(tx["input"]))

# -------------------------------------------------
# 2. Ambil receipt
# -------------------------------------------------

receipt = w3.eth.get_transaction_receipt(TX_HASH)

print("\nRECEIPT")
print("Status          :", receipt["status"])
print("ContractAddress :", receipt["contractAddress"])
print("Block           :", receipt["blockNumber"])
print("Gas used        :", receipt["gasUsed"])

# -------------------------------------------------
# 3. Check bytecode
# -------------------------------------------------

code = w3.eth.get_code(
    Web3.to_checksum_address(CONTRACT)
)

print("\nCONTRACT")
print("Address    :", Web3.to_checksum_address(CONTRACT))
print("Code len   :", len(code))
print("Code       :", code.hex()[:200])