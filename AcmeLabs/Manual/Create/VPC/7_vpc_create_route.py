import boto3
import botocore.exceptions as ClientError
from typing import Tuple, Optional, Union

# Initialize the EC2 client
ec2 = boto3.client('ec2')

# Constants for route creation
TAG_IGW_NAME = 'AcmeLabs-Dev-IGW'  # Name tag for the Internet Gateway
TAG_RTB = 'AcmeLabs-Dev-RouteTable'  # Name tag for the Route Table
DEST_CIDR_BLOCK = '0.0.0.0/0'  # Destination CIDR block for the route

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
        gigi_response = client.describe_internet_gateways(
            Filters=[{'Name': 'tag:Name', 'Values': [gigi_tag_name]}]  # Filter by Name tag
        )

        # Check if any Internet Gateways match the filters and return the first one found
        if gigi_response['InternetGateways']:
            return gigi_response['InternetGateways'][0]['InternetGatewayId'], None
        else:
            return None, "No Internet Gateway found with the specified tag."
    except ClientError as e:
        return None, f"Error checking Internet Gateway existence: {e}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

def get_route_table_id(client: boto3.client, grti_rtb_tag: str) -> Union[str, str]:
    """
    Retrieve the Route Table ID based on the given tag.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        grti_rtb_tag (str): The tag name of the route table to retrieve.

    Returns:
        Union[str, str]: The Route Table ID or an error message.
    """
    try:
        # Describe route tables with the specified tag
        grti_response = client.describe_route_tables(
            Filters=[{'Name': 'tag:Name', 'Values': [grti_rtb_tag]}]
        )

        # Check if any route tables were found
        if grti_response['RouteTables']:
            return grti_response['RouteTables'][0]['RouteTableId']
        else:
            return f"No route table found with tag: {grti_rtb_tag}"
    except ClientError as e:
        return f"Client error retrieving route table ID: {e.response['Error']['Message']}"
    except Exception as e:
        return f"Error retrieving route table ID: {str(e)}"

def create_route(client: boto3.client, cr_dest_cidr_block: str, cr_igw_id: str, cr_rtb_id: str) -> Union[Tuple[Optional[str], Optional[str]], str]:
    """
    Create a route in the specified route table to direct traffic to the Internet Gateway.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        cr_dest_cidr_block (str): The destination CIDR block for the route.
        cr_igw_id (str): The Internet Gateway ID.
        cr_rtb_id (str): The Route Table ID.

    Returns:
        Union[Tuple[Optional[str], Optional[str]], str]: The Route Table ID or an error message.
    """
    try:
        # Create a route in the specified route table
        cr_response = client.create_route(
            DestinationCidrBlock=cr_dest_cidr_block,
            GatewayId=cr_igw_id,
            RouteTableId=cr_rtb_id
        )
        if cr_response['Return']:
            return cr_rtb_id, None
        else:
            return None, "Route creation failed, no RouteTableId returned."
    except ClientError as e:
        return None, f"Error creating route: {e.response['Error']['Message']}"
    except Exception as e:
        return None, f"Error creating route: {str(e)}"

if __name__ == "__main__":
    # Get the Internet Gateway ID based on the specified tag
    igw_id, error = get_internet_gateway_id(ec2, TAG_IGW_NAME)
    if error:
        print(error)
    else:
        print(f"Internet Gateway ID: {igw_id}")

    # Get the Route Table ID based on the specified tag
    rtb_id = get_route_table_id(ec2, TAG_RTB)
    if isinstance(rtb_id, str) and "No route table found" in rtb_id:
        print(rtb_id)
    else:
        print(f"Route Table ID: {rtb_id}")

    # Create a route in the Route Table to direct traffic to the Internet Gateway
    route_result = create_route(ec2, DEST_CIDR_BLOCK, igw_id, rtb_id)
    if isinstance(route_result, tuple) and route_result[1]:
        print(route_result[1])  # Print error if route creation fails
    else:
        print(f"Route created successfully in Route Table ID: {route_result[0]}")
