import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any, List

def describe_internet_gateways() -> Optional[List[Dict[str, Any]]]:
    """
    Describe Internet Gateways in the AWS EC2 service.

    Returns:
        Optional[List[Dict[str, Any]]]: A list of dictionaries containing
        information about Internet Gateways, or None if an error occurs.
    """
    ec2 = boto3.client('ec2')

    try:
        response = ec2.describe_internet_gateways()
        return response.get('InternetGateways', [])
    except ClientError as e:
        print(f"Error describing internet gateways: {e}")
        return None

def print_internet_gateways(internet_gateways: List[Dict[str, Any]]) -> None:
    """
    Print the Internet Gateway IDs and their VPC attachments.

    Args:
        internet_gateways (List[Dict[str, Any]]): The list of Internet Gateways.
    """
    for igw in internet_gateways:
        print(f"Internet Gateway ID: {igw['InternetGatewayId']}")
        for attachment in igw['Attachments']:
            print(f"VPC ID: {attachment['VpcId']}, State: {attachment['State']}")

if __name__ == "__main__":
    # Main body of the script
    internet_gateways = describe_internet_gateways()
    if internet_gateways is not None:
        print_internet_gateways(internet_gateways)
    else:
        print("No Internet Gateways found or an error occurred.")
