import boto3
from botocore.exceptions import ClientError
from typing import Any, Dict, List, Optional, Tuple, Union
import json

# Load configuration from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

def vpc_exists(client: boto3.client, a_cidr: str, a_tag_name: str, a_tag_env: str) -> Tuple[bool, str]:
    """
    Check if a VPC exists with the specified CIDR block and tags.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        a_cidr (str): The CIDR block of the VPC to check.
        a_tag_name (str): The name tag of the VPC to check.
        a_tag_env (str): The environment tag of the VPC to check.

    Returns:
        Tuple[bool, str]: (True if VPC exists, False otherwise, error message if applicable).
    """
    try:
        # Describe VPCs based on the provided filters
        a_response = client.describe_vpcs(
            Filters=[
                {'Name': 'cidr', 'Values': [a_cidr]},  # Filter by CIDR block
                {'Name': 'tag:Name', 'Values': [a_tag_name]},  # Filter by Name tag
                {'Name': 'tag:Environment', 'Values': [a_tag_env]}  # Filter by Environment tag
            ]
        )
        return (len(a_response['Vpcs']) > 0, "")
    except ClientError as e:
        return (False, f"Error checking VPC existence: {e}")

def subnet_exists(client: boto3.client, b_cidr_block: str, b_tag_name: str, b_tag_env , b_vpc_id: str, b_availability_zone: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a subnet exists based on CIDR block, tag name, VPC ID, and availability zone.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        b_cidr_block (str): CIDR block of the subnet.
        b_tag_name (str): Tag name of the subnet.
        b_tag_env (str): Environment tag of the subnet.
        b_vpc_id (str): VPC ID of the subnet.
        b_availability_zone (str): Availability zone of the subnet.

    Returns:
        Tuple[bool, Optional[str]]: (True if subnet exists, error message if applicable).
    """
    try:
        # Describe the subnets with the given filters
        b_response = client.describe_subnets(
            Filters=[
                {'Name': 'cidr-block', 'Values': [b_cidr_block]},  # Filter by CIDR block
                {'Name': 'tag:Name', 'Values': [b_tag_name]},  # Filter by tag name
                {'Name': 'tag:Environment', 'Values': [b_tag_env]},  # Filter by environment tag
                {'Name': 'vpc-id', 'Values': [b_vpc_id]},  # Filter by VPC ID
                {'Name': 'availability-zone', 'Values': [b_availability_zone]}  # Filter by availability zone
            ]
        )
        b_exists = len(b_response['Subnets']) > 0  # Check if any subnets were found
        return b_exists, None  # Return existence status and no error
    except ClientError as e:
        return False, f"Error describing subnets: {e}"  # Return error message

def route_table_exists(client: boto3.client, c_tag_name: str, c_tag_env: str, c_vpc_id: str) -> bool:
    """
    Check if a route table exists in the specified VPC with the given tags.

    Args:
        client (boto3.client): The Boto3 EC2 client.
        c_tag_name (str): The name tag of the route table.
        c_tag_env (str): The environment tag of the route table.
        c_vpc_id (str): The ID of the VPC.

    Returns:
        bool: True if the route table exists, False otherwise.
    """
    try:
        # Describe route tables with specified filters
        c_response = client.describe_route_tables(
            Filters=[
                {'Name': 'tag:Name', 'Values': [c_tag_name]},  # Filter for the Name tag
                {'Name': 'tag:Environment', 'Values': [c_tag_env]},  # Filter for the Environment tag
                {'Name': 'vpc-id', 'Values': [c_vpc_id]}  # Filter for the VPC ID
            ]
        )
        return len(c_response['RouteTables']) > 0  # Return True if any route tables are found
    except ClientError:
        return False  # Handle client error and return False

def internet_gateway_exists(client: boto3.client, d_tag_name: str, d_tag_env: str) -> bool:
    """
    Check if an Internet Gateway exists with the specified tags.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        d_tag_name (str): The name tag of the Internet Gateway.
        d_tag_env (str): The environment tag of the Internet Gateway.

    Returns:
        bool: True if the Internet Gateway exists, False otherwise.
    """
    try:
        # Describe Internet Gateways with specified filters
        d_response = client.describe_internet_gateways(
            Filters=[
                {'Name': 'tag:Name', 'Values': [d_tag_name]},
                {'Name': 'tag:Environment', 'Values': [d_tag_env]}
            ]
        )
        return len(d_response['InternetGateways']) > 0  # Return True if any Internet Gateways match the filters
    except ClientError as e:
        return False  # Simply return False on error

def get_vpc_id(client: boto3.client) -> Tuple[Optional[str], Optional[str]]:
    """
    Check if a VPC exists with the specified name tag 'AcmeLabs-Dev'.
    If it exists, return the VPC ID.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.

    Returns:
        Tuple[Optional[str], Optional[str]]: The VPC ID if the VPC exists, or an error message.
    """
    try:
        e_response = client.describe_vpcs(
            Filters=[
                {'Name': 'tag:Name', 'Values': [config["TAG_VPC_NAME"]]},
                {'Name': 'tag:Environment', 'Values': [config["TAG_ENV"]]}
            ]
        )
        if e_response['Vpcs']:
            return e_response['Vpcs'][0]['VpcId'], None
        else:
            return None, "No matching VPC found."
    except ClientError as e:
        return None, f"Error checking VPC existence: {e}"

def get_route_table_id(client: boto3.client, f_tag_name: str) -> Union[str, str]:
    """
    Retrieve the Route Table ID based on the given tag.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        f_tag_name (str): The tag name of the route table to retrieve.

    Returns:
        Union[str, str]: The Route Table ID or an error message.
    """
    try:
        f_response = client.describe_route_tables(
            Filters=[
                {'Name': 'tag:Name', 'Values': [f_tag_name]}
            ]
        )
        if f_response['RouteTables']:
            return f_response['RouteTables'][0]['RouteTableId']
        else:
            return f"No route table found with tag: {f_tag_name}"
    except ClientError as e:
        return f"Client error retrieving route table ID: {e.response['Error']['Message']}"
    except Exception as e:
        return f"Error retrieving route table ID: {str(e)}"

def get_internet_gateway_id(client: boto3.client, g_tag_name: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Check if an Internet Gateway exists with the specified name tag.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        g_tag_name (str): The name of the tag to filter the Internet Gateway.

    Returns:
        Tuple[Optional[str], Optional[str]]: The Internet Gateway ID if it exists, or an error message.
    """
    try:
        g_response = client.describe_internet_gateways(
            Filters=[
                {'Name': 'tag:Name', 'Values': [g_tag_name]}
            ]
        )
        if g_response['InternetGateways']:
            return g_response['InternetGateways'][0]['InternetGatewayId'], None
        else:
            return None, "No Internet Gateway found with the specified tag."
    except ClientError as e:
        return None, f"Error checking Internet Gateway existence: {e}"

def get_subnet_info(client: boto3.client, h_tag_name_prefix: str) -> Tuple[Union[Dict[str, Dict[str, str]], str], Union[List[str], str]]:
    """
    Get subnet information based on the specified tag prefix.

    Args:
        client: Boto3 EC2 client.
        h_tag_name_prefix: The starting prefix for the subnet names.

    Returns:
        A tuple containing a dictionary of subnet details and a list of subnet IDs or an error message.
    """
    h_filters = [
        {
            'Name': 'tag:Name',
            'Values': [f'{h_tag_name_prefix}*']
        }
    ]

    try:
        h_response = client.describe_subnets(Filters=h_filters)['Subnets']
        h_subnet_details = {}
        h_subnet_ids = []

        for h_subnet in h_response:
            if 'Tags' in h_subnet:
                for tag in h_subnet['Tags']:
                    if tag['Key'] == 'Name' and tag['Value'].startswith(h_tag_name_prefix):
                        h_subnet_ids.append(h_subnet['SubnetId'])
                        h_subnet_details[h_subnet['SubnetId']] = {
                            'Subnet ID': h_subnet['SubnetId'],
                            'CIDR Block': h_subnet['CidrBlock'],
                            'Availability Zone': h_subnet['AvailabilityZone'],
                            'VPC ID': h_subnet['VpcId']
                        }

        return h_subnet_details, h_subnet_ids
    except ClientError as e:
        return {}, f"Client error retrieving subnet information: {e.response['Error']['Message']}"
    except Exception as e:
        return {}, f"Error retrieving subnet information: {str(e)}"

def create_vpc(client: boto3.client, i_cidr_block: str, i_tag_name: str, i_tag_env: str) -> Tuple[str, str]:
    """
    Create a new VPC with the specified CIDR block and tags.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        i_cidr_block (str): The CIDR block for the VPC.
        i_tag_name (str): The name tag for the VPC.
        i_tag_env (str): The environment tag for the VPC.

    Returns:
        Tuple[str, str]: (VPC ID, error message if applicable).
    """
    try:
        # Create a new VPC with the specified CIDR block and tags
        i_response = client.create_vpc(
            CidrBlock=i_cidr_block,
            TagSpecifications=[
                {
                    'ResourceType': 'vpc',
                    'Tags': [
                        {'Key': 'Name', 'Value': i_tag_name},  # Name tag
                        {'Key': 'Environment', 'Value': i_tag_env}  # Environment tag
                    ]
                }
            ]
        )
        return (i_response['Vpc']['VpcId'], "")
    except ClientError as e:
        return ("", f"Error creating VPC: {e}")

def enable_dns_vpc(client: boto3.client, u_vpc_id: str) -> None:
    """
    Enables DNS support and hostname lookups for the specified VPC.

    Parameters:
    client (boto3.client): The EC2 client used to interact with AWS.
    vpc_id (str): The ID of the VPC to modify.

    Returns:
    None
    """
    # Step 1: Enable DNS support
    client.modify_vpc_attribute(
        VpcId=u_vpc_id,
        EnableDnsSupport={'Value': True}
    )
    print(f'DNS support enabled for VPC ID: {u_vpc_id}')

    # Step 2: Enable DNS hostname lookups
    client.modify_vpc_attribute(
        VpcId=u_vpc_id,
        EnableDnsHostnames={'Value': True}
    )
    print(f'DNS hostname lookups enabled for VPC ID: {u_vpc_id}')

def create_subnet(client: boto3.client, j_cidr_block: str, j_azs: str, j_tag_name: str, j_tag_env: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Create a subnet if it does not already exist.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        j_cidr_block (str): CIDR block for the new subnet.
        j_azs (str): Availability zone for the new subnet.
        j_tag_name (str): Tag name for the new subnet.
        j_tag_env (str): Environment tag for the new subnet.

    Returns:
        Tuple[Optional[str], Optional[str]]: Subnet ID if created, error message if applicable.
    """
    # Get the VPC ID to create the subnet in
    j_vpc_id, j_vpc_error = get_vpc_id(client)
    if j_vpc_error:
        return None, j_vpc_error  # Return an error if the VPC ID could not be retrieved

    # Check if the subnet already exists
    j_exists, j_error_message = subnet_exists(client, j_cidr_block, j_tag_name, j_tag_env, j_vpc_id, j_azs)
    if j_error_message:
        return None, j_error_message  # Return the error if it occurred

    if j_exists:
        # Return an error message if the subnet already exists
        return (None, f"Subnet Exists:\n"
                      f"    Name: {j_tag_name}\n"
                      f"    Environment: {j_tag_env}\n"
                      f"    CIDR Block: {j_cidr_block}\n"
                      f"    Availability Zone: {j_azs}"
                )
    try:
        # Create a new subnet with the specified parameters
        j_public_subnet = client.create_subnet(
            TagSpecifications=[
                {
                    'ResourceType': 'subnet',
                    'Tags': [
                        {'Key': 'Name', 'Value': j_tag_name},  # Tag for the subnet name
                        {'Key': 'Environment', 'Value': config['TAG_ENV']}  # Tag for the environment
                    ]
                }
            ],
            AvailabilityZone=j_azs,  # Specify the availability zone
            CidrBlock=j_cidr_block,  # Specify the CIDR block
            VpcId=j_vpc_id  # Specify the VPC ID to create the subnet in
        )
        j_subnet_id = j_public_subnet['Subnet']['SubnetId']  # Get the ID of the created subnet
        return j_subnet_id, None  # Return the subnet ID and no error
    except ClientError as e:
        return None, f"Error creating subnet: {e}"  # Return error message

def associate_route_table(client: boto3.client, k_subnets: List[str], k_rtb: str) -> List[Tuple[str, Union[Dict[str, str], str]]]:
    """
    Associate the specified route table with the given subnets.

    Args:
        client (boto3.client): Boto3 EC2 client.
        k_subnets (List[str]): List of subnet IDs to associate.
        k_rtb (str): The Route Table ID to associate with the subnets.

    Returns:
        List[Tuple[str, Union[Dict[str, str], str]]]: A list of tuples containing subnet IDs and the corresponding response or error message.
    """
    k_results = []
    for k_subnet in k_subnets:
        try:
            # Associate the route table with the subnet
            k_response = client.associate_route_table(
                SubnetId=k_subnet,
                RouteTableId=k_rtb
            )
            k_results.append((k_subnet, k_response))
        except ClientError as e:
            k_results.append((k_subnet, f"Client error associating Route Table: {e.response['Error']['Message']}"))
        except Exception as e:
            k_results.append((k_subnet, f"Error associating Route Table: {str(e)}"))

    return k_results

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
        l_response = client.create_internet_gateway(
            TagSpecifications=[
                {
                    'ResourceType': 'internet-gateway',
                    'Tags': [
                        {'Key': 'Name', 'Value': config['TAG_IGW_NAME']},
                        {'Key': 'Environment', 'Value': config['TAG_ENV']}
                    ]
                }
            ]
        )

        # Access the Internet Gateway object from the response
        l_igw = l_response['InternetGateway']

        # Return the ID of the created Internet Gateway
        return l_igw['InternetGatewayId']  # Return the ID of the created Internet Gateway

    except ClientError as e:
        return f"Error creating Internet Gateway: {e.response['Error']['Message']}"

def attach_internet_gateway(client: boto3.client, m_vpc_id: str, m_igw_id: str) -> Tuple[bool, str]:
    """
    Attach an Internet Gateway to the specified VPC.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        m_vpc_id (str): The ID of the VPC to attach the Internet Gateway to.
        m_igw_id (str): The ID of the Internet Gateway to attach.

    Returns:
        Tuple[bool, str]: True if the attachment was successful, or an error message.
    """
    try:
        # Attach the Internet Gateway to the VPC
        m_response = client.attach_internet_gateway(
            InternetGatewayId=m_igw_id,
            VpcId=m_vpc_id
        )
        return True, m_response  # Return success status and response
    except ClientError as e:
        return False, f"Error attaching Internet Gateway: {e}"  # Return error message

def create_route(client: boto3.client, n_dest_cidr_block: str, n_igw_id: str, n_rtb_id: str) -> Union[Tuple[Optional[str], Optional[str]], str]:
    """
    Create a route in the specified route table to direct traffic to the Internet Gateway.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        n_dest_cidr_block (str): The destination CIDR block for the route.
        n_igw_id (str): The Internet Gateway ID.
        n_rtb_id (str): The Route Table ID.

    Returns:
        Union[Tuple[Optional[str], Optional[str]], str]: The Route Table ID or an error message.
    """
    try:
        # Create a route in the specified route table
        n_response = client.create_route(
            DestinationCidrBlock=n_dest_cidr_block,
            GatewayId=n_igw_id,
            RouteTableId=n_rtb_id
        )
        if n_response['Return']:
            return n_rtb_id, None
        else:
            return None, "Route creation failed, no RouteTableId returned."
    except ClientError as e:
        return None, f"Error creating route: {e.response['Error']['Message']}"
    except Exception as e:
        return None, f"Error creating route: {str(e)}"

def delete_route(client: boto3.client, o_rtb_id: str, o_dest_cidr_block: str) -> str:
    """
    Delete a route from the specified Route Table.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        o_rtb_id (str): The ID of the Route Table from which to delete the route.
        o_dest_cidr_block (str): The destination CIDR block of the route to delete.

    Returns:
        str: A success or error message.
    """
    try:
        o_response = client.delete_route(
            RouteTableId=o_rtb_id,
            DestinationCidrBlock=o_dest_cidr_block
        )
        if o_response['ResponseMetadata']['HTTPStatusCode'] != 200:
            return f"Failed to delete route: {o_response}"
        return f"Route deleted successfully from Route Table {o_rtb_id} for CIDR block {o_dest_cidr_block}"
    except ClientError as e:
        return f"Client error deleting route: {e.response['Error']['Message']}"
    except Exception as e:
        return f"Error deleting route: {str(e)}"

def detach_internet_gateway(client: boto3.client, p_igw_id: str, p_vpc_id: str) -> str:
    """
    Detach an Internet Gateway from a specified VPC.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        p_igw_id (str): The ID of the Internet Gateway to detach.
        p_vpc_id (str): The ID of the VPC from which to detach the Internet Gateway.

    Returns:
        str: A message indicating the result of the detach operation.
    """
    try:
        p_response = client.detach_internet_gateway(
            InternetGatewayId=p_igw_id,
            VpcId=p_vpc_id,
        )
        if p_response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return f"Internet Gateway {p_igw_id} detached from VPC {p_vpc_id} successfully."
        else:
            return f"Failed to detach Internet Gateway {p_igw_id} from VPC {p_vpc_id}. HTTP Status Code: {p_response['ResponseMetadata']['HTTPStatusCode']}"
    except ClientError as e:
        return f"Client error detaching Internet Gateway: {e.response['Error']['Message']}"

def delete_internet_gateway(client: boto3.client, q_igw_id: str) -> str:
    """
    Delete the specified Internet Gateway.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        q_igw_id (str): The ID of the Internet Gateway to delete.

    Returns:
        str: A message indicating the result of the delete operation.
    """
    try:
        client.delete_internet_gateway(
            InternetGatewayId=q_igw_id
        )
        return f"Internet Gateway {q_igw_id} deleted successfully."
    except ClientError as e:
        return f"Error deleting Internet Gateway: {e}"

def disassociate_subnets_from_route_table(client: boto3.client, r_tag_name: str) -> Union[str, str]:
    """
    Disassociate non-main subnets from a route table identified by the given tag.

    Args:
        client (boto3.client): Boto3 EC2 client.
        r_tag_name (str): The tag name of the route table from which to disassociate subnets.

    Returns:
        str: A message indicating the result of the disassociation operation or an error message.
    """
    try:
        r_route_table_id = get_route_table_id(client, r_tag_name)
        if isinstance(r_route_table_id, str) and r_route_table_id.startswith("No route table found"):
            return r_route_table_id

        r_disassociation_count = 0
        r_removed_subnets = []

        r_associations = client.describe_route_tables(RouteTableIds=[r_route_table_id])['RouteTables'][0]['Associations']

        for r_response in r_associations:
            if not r_response['Main']:
                client.disassociate_route_table(AssociationId=r_response['RouteTableAssociationId'])
                r_disassociation_count += 1
                r_removed_subnets.append(r_response['SubnetId'])

        if r_disassociation_count > 0:
            return (f"Successfully disassociated {r_disassociation_count} subnet(s) from route table {r_route_table_id}. \n"
                    f"Removed subnets: {', '.join(r_removed_subnets)}.")
        else:
            return f"No non-main subnets found associated with route table {r_route_table_id}."
    except ClientError as e:
        return f"Client error disassociating subnet from route table: {e.response['Error']['Message']}"
    except Exception as e:
        return f"Error disassociating subnet from route table: {str(e)}"

def delete_route_table(client: boto3.client, s_rtb_id: str) -> str:
    """
    Delete a Route Table by its ID.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        s_rtb_id (str): The ID of the route table to delete.

    Returns:
        str: Success or error message regarding the deletion.
    """
    try:
        s_response = client.delete_route_table(
            RouteTableId=s_rtb_id
        )
        if s_response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return f"Route Table {s_rtb_id} deleted successfully."
        else:
            return f"Failed to delete Route Table {s_rtb_id}. HTTP Status Code: {s_response['ResponseMetadata']['HTTPStatusCode']}"
    except ClientError as e:
        return f"Client error deleting route table: {e.response['Error']['Message']}"
    except Exception as e:
        return f"Error deleting route table: {str(e)}"

def delete_vpc(client: boto3.client, t_vpc_id: str) -> Optional[str]:
    """
    Delete the specified VPC by its ID.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        t_vpc_id (str): The ID of the VPC to delete.

    Returns:
        Optional[str]: Success status code or an error message.
    """
    try:
        t_response = client.delete_vpc(VpcId=t_vpc_id)
        return t_response.get('ResponseMetadata', {}).get('HTTPStatusCode', None)
    except ClientError as e:
        return f"Error deleting VPC: {e.response['Error']['Message']}"
    except Exception as e:
        return f"Unexpected error deleting VPC: {str(e)}"
