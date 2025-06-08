import boto3
from botocore.exceptions import ClientError
from typing import Union

# Initialize the EC2 client
ec2 = boto3.client('ec2')

# Constants for route table disassociation
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

def disassociate_subnets_from_route_table(client: boto3.client, dsfrt_rtb_tag: str) -> Union[str, str]:
    """
    Disassociate non-main subnets from a route table identified by the given tag.

    Args:
        client: Boto3 EC2 client.
        dsfrt_rtb_tag: The tag name of the route table from which to disassociate subnets.

    Returns:
        A message indicating the result of the disassociation operation or an error message.
    """
    try:
        # Retrieve the route table ID based on the tag
        dsfrt_route_table_id = get_route_table_id(client, dsfrt_rtb_tag)

        # Check if the route table ID retrieval was successful
        if isinstance(dsfrt_route_table_id, str) and dsfrt_route_table_id.startswith("No route table found"):
            return dsfrt_route_table_id  # Return if no route table was found

        dsfrt_disassociation_count = 0  # Counter for disassociated subnets
        dsfrt_removed_subnets = []  # List to hold removed subnet IDs

        # Retrieve the associations for the route table
        dsfrt_associations = client.describe_route_tables(RouteTableIds=[dsfrt_route_table_id])['RouteTables'][0]['Associations']

        # Iterate through associations and disassociate non-main subnets
        for dsfrt_response in dsfrt_associations:
            if not dsfrt_response['Main']:
                client.disassociate_route_table(AssociationId=dsfrt_response['RouteTableAssociationId'])
                dsfrt_disassociation_count += 1  # Increment the counter
                dsfrt_removed_subnets.append(dsfrt_response['SubnetId'])  # Add the removed subnet ID to the list

        # Return success message if subnets were disassociated
        if dsfrt_disassociation_count > 0:
            return (f"Successfully disassociated {dsfrt_disassociation_count} subnet(s) from route table {dsfrt_route_table_id}. \n"
                    f"Removed subnets: {', '.join(dsfrt_removed_subnets)}.")
        else:
            return f"No non-main subnets found associated with route table {dsfrt_route_table_id}."
    except ClientError as e:
        return f"Client error disassociating subnet from route table: {e.response['Error']['Message']}"
    except Exception as e:
        return f"Error disassociating subnet from route table: {str(e)}"

if __name__ == "__main__":
    # Execute the disassociation of subnets from the route table and print the result
    result = disassociate_subnets_from_route_table(ec2, TAG_RTB)
    print(result)
