abi="""
[
	{
		"constant": false,
		"inputs": [
			{
				"name": "_certi_hash",
				"type": "string"
			},
			{
				"name": "_owner_address",
				"type": "address"
			},
			{
				"name": "_amount",
				"type": "uint256"
			},
			{
				"name": "_ttl",
				"type": "uint256"
			}
		],
		"name": "addCredits",
		"outputs": [
			{
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
				"name": "_owner_address",
				"type": "address"
			},
			{
				"name": "_receiver_address",
				"type": "address"
			},
			{
				"name": "_uuid",
				"type": "uint256"
			},
			{
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
		"inputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "_address",
				"type": "address"
			}
		],
		"name": "viewCurrentBalance",
		"outputs": [
			{
				"components": [
					{
						"name": "uuid",
						"type": "uint256"
					},
					{
						"name": "owner_addr",
						"type": "address"
					},
					{
						"name": "certifying_auth_addr",
						"type": "address"
					},
					{
						"name": "amount",
						"type": "uint256"
					},
					{
						"name": "ttl",
						"type": "uint256"
					},
					{
						"name": "certi_hash",
						"type": "string"
					},
					{
						"name": "retired",
						"type": "bool"
					}
				],
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