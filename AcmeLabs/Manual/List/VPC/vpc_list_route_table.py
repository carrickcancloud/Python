import boto3
from botocore.exceptions import ClientError
from typing import Any, Dict

# Initialize the EC2 client
ec2 = boto3.client('ec2')

def describe_route_tables(client: boto3.client) -> None:
    """
    Describe route tables in the AWS EC2 service.

    This function retrieves and prints route table details including VPC ID,
    route table ID, associations, and routes. It handles potential errors during
    the API call and prints appropriate error messages.

    Args:
        client (boto3.client): The EC2 client for making API calls.
    """

    try:
        # Attempt to retrieve route tables
        response: Dict[str, Any] = client.describe_route_tables()
    except ClientError as e:
        # Handle API errors and print a user-friendly message
        print(f"Error retrieving route tables: {e}")
        return  # Exit the function on error

    # Iterate over route tables in the response
    for rtb in response.get('RouteTables', []):
        print(f"VPC ID: {rtb['VpcId']}\nRoute Table ID: {rtb['RouteTableId']}")

        # Iterate over associations within the route table
        for association in rtb.get('Associations', []):
            print(f"Route Table Association ID: {association['RouteTableAssociationId']}")
            if 'SubnetId' in association:
                print(f"Subnet ID: {association['SubnetId']}")

        # Iterate over routes within the route table
        for route in rtb.get('Routes', []):
            print(f"Destination CIDR Block: {route['DestinationCidrBlock']}, Gateway ID: {route['GatewayId']}")

        # Print separator line for better readability
        print("-" * 40)

if __name__ == "__main__":
    describe_route_tables(ec2)
