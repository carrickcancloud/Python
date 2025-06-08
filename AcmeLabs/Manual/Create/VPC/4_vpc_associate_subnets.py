import boto3
from botocore.exceptions import ClientError
from typing import Dict, List, Tuple, Union

# Initialize the EC2 client
ec2 = boto3.client('ec2')

# Constants for route table association
TAG_SUBNET = 'AcmeLabs-Dev-Public-Subnet'
TAG_RTB = 'AcmeLabs-Dev-RouteTable'

def get_route_table_id(client: boto3.client, grti_rtb_tag: str) -> Union[str, str]:
    """
    Retrieve the Route Table ID based on the given tag.

    Args:
        client: Boto3 EC2 client.
        grti_rtb_tag: The tag name of the route table to retrieve.

    Returns:
        The Route Table ID or an error message.
    """
    try:
        # Describe route tables with the specified tag
        grti_response = client.describe_route_tables(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [grti_rtb_tag]
                }
            ]
        )
        # Check if any route tables were found
        if grti_response['RouteTables']:
            return grti_response['RouteTables'][0]['RouteTableId']
        else:
            return f"No route table found with tag: {grti_rtb_tag}"
    except ClientError as e:
        return f"Client error retrieving route table ID: {e.response['Error']['Message']}"
    except Exception as e:
        return f"Error retrieving route table ID: {str(e)}"

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

def associate_route_table(client: boto3.client, art_subnets: List[str], art_rtb: str) -> List[Tuple[str, Union[Dict[str, str], str]]]:
    """
    Associate the specified route table with the given subnets.

    Args:
        client: Boto3 EC2 client.
        art_subnets: List of subnet IDs to associate.
        art_rtb: The Route Table ID to associate with the subnets.

    Returns:
        A list of tuples containing subnet IDs and the corresponding response or error message.
    """
    art_results = []
    for art_subnet in art_subnets:
        try:
            # Associate the route table with the subnet
            art_response = client.associate_route_table(
                SubnetId=art_subnet,
                RouteTableId=art_rtb
            )
            art_results.append((art_subnet, art_response))
        except ClientError as e:
            art_results.append((art_subnet, f"Client error associating Route Table: {e.response['Error']['Message']}"))
        except Exception as e:
            art_results.append((art_subnet, f"Error associating Route Table: {str(e)}"))

    return art_results

if __name__ == '__main__':
    try:
        # Get the Route Table ID
        rtb_id = get_route_table_id(ec2, TAG_RTB)
        if "Error" in rtb_id:
            print(rtb_id)
            exit(1)

        # Get subnet details and IDs
        subnet_details, subnet_ids = get_subnet_info(ec2, TAG_SUBNET)
        if isinstance(subnet_ids, str):  # Check if it's an error message
            print(subnet_ids)
            exit(1)

        if not subnet_ids:
            print("No subnets found with the specified tag.")
        else:
            # Print details of each found subnet
            for subnet_id in subnet_ids:
                details = subnet_details[subnet_id]
                print(f"Subnet Found:\n"
                      f"    Subnet ID: {subnet_id}\n"
                      f"    CIDR Block: {details['CIDR Block']}\n"
                      f"    Availability Zone: {details['Availability Zone']}\n"
                      f"    VPC ID: {details['VPC ID']}\n")

            # Associate the route table with the subnets
            response = associate_route_table(ec2, subnet_ids, rtb_id)
            for subnet_id, result in response:
                if isinstance(result, dict):
                    print(
                        f"Successfully Associated:\n"
                        f"    RouteTable ID: {rtb_id}\n"
                        f"    Subnet ID: {subnet_id}"
                    )
                else:
                    print(
                        f"Failed Association:\n"
                        f"    RouteTable: {rtb_id}\n"
                        f"    Subnet ID {subnet_id}: {result}"
                    )

    except Exception as e:
        print(f"An error occurred in the main execution: {str(e)}")
