import boto3
from botocore.exceptions import ClientError
from typing import List, Optional

# Create an EC2 client
ec2 = boto3.client('ec2')

def list_key_pairs(client: boto3.client) -> List[str]:
    """
    List all key pairs in the AWS EC2 service.

    Args:
        client (boto3.client): The EC2 client to interact with AWS.

    Returns:
        List[str]: A list of formatted key pair details.
    """
    key_pair_details = []  # List to store key pair information
    next_token: Optional[str] = None  # Token for paginated results

    while True:
        try:
            # Fetch key pairs, using next_token if available
            response = client.describe_key_pairs(NextToken=next_token) if next_token else client.describe_key_pairs()

            # Process each key pair in the response
            for kp in response['KeyPairs']:
                try:
                    # Format key pair information
                    key_pair_info = (
                        f"KeyName: {kp['KeyName']}\n"
                        f"KeyPairId: {kp['KeyPairId']}\n"
                        f"KeyType: {kp['KeyType']}\n"
                        f"KeyFingerprint: {kp['KeyFingerprint']}\n"
                        f"CreateTime: {kp['CreateTime']}"
                    )
                    key_pair_details.append(key_pair_info)  # Append to the list
                except KeyError as e:
                    print(f"Missing key in KeyPair data: {e}")  # Handle missing keys

            # Check for the next token to continue pagination
            next_token = response.get('NextToken')
            if not next_token:
                break  # Exit loop if there are no more pages

        except ClientError as e:
            print(f"Client error while retrieving KeyPair data: {e}")  # Handle AWS client errors
            break
        except Exception as e:
            print(f"Unexpected error while retrieving KeyPair data: {e}")  # Handle any other unexpected errors
            break

    return key_pair_details  # Return the list of key pair details

if __name__ == "__main__":
    key_pairs = list_key_pairs(ec2)  # Call the function to list key pairs
    for key_pair in key_pairs:
        print(key_pair)  # Print each key pair detail
