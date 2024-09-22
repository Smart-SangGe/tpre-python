from web3 import Web3
import json

rpc_url = "https://ethereum-holesky-rpc.publicnode.com"
chain = Web3(Web3.HTTPProvider(rpc_url))
contract_address = "0x642C23F91bf8339044A00251BC09d1D98110C433"
contract_abi = json.loads('''[
		{
			"anonymous": false,
			"inputs": [
				{
					"indexed": false,
					"internalType": "string",
					"name": "msg",
					"type": "string"
				}
			],
			"name": "messageLog",
			"type": "event"
		},
		{
			"inputs": [
				{
					"internalType": "string",
					"name": "text",
					"type": "string"
				}
			],
			"name": "logmessage",
			"outputs": [
				{
					"internalType": "bool",
					"name": "",
					"type": "bool"
				}
			],
			"stateMutability": "nonpayable",
			"type": "function"
		}
	]''')
contract = chain.eth.contract(address=contract_address, abi=contract_abi)
wallet_address = "0xe02666Cb63b3645E7B03C9082a24c4c1D7C9EFf6"
pk = "ae66ae3711a69079efd3d3e9b55f599ce7514eb29dfe4f9551404d3f361438c6"


def call_eth_logger(wallet_address, pk, message: str):
    transaction = contract.functions.logmessage(message).build_transaction({
        'chainId': 17000,
        'gas': 30000,
        'gasPrice': chain.to_wei('10', 'gwei'),
        'nonce': chain.eth.get_transaction_count(wallet_address, 'pending'),
    })
    signed_tx = chain.eth.account.sign_transaction(transaction, private_key=pk)
    tx_hash = chain.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(tx_hash)
    receipt = chain.eth.wait_for_transaction_receipt(tx_hash)
    transfer_event = contract.events.messageLog().process_receipt(receipt)
    for event in transfer_event:
        print(event['args']['msg'])
