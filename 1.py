import requests
import random
from mnemonic import Mnemonic
from web3 import Web3
from bip44 import Wallet
import os

# Initialize Mnemonic library
mnemo = Mnemonic("english")

# Function to generate a random valid seed phrase
def generate_valid_seed_phrase(word_count=12):
    # Generate a random seed phrase with 12 words (or change word_count for more/less)
    seed_phrase = mnemo.generate(strength=word_count * 32)  # 12 words = 128 bits of entropy
    return seed_phrase

# Function to check if the seed phrase is valid using the BIP-39 wordlist
def is_valid_seed_phrase(seed_phrase):
    # Check if all words in the seed phrase are valid BIP-39 words
    word_list = mnemo.wordlist
    words = seed_phrase.split()
    return all(word in word_list for word in words)

# Function to generate Ethereum address from the seed phrase
def get_eth_address_from_seed(seed_phrase, index=0):
    # Initialize Wallet
    wallet = Wallet(seed_phrase)
    eth_account = wallet.derive_account("eth", index)
    # Return the Ethereum address and private key
    return eth_account["address"], eth_account["private_key"]

# Function to check Ethereum balance using Etherscan API
def check_eth_balance(address, api_key):
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={api_key}"
    response = requests.get(url).json()
    if response["status"] == "1":
        balance = int(response["result"]) / (10 ** 18)  # Convert Wei to Ether
        return balance
    else:
        return None

# Function to pick a random seed phrase from a .txt file uploaded from local storage
def get_random_seed_phrase_from_file(file_path):
    try:
        if not os.path.isfile(file_path):
            print(f"Error: The file at {file_path} does not exist.")
            return None

        with open(file_path, 'r') as file:
            seed_phrases = file.readlines()

        seed_phrases = [phrase.strip() for phrase in seed_phrases if phrase.strip()]
        
        if not seed_phrases:
            print("Error: The seed phrase file is empty.")
            return None
        
        return random.choice(seed_phrases)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# Main function to execute the workflow
def main():
    # Dictionary to hold addresses with balances > 0
    addresses_with_balance = {}

    # Choose whether to generate a random seed phrase or upload a file
    choice = input("Do you want to generate a random seed phrase or upload a .txt file? (generate/upload): ").lower()

    if choice == "generate":
        # Generate a random valid seed phrase
        seed_phrase = generate_valid_seed_phrase()
        print(f"Generated Seed Phrase: {seed_phrase}")
        
        # Validate the generated seed phrase
        if not is_valid_seed_phrase(seed_phrase):
            print("Error: The generated seed phrase is invalid!")
            return
        
        # Derive Ethereum address and check balance
        address, private_key = get_eth_address_from_seed(seed_phrase)
        print(f"Ethereum Address: {address}")
        
        # Get Etherscan API key
        api_key = input("Enter your Etherscan API key: ")
        balance = check_eth_balance(address, api_key)

        # If balance > 0, store the address and seed phrase
        if balance and balance > 0:
            addresses_with_balance[address] = {"seed_phrase": seed_phrase, "balance": balance}
        
    elif choice == "upload":
        # Get file path of the seed phrase .txt file from user
        file_path = input("Enter the full path to your seed phrases .txt file (e.g., /path/to/your/file.txt): ")
        
        # Automatically pick a seed phrase from the .txt file
        seed_phrase = get_random_seed_phrase_from_file(file_path)
        
        if seed_phrase is None:
            return  # Exit if there's an error with the file
    
        print(f"Using Seed Phrase: {seed_phrase}")
        
        # Derive Ethereum address and check balance
        address, private_key = get_eth_address_from_seed(seed_phrase)
        print(f"Ethereum Address: {address}")
        
        # Get Etherscan API key
        api_key = input("Enter your Etherscan API key: ")
        balance = check_eth_balance(address, api_key)

        # If balance > 0, store the address and seed phrase
        if balance and balance > 0:
            addresses_with_balance[address] = {"seed_phrase": seed_phrase, "balance": balance}
        
    else:
        print("Invalid option. Please choose 'generate' or 'upload'.")
        return

    # Output all addresses with a balance > 0
    if addresses_with_balance:
        print("\nAddresses with balance > 0:")
        for address, data in addresses_with_balance.items():
            print(f"Address: {address}")
            print(f"Seed Phrase: {data['seed_phrase']}")
            print(f"Balance: {data['balance']} ETH\n")
    else:
        print("No addresses with balance > 0 found.")

# Run the main function
if __name__ == "__main__":
    main()
