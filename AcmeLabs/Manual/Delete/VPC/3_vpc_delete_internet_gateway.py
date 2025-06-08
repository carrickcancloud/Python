import boto3
from botocore.exceptions import ClientError
from typing import Tuple, Optional

# Initialize the EC2 client
ec2 = boto3.client('ec2')

# Constants for internet gateway deletion
TAG_IGW_NAME = 'AcmeLabs-Dev-IGW'  # Name tag for the Internet Gateway
TAG_IGW_ENV = 'Dev'  # Environment tag for the Internet Gateway

def get_internet_gateway_id(client: boto3.client, gigi_tag_name: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Check if an Internet Gateway exists with the specified name tag.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        gigi_tag_name (str): The name of the tag to filter the Internet Gateway.

    Returns:
        Tuple[Optional[str], Optional[str]]: The Internet Gateway ID if it exists, or an error message.
    """
    try:
        # Describe Internet Gateways based on the provided filters
        gigi_igw_response = client.describe_internet_gateways(
            Filters=[
                {'Name': 'tag:Name', 'Values': [gigi_tag_name]},  # Filter by Name tag
                {'Name': 'tag:Environment', 'Values': [TAG_IGW_ENV]}  # Filter by Environment tag
            ]
        )

        # Check if any Internet Gateways match the filters and return the first one found
        if gigi_igw_response['InternetGateways']:
            return gigi_igw_response['InternetGateways'][0]['InternetGatewayId'], None
        else:
            return None, "No Internet Gateway found with the specified tag."
    except ClientError as e:
        return None, f"Error checking Internet Gateway existence: {e}"

def delete_internet_gateway(client: boto3.client, dig_igw_id: str) -> str:
    """
    Delete the specified Internet Gateway.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        dig_igw_id (str): The ID of the Internet Gateway to delete.

    Returns:
        str: A message indicating the result of the delete operation.
    """
    try:
        client.delete_internet_gateway(
            InternetGatewayId=dig_igw_id
        )
        return f"Internet Gateway {dig_igw_id} deleted successfully."
    except ClientError as e:
        return f"Error deleting Internet Gateway: {e}"

if __name__ == "__main__":
    # Get the Internet Gateway ID
    igw_id, error = get_internet_gateway_id(ec2, TAG_IGW_NAME)

    # Print error or proceed to delete the Internet Gateway
    if error:
        print(error)
    else:
        # Delete the Internet Gateway
        result = delete_internet_gateway(ec2, igw_id)
        print(result)
