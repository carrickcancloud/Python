import boto3
from botocore.exceptions import ClientError
from typing import Optional, Tuple

# Initialize the Boto3 EC2 client
ec2 = boto3.client('ec2')

# Constants for VPC deletion
TAG_VPC_NAME = 'AcmeLabs-Dev'  # Name tag for the VPC

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
        # Describe VPCs based on the provided filters
        gvi_response = client.describe_vpcs(
            Filters=[
                {'Name': 'tag:Name', 'Values': [TAG_VPC_NAME]}  # Filter by Name tag
            ]
        )

        # Check if any VPCs match the filters and return the VPC ID
        if gvi_response['Vpcs']:
            return gvi_response['Vpcs'][0]['VpcId'], None  # Return the VPC ID of the first matching VPC
        else:
            return None, "No matching VPC found."  # No matching VPC found
    except ClientError as e:
        return None, f"Error checking VPC existence: {e}"  # Return error message
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"  # Handle unexpected errors

def delete_vpc(client: boto3.client, dv_vpc_id: str) -> Optional[str]:
    """
    Delete the specified VPC by its ID.

    Args:
        client (boto3.client): The EC2 client used to interact with AWS.
        dv_vpc_id (str): The ID of the VPC to delete.

    Returns:
        Optional[str]: Success status code or an error message.
    """
    try:
        # Attempt to delete the specified VPC
        dv_response = client.delete_vpc(VpcId=dv_vpc_id)
        return dv_response.get('ResponseMetadata', {}).get('HTTPStatusCode', None)  # Return the HTTP status code
    except ClientError as e:
        return f"Error deleting VPC: {e.response['Error']['Message']}"  # Return error message
    except Exception as e:
        return f"Unexpected error deleting VPC: {str(e)}"  # Handle unexpected errors

if __name__ == "__main__":
    # Get the VPC ID and any error message
    vpc_id, error_message = get_vpc_id(ec2)

    if error_message:
        print(error_message)  # Print any error message from VPC retrieval
    elif vpc_id:
        # Proceed to delete the VPC if it exists
        delete_status = delete_vpc(ec2, vpc_id)
        if isinstance(delete_status, int):
            print(f"VPC {vpc_id} deleted successfully.")  # Print success message
        else:
            print(delete_status)  # Print any error message from deletion
    else:
        print("No VPC to delete.")  # Handle case where no VPC was found
