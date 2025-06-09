import boto3
from botocore.exceptions import ClientError
import os
from typing import Optional, Dict, Any

# Initialize the EC2 client
ec2 = boto3.client('ec2')

def create_key_pair(client: boto3.client, ckp_key_name: str) -> Optional[Dict[str, Any]]:
    """
    Create a key pair in AWS EC2.

    Parameters:
    - client: The EC2 client.
    - ckp_key_name: The name of the key pair to create.

    Returns:
    - The response from the create_key_pair API call if successful, None otherwise.
    """
    try:
        ckp_response = client.create_key_pair(
            KeyName=ckp_key_name,
            KeyType='rsa',
            TagSpecifications=[
                {
                    'ResourceType': 'key-pair',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': ckp_key_name
                        }
                    ]
                }
            ],
            KeyFormat='pem',
        )
        # Save the private key to a file
        private_key = ckp_response['KeyMaterial']
        save_private_key_to_file(ckp_key_name, private_key)
        return ckp_response
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidKeyPair.Duplicate':
            print(f"Key pair '{ckp_key_name}' already exists in AWS.")
            return None
        else:
            print(f"Failed to create key pair: {e}")
            return None

def key_pair_exists(client: boto3.client, kpe_key_name: str) -> bool:
    """
    Check if a key pair exists in AWS EC2.

    Parameters:
    - client: The EC2 client.
    - kpe_key_name: The name of the key pair to check.

    Returns:
    - True if the key pair exists, False otherwise.
    """
    try:
        kpe_response = client.describe_key_pairs(KeyNames=[kpe_key_name])
        return True if kpe_response['KeyPairs'] else False
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidKeyPair.NotFound':
            return False
        else:
            print(f"Error checking key pair existence: {e}")
            return False

def save_private_key_to_file(spktf_key_name: str, spktf_private_key: str) -> None:
    """
    Save the private key to a file with appropriate permissions.

    Parameters:
    - spktf_key_name: The name of the key pair.
    - spktf_private_key: The private key material.
    """
    # Get the current working directory
    current_directory = os.getcwd()
    file_name = os.path.join(current_directory, f"{spktf_key_name}.pem")

    with open(file_name, 'w') as file:
        file.write(spktf_private_key)
    os.chmod(file_name, 0o400)

    # Print the message including the current working directory
    print(f"Private key saved to '{file_name}'.")

def local_key_exists(lke_key_name: str) -> bool:
    """
    Check if a local copy of the key exists based on the name provided.

    Parameters:
    - lke_key_name: The name of the local key.

    Returns:
    - True if the local key file exists, False otherwise.
    """
    return os.path.isfile(f"{lke_key_name}.pem")

if __name__ == '__main__':
    # Prompt the user for the key name
    key_name = input("Enter the name for the key pair: ")

    # Check if the key pair already exists in AWS
    if key_pair_exists(ec2, key_name):
        print(f"Key pair '{key_name}' already exists in AWS, no action taken.")
    else:
        # Check if a local copy exists based on the user input
        if local_key_exists(key_name):
            print(f"Local key pair '{key_name}.pem' exists. Deleting it.")
            os.remove(f"{key_name}.pem")
            print(f"Local key pair '{key_name}.pem' has been deleted.")

        # Create a new key pair in AWS
        response = create_key_pair(ec2, key_name)
        if response:
            print(f"Key pair {key_name} created.")
