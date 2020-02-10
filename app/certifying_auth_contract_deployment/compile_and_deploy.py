import json
from web3 import Web3
from solc import compile_files, link_code, compile_source


# web3.py instance
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.eth.defaultAccount = w3.eth.accounts[0]

def deploy_contract(contract_interface):
    # Instantiate and deploy contract
    contract = w3.eth.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['bin']
    )

    print(contract)
    # Get transaction hash from deployed contract
    tx_hash = contract.constructor().transact()
    # Get tx receipt to get contract address
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    return tx_receipt['contractAddress']


# compile all contract files

PATH_TO_SOLIDITY_PROGRAM = 'E:\Blockchain\Python-Ethereum\cc-trading-demo\CarbonCreditContract.sol'


contracts = compile_files([PATH_TO_SOLIDITY_PROGRAM])
#print(contracts)
main_contract = contracts.pop(PATH_TO_SOLIDITY_PROGRAM + ':ReceiverPays')
#main_contract = contracts.pop('user.sol:userRecords')
# add abi(application binary interface) and transaction reciept in json file
with open('deployment_data.json', 'w') as outfile:
    data = {
        "abi": main_contract['abi'],
        "contract_address": deploy_contract(main_contract)
    }
    json.dump(data, outfile, indent=4, sort_keys=True)

print('Successfully compiled and deployed. More details in deployment_data.json\n')
