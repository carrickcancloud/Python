import boto3
from botocore.exceptions import ClientError
from typing import Dict, List, Tuple, Union

# Initialize the Boto3 EC2 client
ec2 = boto3.client('ec2')

# Constants for subnet deletion
TAG_SUBNET = 'AcmeLabs-Dev-Public-Subnet'

def get_subnet_info(client: boto3.client, gsi_tag_start: str) -> Tuple[Union[Dict[str, Dict[str, str]], str], Union[List[str], str]]:
    """
    Get subnet information based on the specified tag prefix.

    Args:
        client: Boto3 EC2 client.
        gsi_tag_start: The starting prefix for the subnet names.

    Returns:
        A tuple containing a dictionary of subnet details and a list of subnet IDs or an error message.
    """
    gsi_filters = [
        {
            'Name': 'tag:Name',
            'Values': [f'{gsi_tag_start}*']
        }
    ]

    try:
        # Describe subnets with the specified filters
        gsi_response = client.describe_subnets(Filters=gsi_filters)['Subnets']
        gsi_subnet_details = {}
        gsi_subnet_ids = []

        # Iterate through the subnets and gather details
        for gsi_subnet in gsi_response:
            if 'Tags' in gsi_subnet:
                for tag in gsi_subnet['Tags']:
                    if tag['Key'] == 'Name' and tag['Value'].startswith(gsi_tag_start):
                        gsi_subnet_ids.append(gsi_subnet['SubnetId'])
                        gsi_subnet_details[gsi_subnet['SubnetId']] = {
                            'Subnet ID': gsi_subnet['SubnetId'],
                            'CIDR Block': gsi_subnet['CidrBlock'],
                            'Availability Zone': gsi_subnet['AvailabilityZone'],
                            'VPC ID': gsi_subnet['VpcId']
                        }

        return gsi_subnet_details, gsi_subnet_ids
    except ClientError as e:
        return {}, f"Client error retrieving subnet information: {e.response['Error']['Message']}"
    except Exception as e:
        return {}, f"Error retrieving subnet information: {str(e)}"

def main() -> None:
    """
    Main function to execute the subnet information retrieval and deletion process.
    """
    # Get subnet details and IDs based on the specified tag
    subnet_details, subnet_ids = get_subnet_info(ec2, TAG_SUBNET)

    # Print subnet details
    if subnet_ids:
        for subnet_id in subnet_ids:
            print(f"Subnet ID: {subnet_id}, Details: {subnet_details.get(subnet_id, {})}")
    else:
        print("No matching subnets found.")

    # Now delete each subnet
    for subnet_id in subnet_ids:
        try:
            response = ec2.delete_subnet(SubnetId=subnet_id)
            print(f"Deleted Subnet ID: {subnet_id}")
        except ClientError as e:
            print(f"Failed to delete Subnet ID: {subnet_id}, Error: {e.response['Error']['Message']}")
        except Exception as e:
            print(f"Failed to delete Subnet ID: {subnet_id}, Error: {str(e)}")

if __name__ == "__main__":
    main()
