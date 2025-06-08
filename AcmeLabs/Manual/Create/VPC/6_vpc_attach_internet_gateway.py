import boto3
from botocore.exceptions import ClientError
from typing import Tuple, Optional, Any

# Initialize the EC2 client
ec2 = boto3.client('ec2')

# Constants for internet gateway attachment
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
    If it exists, return the Internet Gateway ID.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        gigi_tag_name (str): The name of the tag to filter the Internet Gateway.

    Returns:
        Tuple[Optional[str], Optional[str]]: The Internet Gateway ID if it exists, or an error message.
    """
    try:
        # Describe Internet Gateways based on the provided filters
        gigi_response = client.describe_internet_gateways(
            Filters=[
                {'Name': 'tag:Name', 'Values': [gigi_tag_name]}  # Filter by Name tag
            ]
        )

        # Check if any Internet Gateways match the filters and return the first one found
        if gigi_response['InternetGateways']:
            return gigi_response['InternetGateways'][0]['InternetGatewayId'], None
        else:
            return None, "No Internet Gateway found with the specified tag."
    except ClientError as e:
        return None, f"Error checking Internet Gateway existence: {e}"  # Return error message

def attach_internet_gateway(client: boto3.client, aig_vpc_id: str, aig_igw_id: str) -> Tuple[bool, Optional[str]]:
    """
    Attach an Internet Gateway to the specified VPC.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        aig_vpc_id (str): The ID of the VPC to attach the Internet Gateway to.
        aig_igw_id (str): The ID of the Internet Gateway to attach.

    Returns:
        Tuple[bool, Optional[str]]: True if the attachment was successful, or an error message.
    """
    try:
        # Attach the Internet Gateway to the VPC
        aig_response = client.attach_internet_gateway(
            InternetGatewayId=aig_igw_id,
            VpcId=aig_vpc_id
        )
        return True, None  # Return success status
    except ClientError as e:
        return False, f"Error attaching Internet Gateway: {e}"  # Return error message

if __name__ == "__main__":
    # Get VPC ID
    vpc_id, error = get_vpc_id(ec2)
    if error:
        print(error)  # Print error message for VPC ID retrieval
    else:
        print(f"VPC ID: {vpc_id}")

        # Get Internet Gateway ID based on the tag name
        igw_id, error = get_internet_gateway_id(ec2, TAG_IGW_NAME)
        if error:
            print(error)  # Print error message for Internet Gateway ID retrieval
        else:
            print(f"Internet Gateway ID: {igw_id}")

            # Attach Internet Gateway to VPC
            success, error = attach_internet_gateway(ec2, vpc_id, igw_id)
            if error:
                print(error)  # Print error message for attaching Internet Gateway
            else:
                print("Internet Gateway successfully attached to VPC.")  # Success message
