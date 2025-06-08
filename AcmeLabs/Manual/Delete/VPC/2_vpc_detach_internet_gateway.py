import boto3
from botocore.exceptions import ClientError
from typing import Union, Tuple, Optional

# Initialize the EC2 client
ec2 = boto3.client('ec2')

# Constants for internet gateway detachment
TAG_VPC_NAME = 'AcmeLabs-Dev'  # Name tag for the VPC
TAG_IGW_NAME = 'AcmeLabs-Dev-IGW'  # Name tag for the Internet Gateway
TAG_IGW_ENV = 'Dev'  # Environment tag for the Internet Gateway

def get_vpc_id(client: boto3.client) -> Tuple[Optional[str], Optional[str]]:
    """
    Check if a VPC exists with the specified name tag 'AcmeLabs-Dev'.
    If it exists, return the VPC ID.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.

    Returns:
        Tuple[Optional[str], Optional[str]]: The VPC ID if the VPC exists, or an error message.
    """
    try:
        # Describe VPCs based on the provided filters
        gvi_response = client.describe_vpcs(
            Filters=[
                {'Name': 'tag:Name', 'Values': [TAG_VPC_NAME]},  # Filter by Name tag
                {'Name': 'tag:Environment', 'Values': [TAG_IGW_ENV]}  # Filter by Environment tag
            ]
        )

        # Check if any VPCs match the filters and return the VPC ID
        if gvi_response['Vpcs']:
            return gvi_response['Vpcs'][0]['VpcId'], None  # Return the VPC ID of the first matching VPC
        else:
            return None, "No matching VPC found."  # No matching VPC found
    except ClientError as e:
        return None, f"Error checking VPC existence: {e}"  # Return error message

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
                {'Name': 'tag:Name', 'Values': [gigi_tag_name]}  # Filter by Name tag
            ]
        )

        # Check if any Internet Gateways match the filters and return the first one found
        if gigi_igw_response['InternetGateways']:
            return gigi_igw_response['InternetGateways'][0]['InternetGatewayId'], None
        else:
            return None, "No Internet Gateway found with the specified tag."
    except ClientError as e:
        return None, f"Error checking Internet Gateway existence: {e}"

def detach_internet_gateway(client: boto3.client, dig_igw_id: str, dig_vpc_id: str) -> str:
    """
    Detach an Internet Gateway from a specified VPC.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        dig_igw_id (str): The ID of the Internet Gateway to detach.
        dig_vpc_id (str): The ID of the VPC from which to detach the Internet Gateway.

    Returns:
        str: A message indicating the result of the detach operation.
    """
    try:
        # Detach the Internet Gateway from the specified VPC
        dig_response = client.detach_internet_gateway(
            InternetGatewayId=dig_igw_id,
            VpcId=dig_vpc_id,
        )

        # Check if the detach operation was successful
        if dig_response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return f"Internet Gateway {dig_igw_id} detached from VPC {dig_vpc_id} successfully."
        else:
            return f"Failed to detach Internet Gateway {dig_igw_id} from VPC {dig_vpc_id}. HTTP Status Code: {dig_response['ResponseMetadata']['HTTPStatusCode']}"
    except ClientError as e:
        return f"Client error detaching Internet Gateway: {e.response['Error']['Message']}"

if __name__ == "__main__":
    # Get the VPC ID
    vpc_id, error = get_vpc_id(ec2)
    if error:
        print(error)  # Print error message for local use
    else:
        # Get the Internet Gateway ID
        igw_id, error = get_internet_gateway_id(ec2, TAG_IGW_NAME)
        if error:
            print(error)  # Print error message for local use
        else:
            # Detach the Internet Gateway from the VPC
            result = detach_internet_gateway(ec2, igw_id, vpc_id)
            print(result)  # Print result for local use
