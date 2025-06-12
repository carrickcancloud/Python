import boto3
from botocore.exceptions import ClientError
from typing import Tuple, Optional, List
import time

# Initialize EC2 client
ec2 = boto3.client('ec2')

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

def read_user_data(rud_file_path: str) -> Optional[str]:
    """
    Read user data from a bash script file.

    Args:
        rud_file_path (str): The path to the bash script file.

    Returns:
        Optional[str]: The user data as a string or None if reading fails.
    """
    try:
        with open(rud_file_path, 'r') as rud_file:
            return rud_file.read()  # Read as plain text
    except FileNotFoundError as e:
        print(f"Error reading user data file: {e}")
        return None

def launch_ec2_instances(client: boto3.client) -> Tuple[Optional[List[str]], Optional[List[str]], Optional[List[str]]]:
    """
    Launch multiple EC2 instances based on user input.

    Args:
        client (boto3.client): The EC2 client for making API calls.

    Returns:
        Tuple[Optional[List[str]], Optional[List[str]], Optional[List[str]]]:
        A list of instance IDs, a list of Name tag values, and a list of Public IP addresses,
        or (None, None, None) on failure.
    """
    # Prompt for user input with error handling
    lei_image_id = prompt_with_retries("Enter AMI ImageId: ")
    if lei_image_id is None:
        print("Exiting due to lack of input for AMI ImageId.")
        return None, None, None

    lei_instance_type = prompt_with_retries("Enter InstanceType: ")
    if lei_instance_type is None:
        print("Exiting due to lack of input for InstanceType.")
        return None, None, None

    lei_key_name = prompt_with_retries("Enter KeyName: ")
    if lei_key_name is None:
        print("Exiting due to lack of input for KeyName.")
        return None, None, None

    lei_max_count = prompt_with_retries("Enter MaxCount: ")
    if lei_max_count is None:
        print("Exiting due to lack of input for MaxCount.")
        return None, None, None

    lei_min_count = prompt_with_retries("Enter MinCount: ")
    if lei_min_count is None:
        print("Exiting due to lack of input for MinCount.")
        return None, None, None

    lei_security_group_ids = prompt_with_retries("Enter SecurityGroupIds (comma-separated): ")
    if lei_security_group_ids is None:
        print("Exiting due to lack of input for SecurityGroupIds.")
        return None, None, None

    lei_subnet_id = prompt_with_retries("Enter SubnetId: ")
    if lei_subnet_id is None:
        print("Exiting due to lack of input for SubnetId.")
        return None, None, None

    lei_tag_name_value = prompt_with_retries("Enter Tag value for the key 'Name': ")
    if lei_tag_name_value is None:
        print("Exiting due to lack of input for Tag value.")
        return None, None, None

    # Read user data from the file
    lei_user_data = read_user_data('userdata.sh')
    if lei_user_data is None:
        print("Exiting due to failure in reading user data.")
        return None, None, None

    # Prepare the request to launch the instances
    try:
        lei_response = client.run_instances(
            ImageId=lei_image_id,
            InstanceType=lei_instance_type,
            KeyName=lei_key_name,
            MaxCount=int(lei_max_count),
            MinCount=int(lei_min_count),
            NetworkInterfaces=[
                {
                    'AssociatePublicIpAddress': True,  # Allocate a public IP
                    'DeviceIndex': 0,
                    'SubnetId': lei_subnet_id,
                    'Groups': [lei_sg.strip() for lei_sg in lei_security_group_ids.split(',')],
                },
            ],
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': lei_tag_name_value,
                        },
                        {
                            'Key': 'Environment',
                            'Value': 'Dev',
                        },
                    ],
                },
            ],
            UserData=lei_user_data,
        )
    except ClientError as e:
        print(f"Failed to launch EC2 instances: {e}")
        return None, None, None

    # Extract instance IDs
    lei_instance_ids = [lei_instance['InstanceId'] for lei_instance in lei_response['Instances']]

    # Wait for all instances to be in the running state
    print("Waiting for instances to be in running state...")
    lei_waiter = client.get_waiter('instance_running')
    lei_waiter.wait(InstanceIds=lei_instance_ids)

    # Retrieve public IP addresses for all instances
    lei_instance_info = client.describe_instances(InstanceIds=lei_instance_ids)
    lei_public_ips = []
    lei_name_values = []

    for lei_reservation in lei_instance_info['Reservations']:
        for lei_instance in lei_reservation['Instances']:
            lei_public_ips.append(lei_instance.get('PublicIpAddress', None))
            lei_name_values.append(next((lei_tag['Value'] for lei_tag in lei_instance.get('Tags', []) if lei_tag['Key'] == 'Name'), None))

    return lei_instance_ids, lei_name_values, lei_public_ips

# Main execution block
if __name__ == "__main__":
    instance_ids, name_values, public_ips = launch_ec2_instances(ec2)
    if instance_ids and name_values and public_ips:
        for instance_id, name_value, public_ip in zip(instance_ids, name_values, public_ips):
            print(
                f"Instance launched successfully:\n"
                f"  Instance ID: {instance_id}\n"
                f"  Name Value: {name_value}\n"
                f"  Public IP: {public_ip}\n"
                f"{'-' * 40}"  # Separator for readability
            )
    else:
        print("Instance launch failed.")
