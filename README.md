# An Ethereum based Carbon Trading Platform

This project aims to demonstrate the trade and consumption of carbon credits on blockchain by using smart contracts to track the origin and path of carbon credits starting from issuance by the Certificate Authority and ending at consumption/retirement.

## Installation instructions

Install python3

In the root folder run the following command (initialize your virtual environment if you want to before this step)

`python -m pip install -r dependencies.txt`

Deploy the smart contract on remix with 'Web3 Provider' option selected and then replace the contract's ABI in app/contract_abi.py

Also replace the corresponding addresses at the start of app/routes.py

The above project has been tested with Ganache. Carefully modify the code in app/routes.py if you want to switch to a different Ethereum test client(such as Infuria)

Remember to update your dependencies.txt file before pushing your update in case you install modules. Use the following command:

`python -m pip freeze > dependencies.txt`

Also run the following command after every pull in order to update your local dependencies

`python -m pip install -r dependencies.txt`

Create `app/contract_abi.py` and paste the abi of your compiled contract's ABI as follows

`abi = """ YOUR ABI HERE """`

Also replace the addresses in the header of routes.py according to your testing platform

## TO-DO List

- [ ] Registration page UI
- [ ] Home page UI (Add charts and stats)
- [ ] Prevent buying of self-owned carbon credits
- [ ] Add functions to update JSON files which mock the databases
- [ ] Upgrade database from JSON to a better alternative (pending discussion)
- [ ] Buy page
- [ ] Sell page
- [ ] Replace addresses with usernames
