import boto3
from botocore.exceptions import ClientError
from typing import Union

# Initialize the EC2 client
ec2 = boto3.client('ec2')

# Constants for route table deletion
TAG_RTB = 'AcmeLabs-Dev-RouteTable'  # Name tag for the Route Table

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
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [grti_rtb_tag]
                }
            ]
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

def delete_route_table(client: boto3.client, drt_rtb_id: str) -> str:
    """
    Delete a Route Table by its ID.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        drt_rtb_id (str): The ID of the route table to delete.

    Returns:
        str: Success or error message regarding the deletion.
    """
    try:
        # Attempt to delete the specified route table
        drt_response = client.delete_route_table(
            RouteTableId=drt_rtb_id
        )
        # Check if the deletion was successful
        if drt_response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return f"Route Table {drt_rtb_id} deleted successfully."
        else:
            return f"Failed to delete Route Table {drt_rtb_id}. HTTP Status Code: {drt_response['ResponseMetadata']['HTTPStatusCode']}"
    except ClientError as e:
        return f"Client error deleting route table: {e.response['Error']['Message']}"
    except Exception as e:
        return f"Error deleting route table: {str(e)}"

if __name__ == "__main__":
    # Get the Route Table ID
    route_table_id = get_route_table_id(ec2, TAG_RTB)

    # Check for errors or no route table found
    if 'No route table found' in route_table_id or 'error' in route_table_id.lower():
        print(route_table_id)  # Print error message
    else:
        # Delete the Route Table
        result = delete_route_table(ec2, route_table_id)
        print(result)  # Print result of deletion
