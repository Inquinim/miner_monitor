Complete the following steps on the server you will be running this script from:
- Install bittensor.
- Regen your public coldkey wallet (or any wallet will do).
- Regen all your hotkeys that you want to monitor under the coldkey wallet.
- Fill out the variables.env file with the required information.
- Install requirements: pip install -r requirements.txt
- Run the command 'python3 miner_monitor.py' (without the quotes) on your desired server.

Note: It's recommended to create a new cold wallet (e.g., called "all") and regenerate all hotkeys from all your coldkeys under this new cold wallet to monitor all miners easily.