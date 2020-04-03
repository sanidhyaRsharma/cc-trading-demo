abi="""
[
	{
		"inputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "uuid",
				"type": "uint256"
			}
		],
		"name": "addEvent",
		"type": "event"
	},
	{
		"constant": false,
		"inputs": [
			{
				"internalType": "string",
				"name": "_certi_hash",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "_owner_address",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "_amount",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_ttl",
				"type": "uint256"
			}
		],
		"name": "addCredits",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"payable": true,
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"internalType": "address",
				"name": "_address",
				"type": "address"
			}
		],
		"name": "retireCredits",
		"outputs": [],
		"payable": true,
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"internalType": "address",
				"name": "_owner_address",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "_receiver_address",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "_uuid",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_amount",
				"type": "uint256"
			}
		],
		"name": "transferCredits",
		"outputs": [],
		"payable": true,
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [
			{
				"internalType": "address",
				"name": "_address",
				"type": "address"
			}
		],
		"name": "viewCurrentBalance",
		"outputs": [
			{
				"components": [
					{
						"internalType": "uint256",
						"name": "uuid",
						"type": "uint256"
					},
					{
						"internalType": "address",
						"name": "owner_addr",
						"type": "address"
					},
					{
						"internalType": "address",
						"name": "certifying_auth_addr",
						"type": "address"
					},
					{
						"internalType": "uint256",
						"name": "amount",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "ttl",
						"type": "uint256"
					},
					{
						"internalType": "string",
						"name": "certi_hash",
						"type": "string"
					},
					{
						"internalType": "bool",
						"name": "retired",
						"type": "bool"
					}
				],
				"internalType": "struct ReceiverPays.CarbonCredits[]",
				"name": "",
				"type": "tuple[]"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	}
]
"""