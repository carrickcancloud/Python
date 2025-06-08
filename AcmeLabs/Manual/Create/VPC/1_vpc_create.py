import boto3
from botocore.exceptions import ClientError

# Initialize the EC2 client
ec2 = boto3.client('ec2')

# Constants for VPC
TAG_VPC_NAME = 'AcmeLabs-Dev'  # Name tag for the VPC
TAG_VPC_ENV = 'Dev'  # Environment tag for the VPC
CIDR_BLOCK = '10.0.0.0/16'  # CIDR block for the VPC

def vpc_exists(client: boto3.client, ve_cidr: str, ve_tag_name: str, ve_tag_env: str) -> tuple[bool, str]:
    """
    Check if a VPC exists with the specified CIDR block and tags.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        ve_cidr (str): The CIDR block of the VPC to check.
        ve_tag_name (str): The name tag of the VPC to check.
        ve_tag_env (str): The environment tag of the VPC to check.

    Returns:
        tuple: (bool, str) indicating if the VPC exists and an error message if applicable.
    """
    try:
        # Describe VPCs based on the provided filters
        ve_response = client.describe_vpcs(
            Filters=[
                {'Name': 'cidr', 'Values': [ve_cidr]},  # Filter by CIDR block
                {'Name': 'tag:Name', 'Values': [ve_tag_name]},  # Filter by Name tag
                {'Name': 'tag:Environment', 'Values': [ve_tag_env]}  # Filter by Environment tag
            ]
        )
        # Return True if any VPCs match the filters
        return (len(ve_response['Vpcs']) > 0, "")
    except ClientError as e:
        error_message = f"Error checking VPC existence: {e}"
        print(error_message)  # Print error for local use
        return (False, error_message)

def create_vpc(client: boto3.client, cv_cidr_block: str, cv_tag_name: str, cv_tag_env: str) -> tuple[str, str]:
    """
    Create a new VPC with the specified CIDR block and tags.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        cv_cidr_block (str): The CIDR block for the VPC.
        cv_tag_name (str): The name tag for the VPC.
        cv_tag_env (str): The environment tag for the VPC.

    Returns:
        tuple: (str, str) containing the VPC ID and an error message if applicable.
    """
    try:
        # Create a new VPC with the specified CIDR block and tags
        cv_response = client.create_vpc(
            CidrBlock=cv_cidr_block,
            TagSpecifications=[
                {
                    'ResourceType': 'vpc',
                    'Tags': [
                        {'Key': 'Name', 'Value': cv_tag_name},  # Name tag
                        {'Key': 'Environment', 'Value': cv_tag_env}  # Environment tag
                    ]
                }
            ]
        )
        # Return VPC ID and no error message
        return (cv_response['Vpc']['VpcId'], "")
    except ClientError as e:
        error_message = f"Error creating VPC: {e}"
        print(error_message)  # Print error for local use
        return ("", error_message)

if __name__ == '__main__':
    # Check if the specified VPC exists
    vpc_exists_result, vpc_exists_error = vpc_exists(ec2, CIDR_BLOCK, TAG_VPC_NAME, TAG_VPC_ENV)

    if vpc_exists_result:
        print(f"VPC Exists:\n"
              f"    Name: {TAG_VPC_NAME}\n"
              f"    Environment: {TAG_VPC_ENV}\n"
              f"    CIDR Block: {CIDR_BLOCK}"
        )
    else:
        vpc_id, create_vpc_error = create_vpc(ec2, CIDR_BLOCK, TAG_VPC_NAME, TAG_VPC_ENV)

        if create_vpc_error:
            print(create_vpc_error)  # Print error if VPC creation fails
        else:
            # Print details of the newly created VPC
            print(f"VPC Details:\n"
                  f"    VPC ID: {vpc_id}\n"
                  f"    Name: {TAG_VPC_NAME}")
