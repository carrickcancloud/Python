import boto3
from botocore.exceptions import ClientError
from typing import List, Dict, Any

def describe_subnets(ec2_client: Any) -> List[Dict[str, Any]]:
    """
    Describe subnets in the specified VPC using the provided EC2 client.

    Args:
        ec2_client: The Boto3 EC2 client used to make API calls.

    Returns:
        A list of subnets with their details.

    Raises:
        ClientError: If the API call to describe subnets fails.
    """
    try:
        response = ec2_client.describe_subnets()  # API call to describe subnets
        return response['Subnets']  # Return the list of subnets
    except ClientError as e:
        print(f"Error retrieving subnets: {e}")  # Print error message for local debugging
        return []  # Return an empty list on error

if __name__ == "__main__":
    # Main body of the script
    ec2 = boto3.client('ec2')  # Create an EC2 client
    subnets = describe_subnets(ec2)  # Get the list of subnets

    # Print details of each subnet
    for subnet in subnets:
        print(f"VPC ID: {subnet['VpcId']}, Subnet ID: {subnet['SubnetId']}, CIDR Block: {subnet['CidrBlock']}")
