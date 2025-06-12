import boto3
from botocore.exceptions import ClientError
from typing import List, Dict, Any
import fnmatch

def describe_subnets(client: Any, ds_filter: str = None) -> List[Dict[str, Any]]:
    """
    Describe subnets in the specified VPC using the provided EC2 client.

    Args:
        client: The Boto3 EC2 client used to make API calls.
        ds_filter: Optional filter for subnets by Tag with Key of 'Name'.

    Returns:
        A list of subnets with their details.

    Raises:
        ClientError: If the API call to describe subnets fails.
    """
    ds_filters = []
    if ds_filter:
        ds_filters.append({'Name': 'tag:Name', 'Values': [ds_filter]})

    try:
        ds_response = client.describe_subnets(Filters=ds_filters)  # API call to describe subnets with filters
        return ds_response['Subnets']  # Return the list of subnets
    except ClientError as e:
        print(f"Error retrieving subnets: {e}")  # Print error message for local debugging
        return []  # Return an empty list on error

def filter_subnets_by_name(fsbn_subnets: List[Dict[str, Any]], fsbn_name_filter: str) -> List[Dict[str, Any]]:
    """
    Filter subnets by name using case-insensitive matching and wildcard support.

    Args:
        fsbn_subnets: The list of subnets to filter.
        fsbn_name_filter: The name filter with possible wildcards.

    Returns:
        A list of subnets that match the name filter.
    """
    fsbn_filtered_subnets = []
    for fsbn_subnet in fsbn_subnets:
        # Extract the subnet name from the tags
        fsbn_subnet_name = next((tag['Value'] for tag in fsbn_subnet.get('Tags', []) if tag['Key'] == 'Name'), None)
        # Check if the subnet name matches the provided filter
        if fsbn_subnet_name and fnmatch.fnmatchcase(fsbn_subnet_name.lower(), fsbn_name_filter.lower()):
            fsbn_filtered_subnets.append(fsbn_subnet)  # Add matching subnet to the results
    return fsbn_filtered_subnets

def prompt_with_retries(pwr_prompt: str, pwr_max_retries: int = 3) -> str:
    """
    Prompt the user with a message and allow a maximum number of retries.

    Args:
        pwr_prompt: The message to display to the user.
        pwr_max_retries: The maximum number of attempts.

    Returns:
        The user input or 'no' if maximum retries reached.
    """
    pwr_retries = 0
    while pwr_retries < pwr_max_retries:
        pwr_response = input(pwr_prompt)  # Get user input
        if pwr_response:
            return pwr_response  # Return valid input
        else:
            pwr_retries += 1
            print(f"No input provided. You have {pwr_max_retries - pwr_retries} retry(s) left.")
    return "no"  # Return 'no' if maximum retries reached

if __name__ == "__main__":
    # Main body of the script
    ec2 = boto3.client('ec2')  # Create an EC2 client

    # Prompt for the filter value
    name_filter = prompt_with_retries("Enter the Name tag value to filter subnets (use '*' as wildcard): ")

    # Get the list of subnets without filtering first
    all_subnets = describe_subnets(ec2)

    # Filter the subnets based on the user input
    subnets = filter_subnets_by_name(all_subnets, name_filter if name_filter != "no" else "*")

    # Print details of each subnet in a formatted way
    for subnet in subnets:
        subnet_name = next((tag['Value'] for tag in subnet.get('Tags', []) if tag['Key'] == 'Name'), 'N/A')
        print(f"Name: {subnet_name}")
        print(f"CIDR Block: {subnet['CidrBlock']}")
        print(f"Availability Zone: {subnet['AvailabilityZone']}")
        print(f"VPC ID: {subnet['VpcId']}")
        print(f"Subnet ID: {subnet['SubnetId']}")
        print(f"State: {subnet['State']}")
        print("-" * 40)  # Separator line for better readability
