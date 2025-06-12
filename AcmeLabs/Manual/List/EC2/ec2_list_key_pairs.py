import boto3
from botocore.exceptions import ClientError
from typing import List, Optional
import fnmatch

# Create an EC2 client
ec2 = boto3.client('ec2')

def list_key_pairs(client: boto3.client, lkp_search_term: str) -> List[str]:
    """
    List all key pairs in the AWS EC2 service that match the search term.

    Args:
        client (boto3.client): The EC2 client to interact with AWS.
        lkp_search_term (str): The search term to filter key pairs.

    Returns:
        List[str]: A list of formatted key pair details that match the search term.
    """
    lkp_key_pair_details = []  # List to store key pair information
    lkp_next_token: Optional[str] = None  # Token for paginated results

    while True:
        try:
            # Fetch key pairs, using next_token if available
            lkp_response = client.describe_key_pairs(NextToken=lkp_next_token) if lkp_next_token else client.describe_key_pairs()

            # Process each key pair in the response
            for lkp_kp in lkp_response.get('KeyPairs'):
                try:
                    # Check if the key pair name matches the search term (case-insensitive and allows wildcards)
                    lkp_key_name = lkp_kp.get('KeyName', 'N/A')
                    if fnmatch.fnmatchcase(lkp_key_name.lower(), lkp_search_term.lower()):
                        # Format key pair information
                        lkp_key_pair_info = (
                            f"KeyName: {lkp_key_name}\n"
                            f"KeyPairId: {lkp_kp.get('KeyPairId', 'N/A')}\n"
                            f"KeyType: {lkp_kp.get('KeyType', 'N/A')}\n"
                            f"KeyFingerprint: {lkp_kp.get('KeyFingerprint', 'N/A')}\n"
                            f"CreateTime: {lkp_kp.get('CreateTime', 'N/A')}\n"
                        )
                        lkp_key_pair_details.append(lkp_key_pair_info)  # Append to the list
                except KeyError as e:
                    print(f"Missing key in KeyPair data: {e}")  # Handle missing keys

            # Check for the next token to continue pagination
            lkp_next_token = lkp_response.get('NextToken')
            if not lkp_next_token:
                break  # Exit loop if there are no more pages

        except ClientError as e:
            print(f"Client error while retrieving KeyPair data: {e}")  # Handle AWS client errors
            break
        except Exception as e:
            print(f"Unexpected error while retrieving KeyPair data: {e}")  # Handle any other unexpected errors
            break

    return lkp_key_pair_details  # Return the list of key pair details

def prompt_with_retries(pwr_prompt: str, pwr_max_retries: int = 3) -> str:
    """
    Prompt the user with a message and allow a maximum number of retries.

    Args:
        pwr_prompt: The message to display to the user.
        pwr_max_retries: The maximum number of attempts.

    Returns:
        The user input or 'no' if maximum retries reached.
    """
    pwr_retries = 0
    while pwr_retries < pwr_max_retries:
        pwr_response = input(pwr_prompt)  # Get user input
        if pwr_response:
            return pwr_response  # Return valid input
        else:
            pwr_retries += 1
            print(f"No input provided. You have {pwr_max_retries - pwr_retries} retry(s) left.")
    return "no"  # Return 'no' if maximum retries reached

if __name__ == "__main__":
    search_term = prompt_with_retries("Enter a key pair name (use '*' as wildcard): ")  # Prompt for key pair name
    if search_term.lower() != "no":
        key_pairs = list_key_pairs(ec2, search_term)  # Call the function to list key pairs
        for key_pair in key_pairs:
            print(key_pair)  # Print each key pair detail
    else:
        print("No valid input provided.")
