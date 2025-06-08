import boto3
from botocore.exceptions import ClientError
from typing import Tuple, Optional

# Initialize the EC2 client
ec2 = boto3.client('ec2')

# Constants for subnets
TAG_VPC_NAME = 'AcmeLabs-Dev'  # Name tag for the VPC
CIDR_PUBLIC_SUBNETS = [  # List of CIDR blocks for public subnets
    '10.0.1.0/24',
    '10.0.2.0/24',
    '10.0.3.0/24'
]
TAG_SUBNETS = [  # List of tags for identifying the subnets
    'AcmeLabs-Dev-Public-Subnet-1',
    'AcmeLabs-Dev-Public-Subnet-2',
    'AcmeLabs-Dev-Public-Subnet-3'
]
TAG_SUBNET_ENV = 'Dev'  # Environment tag for the subnets
AVAILABILITY_ZONES = [  # List of availability zones for the subnets
    'us-east-1a',
    'us-east-1b',
    'us-east-1c'
]

def get_vpc_id(client: boto3.client) -> Tuple[Optional[str], Optional[str]]:
    """
    Retrieve the VPC ID based on the VPC name.

    Parameters:
    - client: Boto3 EC2 client

    Returns:
    - Tuple containing the VPC ID and an error message (if any)
    """
    try:
        gvi_response = client.describe_vpcs(
            Filters=[
                {'Name': 'tag:Name', 'Values': [TAG_VPC_NAME]}
            ]
        )
        if gvi_response['Vpcs']:
            return gvi_response['Vpcs'][0]['VpcId'], None
        else:
            return None, "No matching VPC found."
    except ClientError as e:
        return None, f"Error checking VPC existence: {e}"

def subnet_exists(se_cidr_block: str, se_tag_name: str, se_tag_env: str, se_vpc_id: str, se_availability_zone: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a subnet exists based on provided parameters.

    Parameters:
    - se_cidr_block: CIDR block of the subnet
    - se_tag_name: Name tag of the subnet
    - se_tag_env: Environment tag of the subnet
    - se_vpc_id: VPC ID where the subnet is located
    - se_availability_zone: Availability zone of the subnet

    Returns:
    - Tuple containing a boolean indicating existence and an error message (if any)
    """
    try:
        se_response = ec2.describe_subnets(
            Filters=[
                {'Name': 'cidr-block', 'Values': [se_cidr_block]},
                {'Name': 'tag:Name', 'Values': [se_tag_name]},
                {'Name': 'tag:Environment', 'Values': [se_tag_env]},
                {'Name': 'vpc-id', 'Values': [se_vpc_id]},
                {'Name': 'availability-zone', 'Values': [se_availability_zone]}
            ]
        )
        se_exists = len(se_response['Subnets']) > 0
        return se_exists, None
    except ClientError as e:
        return False, f"Error describing subnets: {e}"

def create_subnet(cs_cidr_block: str, cs_azs: str, cs_tag_name: str, cs_tag_env: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Create a subnet if it doesn't already exist.

    Parameters:
    - cs_cidr_block: CIDR block for the new subnet
    - cs_azs: Availability zone for the new subnet
    - cs_tag_name: Name tag for the new subnet
    - cs_tag_env: Environment tag for the new subnet

    Returns:
    - Tuple containing the created subnet ID and an error message (if any)
    """
    cs_vpc_id, cs_vpc_error = get_vpc_id(ec2)
    if cs_vpc_error:
        return None, cs_vpc_error

    cs_exists, cs_error_message = subnet_exists(cs_cidr_block, cs_tag_name, cs_tag_env, cs_vpc_id, cs_azs)
    if cs_error_message:
        return None, cs_error_message

    if cs_exists:
        return None, (
            f"Subnet Exists:\n"
            f"    Name: {cs_tag_name}\n"
            f"    Environment: {cs_tag_env}\n"
            f"    CIDR Block: {cs_cidr_block}\n"
            f"    Availability Zone: {cs_azs}."
        )

    try:
        cs_public_subnet = ec2.create_subnet(
            TagSpecifications=[
                {
                    'ResourceType': 'subnet',
                    'Tags': [
                        {'Key': 'Name', 'Value': cs_tag_name},
                        {'Key': 'Environment', 'Value': cs_tag_env}
                    ]
                }
            ],
            AvailabilityZone=cs_azs,
            CidrBlock=cs_cidr_block,
            VpcId=cs_vpc_id
        )
        cs_subnet_id = cs_public_subnet['Subnet']['SubnetId']
        return cs_subnet_id, None
    except ClientError as e:
        return None, f"Error creating subnet: {e}"

if __name__ == '__main__':
    # Iterate over CIDR blocks, availability zones, and tags to create subnets
    for cidr, az, tag in zip(CIDR_PUBLIC_SUBNETS, AVAILABILITY_ZONES, TAG_SUBNETS):
        subnet_id, error = create_subnet(cidr, az, tag, TAG_SUBNET_ENV)  # Use TAG_SUBNET_ENV directly
        if error:
            print(error)  # Print error for local use
        else:
            print(f"Created Subnet ID: {subnet_id}")  # Print success message
