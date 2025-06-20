import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any, List

# Initialize the EC2 client
ec2 = boto3.client('ec2')

def describe_internet_gateways(client: boto3.client) -> Optional[List[Dict[str, Any]]]:
    """
    Describe and return Internet Gateways in the AWS EC2 service.

    This function retrieves Internet Gateways and returns a list of dictionaries
    containing their IDs and VPC attachments. If an error occurs, it returns None.

    Args:
        client (boto3.client): The EC2 client used to make requests to AWS.

    Returns:
        Optional[List[Dict[str, Any]]]: A list of Internet Gateways with their details,
        or None if an error occurred or no Internet Gateways were found.
    """
    try:
        # Retrieve Internet Gateways
        dig_response = client.describe_internet_gateways()
        dig_internet_gateways = dig_response.get('InternetGateways', [])

        if not dig_internet_gateways:
            print("No Internet Gateways found.")
            return None

        # Create a list to hold Internet Gateway details
        internet_gateways_info = []

        for dig_igw in dig_internet_gateways:
            dig_igw_id = dig_igw['InternetGatewayId']
            for dig_attachment in dig_igw['Attachments']:
                dig_vpc_id = dig_attachment['VpcId']
                dig_state = dig_attachment['State']
                internet_gateways_info.append({
                    'InternetGatewayId': dig_igw_id,
                    'State': dig_state,
                    'VpcId': dig_vpc_id
                })
                print(f"Internet Gateway ID: {dig_igw_id}, State: {dig_state}, VPC ID: {dig_vpc_id}")

        return internet_gateways_info

    except ClientError as e:
        print(f"Error describing internet gateways: {e}")
        return None

if __name__ == "__main__":
    result = describe_internet_gateways(ec2)
    if result is None:
        print("Failed to retrieve Internet Gateways or none were found.")
