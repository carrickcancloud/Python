import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any

# Initialize the EC2 client
ec2 = boto3.client('ec2')

def delete_key_pair(client: boto3.client, dkp_key_name: str = None, dkp_key_id: str = None) -> Dict[str, Any]:
    """
    Deletes a specified key pair from EC2 using either the name or the ID.

    Args:
        client (boto3.client): The EC2 client.
        dkp_key_name (str): The name of the key pair to delete.
        dkp_key_id (str): The ID of the key pair to delete.

    Returns:
        Dict[str, Any]: A dictionary containing the success status and message.
    """
    dkp_response = {
        "success": False,
        "message": ""
    }

    try:
        # Attempt to delete the key pair using the name if provided
        if dkp_key_name:
            client.delete_key_pair(KeyName=dkp_key_name)
            dkp_response["success"] = True
            dkp_response["message"] = f"Key pair '{dkp_key_name}' deleted successfully."
            return dkp_response

        # If name is not provided, attempt to delete using the ID
        if dkp_key_id:
            client.delete_key_pair(KeyPairId=dkp_key_id)
            dkp_response["success"] = True
            dkp_response["message"] = f"Key pair with ID '{dkp_key_id}' deleted successfully."
            return dkp_response

    except ClientError as e:
        # Handle specific error for key pair not found
        if e.response['Error']['Code'] == 'InvalidKeyPair.NotFound':
            dkp_response["message"] = f"Key pair '{dkp_key_name or dkp_key_id}' not found."
        else:
            dkp_response["message"] = f"An error occurred: {e}"

    return dkp_response

def prompt_with_retries(pwr_prompt: str, pwr_max_retries: int = 3) -> str:
    """
    Prompt the user with a message and allow a maximum number of retries.

    :param pwr_prompt: Input prompt message
    :param pwr_max_retries: Maximum number of retries for input
    :return: Validated input from the user
    :raises Exception: If maximum retries are reached
    """
    pwr_retries = 0
    while pwr_retries < pwr_max_retries:
        pwr_response = input(pwr_prompt).strip()
        if pwr_response:
            return pwr_response
        else:
            pwr_retries += 1
            print(f"No input provided. You have {pwr_max_retries - pwr_retries} retry(s) left.")

    # Raise an exception if maximum retries reached
    raise Exception("Maximum retries reached. Exiting the program.")

def get_key_input_type() -> str:
    """
    Prompt the user to select whether to use a key name or key ID.

    :return: The type of key input ('name' or 'id')
    :raises Exception: If maximum retries are reached
    """
    while True:
        gki_choice = prompt_with_retries(
            "Do you want to use a Key Name or Key ID? (Enter 'name' or 'id'): ").strip().lower()
        if gki_choice in ['name', 'id']:
            return gki_choice
        else:
            print("Invalid choice. Please enter 'name' for Key Name or 'id' for Key ID.")

if __name__ == "__main__":
    try:
        # Prompt for key input type
        key_input_type = get_key_input_type()

        # Based on the choice, prompt for the appropriate key
        if key_input_type == 'name':
            key_name = prompt_with_retries("Enter the key pair name: ")
            key_id = ""  # No key ID needed if using key name
        else:  # key_input_type == 'id'
            key_name = ""
            key_id = prompt_with_retries("Enter the key pair ID: ")

        # Call the function and handle the result
        result = delete_key_pair(ec2, key_name if key_name else None, key_id if key_id else None)
        print("Deletion status:", result["success"])
        print("Message:", result["message"])

    except Exception as e:
        print(str(e))  # Print the error message
        exit(1)  # Exit with a non-zero status to indicate error
