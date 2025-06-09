import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from typing import List, Dict, Any

# Initialize the EC2 client with specific configurations
ec2 = boto3.client('ec2', config=Config(connect_timeout=5, read_timeout=30, retries={'max_attempts': 3}))

# AWS account ID for filtering AMIs
our_aws_account_id = '<AWS Account ID>'

def list_amis(client: Any) -> List[str]:
    """
    List Amazon Machine Images (AMIs) owned by the specified AWS account.

    Parameters:
    client (Any): The boto3 EC2 client.

    Returns:
    List[str]: A list of strings containing AMI details.
    """
    instance_image_details = []
    next_token = None

    # Define filters for Quick Start AMIs
    filters = [
        {
            'Name': 'owner-id',
            'Values': [our_aws_account_id]
        }
    ]

    while True:
        try:
            # Describe EC2 AMIs with pagination
            response = client.describe_images(Filters=filters, NextToken=next_token) if next_token else client.describe_images()

            # Iterate through the EC2 AMIs in the response
            for image in response.get('Images', []):
                try:
                    # Construct AMI information
                    image_info = (
                        f"Name: {image.get('Name', 'N/A')}\n"
                        f"ImageId: {image.get('ImageId', 'N/A')}\n"
                        f"OwnerId: {image.get('OwnerId', 'N/A')}\n"
                        f"Description: {image.get('Description', 'N/A')}\n"
                        f"State: {image.get('State', 'N/A')}\n"
                        f"Public: {image.get('Public', 'N/A')}\n"
                        f"ProductCodes: {image.get('ProductCodes', 'N/A')}\n"
                        f"CreationDate: {image.get('CreationDate', 'N/A')}\n"
                        f"DeprecationTime: {image.get('DeprecationTime', 'N/A')}\n"
                        f"Architecture: {image.get('Architecture', 'N/A')}\n"
                        f"ImageType: {image.get('ImageType', 'N/A')}\n"
                        f"PlatformDetails: {image.get('PlatformDetails', 'N/A')}\n"
                        f"VirtualizationType: {image.get('VirtualizationType', 'N/A')}\n"
                        f"BootMode: {image.get('BootMode', 'N/A')}\n"
                        f"Platform: {image.get('Platform', 'N/A')}"
                    )
                    instance_image_details.append(image_info)  # Append the AMI info to the list
                except Exception as e:
                    print(f"Error processing AMI data: {e}")  # Log specific AMI processing errors

            # Check if there's a NextToken for pagination
            next_token = response.get('NextToken')
            if not next_token:
                break  # Exit the loop if there's no more data

        except ClientError as e:
            print(f"ClientError retrieving AMI data: {e.response['Error']['Message']}")  # Log AWS error message
            break
        except Exception as e:
            print(f"Error retrieving AMI data: {e}")  # Log error for EC2 AMI retrieval
            break

    return instance_image_details  # Return the list of AMIs

if __name__ == "__main__":
    amis = list_amis(ec2)  # Call the function to list AMIs
    for ami in amis:
        print(ami)  # Print each AMI's details
