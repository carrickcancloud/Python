import boto3
from botocore.exceptions import ClientError
from typing import Any, Dict, List

def describe_route_tables() -> None:
    """
    Describe route tables in the AWS EC2 service.

    This function retrieves and prints route table details including VPC ID,
    route table ID, associations, and routes. It handles potential errors during
    the API call and prints appropriate error messages.
    """
    ec2 = boto3.client('ec2')

    try:
        response: Dict[str, Any] = ec2.describe_route_tables()
    except ClientError as e:
        print(f"Error retrieving route tables: {e}")
        return  # Exit the function on error

    # Iterate over route tables
    for rtb in response['RouteTables']:
        print(f"VPC ID: {rtb['VpcId']}\nRoute Table ID: {rtb['RouteTableId']}")

        # Iterate over associations
        for association in rtb['Associations']:
            print(f"Route Table Association ID: {association['RouteTableAssociationId']}")
            if 'SubnetId' in association:
                print(f"Subnet ID: {association['SubnetId']}")

        # Iterate over routes
        for route in rtb['Routes']:
            print(f"Destination CIDR Block: {route['DestinationCidrBlock']}, Gateway ID: {route['GatewayId']}")

if __name__ == "__main__":
    # Main body of the script
    describe_route_tables()
