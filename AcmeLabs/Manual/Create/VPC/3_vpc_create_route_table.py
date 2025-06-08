import boto3
from botocore.exceptions import ClientError
from typing import Tuple, Optional

# Initialize the EC2 client
ec2 = boto3.client('ec2')

# Constants for route table
TAG_VPC_NAME = 'AcmeLabs-Dev'  # Name tag for the VPC
TAG_RTB = 'AcmeLabs-Dev-RouteTable'  # Name tag for the route table
TAG_RTB_ENV = 'Dev'  # Environment tag for the route table

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
                {'Name': 'tag:Name', 'Values': [TAG_VPC_NAME]}  # Filter by Name tag
            ]
        )

        # Check if any VPCs match the filters and return the VPC ID
        if gvi_response['Vpcs']:
            return gvi_response['Vpcs'][0]['VpcId'], None  # Return the VPC ID of the first matching VPC
        else:
            return None, "No matching VPC found."  # No matching VPC found
    except ClientError as e:
        return None, f"Error checking VPC existence: {e}"  # Return error message

def route_table_exists(client: boto3.client, rte_tag_name: str, rte_tag_env: str, rte_vpc_id: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a route table exists in the specified VPC with the given tags.

    Args:
        client (boto3.client): The Boto3 EC2 client.
        rte_tag_name (str): The name tag of the route table.
        rte_tag_env (str): The environment tag of the route table.
        rte_vpc_id (str): The ID of the VPC.

    Returns:
        Tuple[bool, Optional[str]]: True if the route table exists, False otherwise, with an optional error message.
    """
    try:
        # Describe route tables with specified filters
        rte_response = client.describe_route_tables(
            Filters=[
                {'Name': 'tag:Name', 'Values': [rte_tag_name]},  # Filter for the Name tag
                {'Name': 'tag:Environment', 'Values': [rte_tag_env]},  # Filter for the Environment tag
                {'Name': 'vpc-id', 'Values': [rte_vpc_id]}  # Filter for the VPC ID
            ]
        )
        # Return True if any route tables are found
        return len(rte_response['RouteTables']) > 0, None
    except ClientError as e:
        # Handle client error and return False with an error message
        return False, f"Error checking route table existence: {e}"

if __name__ == '__main__':
    # Check if the VPC ID can be retrieved
    vpc_id, error_msg = get_vpc_id(ec2)
    if error_msg:
        print(error_msg)  # Print error message if VPC ID retrieval fails
    else:
        # Check if the route table exists and print the result
        exists, error_msg = route_table_exists(ec2, TAG_RTB, TAG_RTB_ENV, vpc_id)
        if error_msg:
            print(error_msg)  # Print error message if route table existence check fails
        elif exists:
            print(
                f"RouteTable Exists:\n"
                f"    Name:{TAG_RTB}\n"
                f"    Environment:{TAG_RTB_ENV}\n"
                f"    VPC:{vpc_id}")
        else:
            # Create a new route table if it does not exist
            rtb = ec2.create_route_table(
                TagSpecifications=[
                    {
                        'ResourceType': 'route-table',  # Specify the resource type
                        'Tags': [
                            {'Key': 'Name', 'Value': TAG_RTB},  # Key for the Name tag
                            {'Key': 'Environment', 'Value': TAG_RTB_ENV}  # Key for the Environment tag
                        ]
                    }
                ],
                VpcId=vpc_id  # ID of the VPC to create the route table in
            )
            # Print details of the created route table
            print(
                f"RouteTable Created:\n"f""
                f"    RouteTable ID: {rtb['RouteTable']['RouteTableId']}\n"
                f"    Name: {rtb['RouteTable']['Tags'][0]['Value']}\n"
                f"    Environment: {rtb['RouteTable']['Tags'][1]['Value']}"
            )
