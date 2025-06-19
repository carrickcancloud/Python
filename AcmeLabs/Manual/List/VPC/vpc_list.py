import boto3
from botocore.exceptions import ClientError
from typing import List, Dict, Any, Optional

# Initialize the EC2 client
ec2 = boto3.client('ec2')

def get_vpc(client: boto3.client, gv_filters: List[Dict[str, Any]] = []) -> Optional[List[Dict[str, Any]]]:
    """
    Retrieve VPC information and names from AWS EC2.

    Args:
        client (boto3.client): The EC2 client.
        gv_filters (List[Dict[str, Any]], optional): Filters to apply to the VPC query. Defaults to an empty list.

    Returns:
        Optional[List[Dict[str, Any]]]: A list of dictionaries containing VPC information and names, or None if an error occurs.
    """
    try:
        # Attempt to describe VPCs using the provided filters
        gv_response = client.describe_vpcs(Filters=gv_filters)
        gv_vpc_info = []

        # Iterate through each VPC in the response
        for gv_vpc in gv_response['Vpcs']:
            gv_vpc_details = {
                'VpcId': gv_vpc['VpcId'],
                'CidrBlock': gv_vpc['CidrBlock'],
                'IsDefault': gv_vpc['IsDefault'],
                'Name': None  # Default value if no name is found
            }

            # Check for tags to find the Name
            if 'Tags' in gv_vpc:
                for gv_tag in gv_vpc['Tags']:
                    if gv_tag['Key'] == 'Name':
                        gv_vpc_details['Name'] = gv_tag['Value']
                        break  # Exit loop once name is found

            gv_vpc_info.append(gv_vpc_details)
            print(gv_vpc_details)  # Print VPC details for local use

        return gv_vpc_info  # Return the list of VPC information

    except ClientError as e:
        print(f"Error retrieving VPC info and names: {e}")  # Print error for local use
        return None  # Return None to indicate an error occurred

# Main execution block
if __name__ == "__main__":
    # No filters to get all VPCs
    filters = []

    # Get VPC information and names
    vpc_info = get_vpc(ec2, filters)

    # Check if VPC info was retrieved successfully
    if vpc_info is None:
        print("Failed to retrieve VPC information.")
