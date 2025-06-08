import boto3
from botocore.exceptions import ClientError

# Initialize the EC2 client
ec2 = boto3.client('ec2')

# Constants for internet gateway
TAG_IGW_NAME = 'AcmeLabs-Dev-IGW'  # Name tag for the Internet Gateway
TAG_IGW_ENV = 'Dev'  # Environment tag for the Internet Gateway

def internet_gateway_exists(client: boto3.client, igw_tag_name: str, igw_tag_env: str) -> bool:
    """
    Check if an Internet Gateway exists with the specified tags.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        igw_tag_name (str): The name tag of the Internet Gateway.
        igw_tag_env (str): The environment tag of the Internet Gateway.

    Returns:
        bool: True if the Internet Gateway exists, False otherwise.
    """
    try:
        # Describe Internet Gateways with specified filters
        igw_response = client.describe_internet_gateways(
            Filters=[
                {'Name': 'tag:Name', 'Values': [igw_tag_name]},
                {'Name': 'tag:Environment', 'Values': [igw_tag_env]}
            ]
        )

        # Return True if any Internet Gateways match the filters
        return len(igw_response['InternetGateways']) > 0

    except ClientError as e:
        print(f"Error checking Internet Gateway existence: {e.response['Error']['Message']}")
        return False  # Return False on error

def create_internet_gateway(client: boto3.client) -> str:
    """
    Create an Internet Gateway with specified tags.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.

    Returns:
        str: The ID of the created Internet Gateway or an error message.
    """
    try:
        # Create the Internet Gateway with specified tags
        cig_response = client.create_internet_gateway(
            TagSpecifications=[
                {
                    'ResourceType': 'internet-gateway',
                    'Tags': [
                        {'Key': 'Name', 'Value': TAG_IGW_NAME},
                        {'Key': 'Environment', 'Value': TAG_IGW_ENV}
                    ]
                }
            ]
        )

        # Access the Internet Gateway object from the response
        igw = cig_response['InternetGateway']

        # Return the ID of the created Internet Gateway
        return igw['InternetGatewayId']

    except ClientError as e:
        return f"Error creating Internet Gateway: {e.response['Error']['Message']}"

if __name__ == '__main__':
    # Check if the Internet Gateway already exists
    exists = internet_gateway_exists(ec2, TAG_IGW_NAME, TAG_IGW_ENV)

    if exists:
        print(
            f"Internet Gateway Exits:\n"
            f"    Name: {TAG_IGW_NAME}\n"
            f"    Environment: {TAG_IGW_ENV}"
        )
        exit(0)  # Exit if the Internet Gateway already exists

    # Create the Internet Gateway and handle any errors
    create_igw = create_internet_gateway(ec2)

    if 'Error' in create_igw:
        # Print the error message if an error occurred
        print(create_igw)
    else:
        # Print the ID of the created Internet Gateway
        print(f"Internet Gateway created with ID: '{create_igw}' for environment '{TAG_IGW_ENV}'")
