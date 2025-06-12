import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any, Tuple, List

# List of AWS regions
REGIONS: List[str] = [
    'ap-northeast-1',
    'ap-northeast-2',
    'ap-south-1',
    'ap-southeast-1',
    'ap-southeast-2',
    'ca-central-1',
    'eu-central-1',
    'eu-west-1',
    'us-east-1',
    'us-east-2',
    'us-west-1',
    'us-west-2'
]

# List of architectures
ARCHITECTURES: List[str] = [
    'x86_64',
    'arm64'
]

# List of OS flavors
OS_FLAVORS: List[str] = [
    'Ubuntu',
    'Amazon Linux'
]

def select_option(so_options: List[str], so_prompt: str) -> Optional[str]:
    """Prompt the user to select an option from a list.

    Args:
        so_options (List[str]): List of options to choose from.
        so_prompt (str): Prompt message for the user.

    Returns:
        Optional[str]: The selected option or None if no valid option is selected.
    """
    print(so_prompt)
    for i, so_option in enumerate(so_options):
        print(f"{i + 1}. {so_option}")

    while True:
        so_choice = prompt_with_retries("Select an option (number): ")
        if so_choice is None:
            return None  # Gracefully exit if no input after retries
        try:
            so_choice = int(so_choice) - 1
            if 0 <= so_choice < len(so_options):
                return so_options[so_choice]
            else:
                print("Invalid choice. Please select a valid option.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def prompt_with_retries(pwr_prompt: str, pwr_max_retries: int = 3) -> Optional[str]:
    """Prompt the user with a message and allow a maximum number of retries.

    Args:
        pwr_prompt: The message to display to the user.
        pwr_max_retries: The maximum number of attempts.

    Returns:
        Optional[str]: The user input or None if maximum retries reached.
    """
    pwr_retries = 0
    while pwr_retries < pwr_max_retries:
        pwr_response = input(pwr_prompt)
        if pwr_response:
            return pwr_response
        else:
            pwr_retries += 1
            print(f"No input provided. You have {pwr_max_retries - pwr_retries} retry(s) left.")

    print("Maximum retries reached. Exiting.")
    return None  # Return None if maximum retries reached

def get_latest_ubuntu_ami(glua_architecture: str) -> Optional[Dict[str, Any]]:
    """Fetch the latest Ubuntu AMI ID.

    Args:
        glua_architecture (str): The architecture to filter AMIs.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the latest Ubuntu AMI details or None if not found.
    """
    try:
        # Define filters for Ubuntu AMIs
        glua_filters = [
            {'Name': 'architecture', 'Values': [glua_architecture]},
            {'Name': 'name', 'Values': ['*server*']}
        ]

        # Describe images based on filters and owner ID for Ubuntu
        glua_response = ec2.describe_images(Filters=glua_filters, Owners=['099720109477'])

        # Find the latest AMI by creation date
        if glua_response['Images']:
            glua_latest_ami = max(glua_response['Images'], key=lambda x: x['CreationDate'])
            return glua_latest_ami
        else:
            print("No images found for the specified filters.")
            return None

    except ClientError as e:
        print(f"ClientError: {e.response['Error']['Message']}")
        return None

def get_latest_amazon_linux_amis(glala_architecture: str) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Fetch the latest Amazon Linux 2 and Amazon Linux 2023 AMI IDs.

    Args:
        glala_architecture (str): The architecture to filter AMIs.

    Returns:
        Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]: A tuple containing the latest Amazon Linux 2 and Amazon Linux 2023 AMI details or None if not found.
    """
    try:
        # Define filters for Amazon Linux 2 and Amazon Linux 2023 AMIs
        glala_filters_amazon_linux2 = [
            {'Name': 'architecture', 'Values': [glala_architecture]},
            {'Name': 'name', 'Values': ['amzn2-ami-kernel-5.10-hvm-*']}
        ]
        glala_filters_amazon_linux2023 = [
            {'Name': 'architecture', 'Values': [glala_architecture]},
            {'Name': 'name', 'Values': ['al2023-ami-2023*']}
        ]

        # Describe images for Amazon Linux 2 using its owner ID
        glala_response_amazon_linux2 = ec2.describe_images(Filters=glala_filters_amazon_linux2, Owners=['137112412989'])
        glala_amazon_linux2_ami = max(glala_response_amazon_linux2['Images'], key=lambda x: x['CreationDate']) if \
        glala_response_amazon_linux2['Images'] else None

        # Describe images for Amazon Linux 2023 using its owner ID
        glala_response_amazon_linux2023 = ec2.describe_images(Filters=glala_filters_amazon_linux2023, Owners=['amazon'])
        glala_amazon_linux2023_ami = max(glala_response_amazon_linux2023['Images'], key=lambda x: x['CreationDate']) if \
        glala_response_amazon_linux2023['Images'] else None

        return glala_amazon_linux2_ami, glala_amazon_linux2023_ami

    except ClientError as e:
        print(f"ClientError: {e.response['Error']['Message']}")
        return None, None

def list_latest_ami_details(llad_architecture: str, os_flavor: str) -> None:
    """List the details of the latest AMIs based on the selected OS flavor.

    Args:
        llad_architecture (str): The architecture to filter AMIs.
        os_flavor (str): The selected OS flavor (Ubuntu or Amazon Linux).
    """
    if os_flavor == 'Ubuntu':
        # Fetch the latest Ubuntu AMI
        llad_ubuntu_ami_info = get_latest_ubuntu_ami(llad_architecture)
        if llad_ubuntu_ami_info:
            print("Latest Ubuntu Server AMI:")
            print(f"  AMI ID: {llad_ubuntu_ami_info['ImageId']}")
            print(f"  Name: {llad_ubuntu_ami_info.get('Name', 'N/A')}")
            print(f"  Description: {llad_ubuntu_ami_info.get('Description', 'N/A')}")
            print(f"  Location: {llad_ubuntu_ami_info.get('ImageLocation', 'N/A')}")
            print(f"  Creation Date: {llad_ubuntu_ami_info.get('CreationDate', 'N/A')}")
            print(f"  Architecture: {llad_ubuntu_ami_info.get('Architecture', 'N/A')}")
            print(f"  State: {llad_ubuntu_ami_info.get('State', 'N/A')}")
            print(f"  Owner: {llad_ubuntu_ami_info.get('OwnerId', 'N/A')}")
            print(f"  Public: {llad_ubuntu_ami_info.get('Public', 'N/A')}")
        else:
            print("No Ubuntu AMIs found.")

    elif os_flavor == 'Amazon Linux':
        # Fetch the latest Amazon Linux AMIs
        llad_amazon_linux2_info, llad_amazon_linux2023_info = get_latest_amazon_linux_amis(llad_architecture)

        if llad_amazon_linux2_info:
            print("Latest Amazon Linux 2 AMI:")
            print(f"  AMI ID: {llad_amazon_linux2_info['ImageId']}")
            print(f"  Name: {llad_amazon_linux2_info.get('Name', 'N/A')}")
            print(f"  Description: {llad_amazon_linux2_info.get('Description', 'N/A')}")
            print(f"  Location: {llad_amazon_linux2_info.get('ImageLocation', 'N/A')}")
            print(f"  Creation Date: {llad_amazon_linux2_info.get('CreationDate', 'N/A')}")
            print(f"  Architecture: {llad_amazon_linux2_info.get('Architecture', 'N/A')}")
            print(f"  State: {llad_amazon_linux2_info.get('State', 'N/A')}")
            print(f"  Owner: {llad_amazon_linux2_info.get('OwnerId', 'N/A')}")
            print(f"  Public: {llad_amazon_linux2_info.get('Public', 'N/A')}")
        else:
            print("No Amazon Linux 2 AMIs found.")

        if llad_amazon_linux2023_info:
            print("Latest Amazon Linux 2023 AMI:")
            print(f"  AMI ID: {llad_amazon_linux2023_info['ImageId']}")
            print(f"  Name: {llad_amazon_linux2023_info.get('Name', 'N/A')}")
            print(f"  Description: {llad_amazon_linux2023_info.get('Description', 'N/A')}")
            print(f"  Location: {llad_amazon_linux2023_info.get('ImageLocation', 'N/A')}")
            print(f"  Creation Date: {llad_amazon_linux2023_info.get('CreationDate', 'N/A')}")
            print(f"  Architecture: {llad_amazon_linux2023_info.get('Architecture', 'N/A')}")
            print(f"  State: {llad_amazon_linux2023_info.get('State', 'N/A')}")
            print(f"  Owner: {llad_amazon_linux2023_info.get('OwnerId', 'N/A')}")
            print(f"  Public: {llad_amazon_linux2023_info.get('Public', 'N/A')}")
        else:
            print("No Amazon Linux 2023 AMIs found.")

if __name__ == "__main__":
    # Select region, architecture, and OS flavor from user
    region_name: Optional[str] = select_option(REGIONS, "Please select an AWS region:")
    if region_name is None:
        print("No region selected. Exiting.")
        exit()

    architecture: Optional[str] = select_option(ARCHITECTURES, "Please select an architecture:")
    if architecture is None:
        print("No architecture selected. Exiting.")
        exit()

    os_flavor: Optional[str] = select_option(OS_FLAVORS, "Please select an OS flavor:")
    if os_flavor is None:
        print("No OS flavor selected. Exiting.")
        exit()

    # Initialize the EC2 client with the user-specified region
    ec2 = boto3.client('ec2', region_name=region_name)

    # Call the unified function with the selected architecture and OS flavor
    list_latest_ami_details(architecture, os_flavor)
