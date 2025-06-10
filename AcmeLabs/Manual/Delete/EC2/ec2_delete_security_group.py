import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any

# Initialize the EC2 client
ec2 = boto3.client('ec2')

def get_security_group_id_by_name(client: boto3.client, gsgibn_tag_name: str) -> str:
    """
    Retrieve the security group ID based on the tag key 'Name'.

    Args:
        client (boto3.client): The EC2 client.
        gsgibn_tag_name (str): The value of the tag 'Name' to search for.

    Returns:
        str: The security group ID if found, else None.
    """
    try:
        gsgibn_response = client.describe_security_groups(Filters=[{
            'Name': 'tag:Name',
            'Values': [gsgibn_tag_name]
        }])

        gsgibn_security_groups = gsgibn_response.get('SecurityGroups', [])
        if gsgibn_security_groups:
            return gsgibn_security_groups[0]['GroupId']  # Return the first matching security group ID

    except ClientError as e:
        print(f"An error occurred: {e}")

    return None

def delete_security_group(client: boto3.client, dsg_group_id: str) -> Dict[str, Any]:
    """
    Deletes a specified security group from EC2 using its ID.

    Args:
        client (boto3.client): The EC2 client.
        dsg_group_id (str): The ID of the security group to delete.

    Returns:
        Dict[str, Any]: A dictionary containing the success status and message.
    """
    dsg_response = {
        "success": False,
        "message": ""
    }

    try:
        client.delete_security_group(GroupId=dsg_group_id)
        dsg_response["success"] = True
        dsg_response["message"] = f"Security group with ID '{dsg_group_id}' deleted successfully."
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidGroup.NotFound':
            dsg_response["message"] = f"Security group with ID '{dsg_group_id}' not found."
        else:
            dsg_response["message"] = f"An error occurred: {e}"

    return dsg_response

def prompt_with_retries(pwr_prompt: str, pwr_max_retries: int = 3) -> str:
    pwr_retries = 0
    while pwr_retries < pwr_max_retries:
        pwr_response = input(pwr_prompt).strip()
        if pwr_response:
            return pwr_response
        else:
            pwr_retries += 1
            print(f"No input provided. You have {pwr_max_retries - pwr_retries} retry(s) left.")

    raise Exception("Maximum retries reached. Exiting the program.")

if __name__ == "__main__":
    try:
        # Ask if the security group is in the default VPC
        is_default_vpc = prompt_with_retries("Is the security group in the default VPC? (yes/no): ").strip().lower()

        if is_default_vpc == 'yes':
            # Prompt for the security group name or ID
            group_input = prompt_with_retries("Enter the security group Name or ID to delete: ")
            # Check if it's a valid ID (assuming IDs are in the format 'sg-xxxxxxxx')
            group_id = group_input if group_input.startswith('sg-') else get_security_group_id_by_name(ec2, group_input)
        else:
            # If not in the default VPC, we must use the group ID
            group_id = prompt_with_retries("Enter the security group ID to delete: ")

        # Call the function to delete the security group
        result = delete_security_group(ec2, group_id)
        print("Deletion status:", result["success"])
        print("Message:", result["message"])

    except Exception as e:
        print(str(e))  # Print the error message
        exit(1)  # Exit with a non-zero status to indicate error
