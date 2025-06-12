import boto3
from botocore.exceptions import ClientError
from typing import List, Optional
import fnmatch

# Initialize the EC2 client
ec2 = boto3.client('ec2')

# List of instance states
INSTANCE_STATES = [
    "pending",
    "running",
    "shutting-down",
    "terminated",
    "stopping",
    "stopped",
    "failed"
]

def list_ec2_instances(client: boto3.client, lei_name_filter: Optional[str] = None, lei_state_filter: Optional[str] = None) -> List[str]:
    """
    List EC2 instances with specific details, optionally filtered by name and state.

    Args:
        client: The EC2 client to use for API calls.
        lei_name_filter: Optional filter for instance name.
        lei_state_filter: Optional filter for instance state.

    Returns:
        A list of strings containing details about each EC2 instance.

    Raises:
        ClientError: If the API call fails.
    """
    lei_instance_details: List[str] = []  # List to store instance details as strings
    lei_next_token: Optional[str] = None  # Initialize next_token for pagination

    while True:
        try:
            # Describe EC2 instances with pagination
            lei_response = client.describe_instances(NextToken=lei_next_token) if lei_next_token else client.describe_instances()
        except ClientError as e:
            print(f"Failed to describe instances: {e}")  # Log the error message
            return []  # Return an empty list on error

        # Iterate through the reservations and instances in the response
        for lei_reservation in lei_response.get('Reservations', []):
            for lei_instance in lei_reservation.get('Instances', []):
                try:
                    # Safely retrieve instance details
                    lei_instance_name = next((tag['Value'] for tag in lei_instance.get('Tags', []) if tag['Key'] == 'Name'), 'N/A')
                    lei_instance_id = lei_instance.get('InstanceId', 'N/A')
                    lei_instance_type = lei_instance.get('InstanceType', 'N/A')
                    lei_state = lei_instance.get('State', {}).get('Name', 'N/A')
                    lei_launch_time = lei_instance.get('LaunchTime', 'N/A')
                    lei_architecture = lei_instance.get('Architecture', 'N/A')
                    lei_ami = lei_instance.get('ImageId', 'N/A')
                    lei_security_groups = [sg.get('GroupName', 'N/A') for sg in lei_instance.get('SecurityGroups', [])]
                    lei_key_name = lei_instance.get('KeyName', 'N/A')
                    lei_vpc_id = lei_instance.get('VpcId', 'N/A')
                    lei_subnet_id = lei_instance.get('SubnetId', 'N/A')
                    lei_availability_zone = lei_instance.get('Placement', {}).get('AvailabilityZone', 'N/A')
                    lei_private_ip = lei_instance.get('PrivateIpAddress', 'N/A')
                    lei_public_ip = lei_instance.get('PublicIpAddress', 'N/A')

                    # Debugging output
                    print(f"Checking instance: {lei_instance_name}, State: {lei_state}")

                    # Check if the instance matches the filters
                    if (lei_name_filter and not fnmatch.fnmatchcase(lei_instance_name.lower(), lei_name_filter.lower())) or \
                       (lei_state_filter and lei_state.lower() != lei_state_filter.lower()):
                        continue  # Skip this instance if it doesn't match the filters

                    # Build the instance info string
                    lei_instance_info = (
                        f"Instance Name: {lei_instance_name}\n"
                        f"Instance ID: {lei_instance_id}\n"
                        f"Instance Type: {lei_instance_type}\n"
                        f"State: {lei_state}\n"
                        f"Launch Time: {lei_launch_time}\n"
                        f"Architecture: {lei_architecture}\n"
                        f"AMI: {lei_ami}\n"
                        f"Security Groups: {lei_security_groups or ['N/A']}\n"
                        f"Key Name: {lei_key_name}\n"
                        f"VPC ID: {lei_vpc_id}\n"
                        f"Subnet ID: {lei_subnet_id}\n"
                        f"Availability Zone: {lei_availability_zone}\n"
                        f"Private IP Address: {lei_private_ip}\n"
                        f"Public IP Address: {lei_public_ip}\n"
                    )
                    lei_instance_details.append(lei_instance_info)  # Add instance info to the list
                except KeyError as e:
                    print(f"Missing data for instance {lei_instance.get('InstanceId', 'unknown')}: {e}")  # Log specific EC2 Instance processing errors

        # Check if there is a next token for pagination
        lei_next_token = lei_response.get('NextToken')
        if not lei_next_token:
            break  # Exit the loop if there are no more pages

    return lei_instance_details  # Return the list of instance details

def prompt_with_retries(pwr_prompt: str, pwr_max_retries: int = 3) -> Optional[str]:
    """
    Prompt the user with a message and allow a maximum number of retries.

    Args:
        pwr_prompt (str): The message to display to the user.
        pwr_max_retries (int): The maximum number of attempts.

    Returns:
        Optional[str]: The user input or None if maximum retries reached.
    """
    pwr_retries = 0
    while pwr_retries < pwr_max_retries:
        pwr_response = input(pwr_prompt)  # Get user input
        if pwr_response:
            return pwr_response  # Return valid input
        else:
            pwr_retries += 1
            print(f"No input provided. You have {pwr_max_retries - pwr_retries} retry(s) left.")

    return None  # Return None if maximum retries reached

def select_instance_state() -> Optional[str]:
    """
    Prompt the user to select an instance state from the available options.

    Returns:
        Optional[str]: The selected instance state or None if no valid selection.
    """
    print("Select an instance state from the following options:")
    for sis_index, sis_state in enumerate(INSTANCE_STATES, start=1):
        print(f"{sis_index}. {sis_state}")

    while True:
        try:
            sis_choice = int(input("Enter the number corresponding to your choice: "))
            if 1 <= sis_choice <= len(INSTANCE_STATES):
                return INSTANCE_STATES[sis_choice - 1]  # Return the selected state
            else:
                print("Invalid choice. Please select a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    name_filter = prompt_with_retries("Enter instance name filter (use '*' as wildcard): ")
    state_filter = select_instance_state()  # Get the state filter from the user

    instances = list_ec2_instances(ec2, name_filter, state_filter)
    if instances:  # Check if instances were retrieved successfully
        for instance_detail in instances:
            print(instance_detail)  # Print each instance detail
            print('-' * 40)  # Separator line of 40 dashes
    else:
        print("No instances found or an error occurred.")  # Message for no instances found
