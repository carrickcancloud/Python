import boto3
from botocore.exceptions import ClientError
from typing import Union

# Initialize the EC2 client
ec2 = boto3.client('ec2')

# Constants for route deletion
TAG_RTB = 'AcmeLabs-Dev-RouteTable'  # Name tag for the Route Table
DEST_CIDR_BLOCK = '0.0.0.0/0'  # Destination CIDR block for the route

def get_route_table_id(client: boto3.client, grt_rtb_tag: str) -> Union[str, str]:
    """
    Retrieve the Route Table ID based on the given tag.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        grt_rtb_tag (str): The tag name of the route table to retrieve.

    Returns:
        Union[str, str]: The Route Table ID or an error message.
    """
    try:
        # Describe route tables with the specified tag
        grt_response = client.describe_route_tables(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [grt_rtb_tag]
                }
            ]
        )
        # Check if any route tables were found
        if grt_response['RouteTables']:
            return grt_response['RouteTables'][0]['RouteTableId']
        else:
            return f"No route table found with tag: {grt_rtb_tag}"
    except ClientError as e:
        return f"Client error retrieving route table ID: {e.response['Error']['Message']}"
    except Exception as e:
        return f"Error retrieving route table ID: {str(e)}"

def delete_route(client: boto3.client, drt_rtb_id: str, drt_dest_cidr_block: str) -> str:
    """
    Delete a route from the specified Route Table.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        drt_rtb_id (str): The ID of the Route Table from which to delete the route.
        drt_dest_cidr_block (str): The destination CIDR block of the route to delete.

    Returns:
        str: A success or error message.
    """
    try:
        # Attempt to delete the specified route
        drt_response = client.delete_route(
            RouteTableId=drt_rtb_id,
            DestinationCidrBlock=drt_dest_cidr_block
        )
        # Check for successful deletion
        if drt_response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return f"Failed to delete route: {drt_response}"
        return f"Route deleted successfully from Route Table {drt_rtb_id} for CIDR block {drt_dest_cidr_block}"
    except ClientError as e:
        return f"Client error deleting route: {e.response['Error']['Message']}"
    except Exception as e:
        return f"Error deleting route: {str(e)}"

if __name__ == "__main__":
    # Get the Route Table ID
    route_table_id = get_route_table_id(ec2, TAG_RTB)

    # Check if the result is an error message
    if isinstance(route_table_id, str) and "No route table found" in route_table_id:
        print(route_table_id)  # Print the error message for local use
    else:
        # Delete the route from the Route Table
        result = delete_route(ec2, route_table_id, DEST_CIDR_BLOCK)
        print(result)  # Print the result of the deletion
