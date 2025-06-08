import boto3
from typing import List, Dict, Any, Optional

def get_vpc_info(client: boto3.client, filters: List[Dict[str, Any]] = []) -> Optional[List[Dict[str, Any]]]:
    """
    Retrieve VPC information from AWS EC2.

    Args:
        client (boto3.client): The EC2 client.
        filters (List[Dict[str, Any]], optional): Filters to apply to the VPC query. Defaults to an empty list.

    Returns:
        Optional[List[Dict[str, Any]]]: A list of VPC information dictionaries or None if an error occurs.
    """
    try:
        response = client.describe_vpcs(Filters=filters)
        vpc_info = []
        for vpc in response['Vpcs']:
            vpc_details = {
                'VpcId': vpc['VpcId'],
                'CidrBlock': vpc['CidrBlock'],
                'IsDefault': vpc['IsDefault']
            }
            vpc_info.append(vpc_details)
            print(vpc_details)  # Print for local use
        return vpc_info
    except Exception as e:
        print(f"Error retrieving VPC info: {e}")  # Print error for local use
        return None

def get_vpc_name(client: boto3.client, filters: List[Dict[str, Any]] = []) -> Optional[List[str]]:
    """
    Retrieve the names of VPCs from AWS EC2 based on tags.

    Args:
        client (boto3.client): The EC2 client.
        filters (List[Dict[str, Any]], optional): Filters to apply to the VPC query. Defaults to an empty list.

    Returns:
        Optional[List[str]]: A list of VPC names or None if an error occurs.
    """
    try:
        response = client.describe_vpcs(Filters=filters)
        vpc_names = []
        for vpc in response['Vpcs']:
            if 'Tags' in vpc:
                for tag in vpc['Tags']:
                    if tag['Key'] == 'Name':
                        vpc_names.append(tag['Value'])
                        print(tag['Value'])  # Print for local use
        return vpc_names
    except Exception as e:
        print(f"Error retrieving VPC names: {e}")  # Print error for local use
        return None


if __name__ == "__main__":
    # Main body of the script
    ec2 = boto3.client('ec2')

    filters = [{'Name': 'isDefault', 'Values': ['true']}]

    # Get VPC information
    vpc_info = get_vpc_info(ec2, filters)

    # Get VPC names
    vpc_names = get_vpc_name(ec2, filters)
