import boto3
from botocore.exceptions import ClientError
from typing import Union, Dict, Any, List, Optional
import re

# Initialize the EC2 client
ec2 = boto3.client('ec2')

def security_group_exists(client: boto3.client, sge_group_name: str, sge_vpc_id: str) -> bool:
    """Check if a security group exists in the specified VPC.

    Args:
        client: The Boto3 EC2 client.
        sge_group_name: The name of the security group.
        sge_vpc_id: The VPC ID where the security group is located.

    Returns:
        True if the security group exists, False otherwise.
    """
    try:
        sge_response = client.describe_security_groups(
            Filters=[
                {'Name': 'group-name', 'Values': [sge_group_name]},
                {'Name': 'vpc-id', 'Values': [sge_vpc_id]}
            ]
        )
        return len(sge_response['SecurityGroups']) > 0
    except ClientError as e:
        return False  # Return False on error for existence check

def create_security_group(client: boto3.client, csg_group_name: str, csg_description: str, csg_vpc_id: str) -> Union[
    Dict[str, Any], str]:
    """Create a security group in the specified VPC.

    Args:
        client: The Boto3 EC2 client.
        csg_group_name: The name of the security group.
        csg_description: Description of the security group.
        csg_vpc_id: The VPC ID where the security group will be created.

    Returns:
        The response from the create security group API or an error message.
    """
    try:
        csg_response = client.create_security_group(
            GroupName=csg_group_name,
            Description=csg_description,
            VpcId=csg_vpc_id,
        )
        return csg_response
    except ClientError as e:
        return f"An error occurred while creating security group: {e}"

def tag_security_group(client: boto3.client, tsg_group_id: str, tsg_tag_value: str) -> str:
    """Tag a security group with a specified name.

    Args:
        client: The Boto3 EC2 client.
        tsg_group_id: The ID of the security group.
        tsg_tag_value: The value for the tag.

    Returns:
        Success or error message.
    """
    try:
        tsg_response = client.create_tags(
            Resources=[tsg_group_id],
            Tags=[{'Key': 'Name', 'Value': tsg_tag_value}]
        )
        if tsg_response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return "Security group tagged successfully."
        else:
            return f"Failed to tag security group id: {tsg_group_id}"
    except ClientError as e:
        return f"An error occurred while tagging security group: {e}"

def cr_is_valid_cidr(civc_cidr: str) -> bool:
    """Check if the input is a valid CIDR block.

    Args:
        civc_cidr: The CIDR block to validate.

    Returns:
        True if valid, False otherwise.
    """
    return re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}/[0-9]{1,2}$', civc_cidr) is not None

def is_valid_security_group_id(ivsgisg_id: str) -> bool:
    """Check if the input is a valid security group ID format.

    Args:
        ivsgisg_id: The security group ID to validate.

    Returns:
        True if valid, False otherwise.
    """
    return re.match(r'^sg-[0-9a-f]{8,17}$', ivsgisg_id) is not None

def prompt_with_retries(pwr_prompt: str, pwr_max_retries: int = 3) -> str:
    """Prompt the user with a message and allow a maximum number of retries.

    Args:
        pwr_prompt: The message to display to the user.
        pwr_max_retries: The maximum number of attempts.

    Returns:
        The user input or 'no' if maximum retries reached.
    """
    pwr_retries = 0
    while pwr_retries < pwr_max_retries:
        pwr_response = input(pwr_prompt)
        if pwr_response:
            return pwr_response
        else:
            pwr_retries += 1
            print(f"No input provided. You have {pwr_max_retries - pwr_retries} retry(s) left.")
    return "no"  # Return 'no' if maximum retries reached

def create_rule(client: boto3.client, cr_group_id: str, cr_protocol: str, cr_port: int,
                cr_current_rule_count: int, cr_rule_type: str) -> Union[List[Dict[str, Any]], str]:
    """Create a rule (ingress or egress) for a security group.

    Args:
        client: The Boto3 EC2 client.
        cr_group_id: The ID of the security group.
        cr_protocol: The protocol (tcp or udp).
        cr_port: The port number.
        cr_current_rule_count: The current number of rules in the group.
        cr_rule_type: The type of rule ('ingress' or 'egress').

    Returns:
        The details of the created rules or an error message.
    """
    try:
        cr_ip_permissions = []
        cr_sources = []

        # Inform user about the limit
        cr_max_rules = 60
        if cr_current_rule_count >= cr_max_rules:
            return f"Maximum number of {cr_rule_type} rules reached. No more rules can be added."

        print("You can specify multiple CIDR blocks, but each rule can only accept one CIDR block or one Security Group ID.")

        while True:
            cr_source_input = prompt_with_retries('Enter CIDR block or Security Group ID (leave blank to finish): ')
            if cr_source_input == "no":
                print("Maximum retries reached. Exiting the script.")
                exit()  # Exit if maximum retries reached

            if cr_is_valid_cidr(cr_source_input):
                cr_sources.append(cr_source_input)
            elif is_valid_security_group_id(cr_source_input):
                cr_sources.append({'GroupId': cr_source_input})
            else:
                print("Invalid input. Please enter a valid CIDR block or Security Group ID.")

            if len(cr_sources) > 0:  # If at least one source has been added, break the loop
                break

        # Create permissions based on the sources
        for cr_source in cr_sources:
            if isinstance(cr_source, str):  # CIDR block
                cr_ip_permissions.append({
                    'IpProtocol': cr_protocol,
                    'FromPort': cr_port,
                    'ToPort': cr_port,
                    'IpRanges': [{'CidrIp': cr_source}],
                })
            elif isinstance(cr_source, dict) and 'GroupId' in cr_source:  # Security group reference
                cr_ip_permissions.append({
                    'IpProtocol': cr_protocol,
                    'FromPort': cr_port,
                    'ToPort': cr_port,
                    'UserIdGroupPairs': [{'GroupId': cr_source['GroupId']}],
                })

        if cr_rule_type == 'ingress':
            cr_response = client.authorize_security_group_ingress(
                GroupId=cr_group_id,
                IpPermissions=cr_ip_permissions
            )
        else:  # egress
            cr_response = client.authorize_security_group_egress(
                GroupId=cr_group_id,
                IpPermissions=cr_ip_permissions
            )

        # Extracting details from the response
        cr_rule_details = []
        for cr_rule in cr_response['SecurityGroupRules']:
            cr_rule_details.append({
                'GroupId': cr_rule['GroupId'],
                'SecurityGroupRuleId': cr_rule['SecurityGroupRuleId'],
                'IpProtocol': cr_rule['IpProtocol'],
                'FromPort': cr_rule['FromPort'],
                'ToPort': cr_rule['ToPort'],
                'CidrIpv4': cr_rule.get('IpRanges', [{}])[0].get('CidrIp', 'N/A')
            })

        return cr_rule_details
    except ClientError as e:
        return f"An error occurred while adding {cr_rule_type} rule: {e}"

def print_rule_details(prd_rules: Union[List[Dict[str, Any]], str]) -> None:
    """Print the details of the ingress or egress rules.

    Args:
        prd_rules: The rules to print or an error message.
    """
    if isinstance(prd_rules, str):
        print(prd_rules)  # Print error message
    elif isinstance(prd_rules, list):
        for prd_rule in prd_rules:
            if isinstance(prd_rule, dict):  # Ensure each rule is a dictionary
                print(f"GroupId: {prd_rule.get('GroupId', 'N/A')}")
                print(f"SecurityGroupRuleId: {prd_rule.get('SecurityGroupRuleId', 'N/A')}")
                print(f"IpProtocol: {prd_rule.get('IpProtocol', 'N/A')}")
                print(f"FromPort: {prd_rule.get('FromPort', 'N/A')}")
                print(f"ToPort: {prd_rule.get('ToPort', 'N/A')}")
                print(f"CidrIpv4: {prd_rule.get('CidrIpv4', 'N/A')}")
                print()  # Print a new line for better readability
            else:
                print("Unexpected rule format. Expected a dictionary.")
    else:
        print("Unexpected input type. Expected a list or a string.")

def prompt_protocol() -> Optional[str]:
    """Prompt for a valid protocol (tcp or udp).

    Returns:
        The protocol if valid, None if maximum retries reached.
    """
    while True:
        pp_protocol = prompt_with_retries('Enter the protocol (tcp or udp): ')
        if pp_protocol == 'no':  # Check if maximum retries reached
            return None  # Indicate failure to the caller
        if pp_protocol in ['tcp', 'udp']:
            return pp_protocol
        else:
            print("Invalid protocol. Please enter 'tcp' or 'udp'.")

def prompt_port() -> Optional[int]:
    """Prompt for a valid port number.

    Returns:
        The port number if valid, None if maximum retries reached.
    """
    while True:
        pp_port = prompt_with_retries('Enter the port number (0-65535): ')
        if pp_port == 'no':  # Check if maximum retries reached
            return None  # Indicate failure to the caller
        try:
            pp_port = int(pp_port)  # Attempt to convert to integer
            if 0 <= pp_port <= 65535:
                return pp_port  # Valid port number
            else:
                print("Port number must be between 0 and 65535.")
        except ValueError:
            print("Please enter a valid integer for the port number.")

if __name__ == '__main__':
    # Prompt user input for security group
    group_name = prompt_with_retries('Enter Security Group Name: ')
    if group_name == 'no':
        exit()  # Exit if maximum retries reached

    group_description = prompt_with_retries('Enter Security Group Description: ')
    if group_description == 'no':
        exit()  # Exit if maximum retries reached

    vpc_id = prompt_with_retries('Enter Security Group VPC ID: ')
    if vpc_id == 'no':
        exit()  # Exit if maximum retries reached

    tag_value = prompt_with_retries('Enter Security Group Tag Name Value: ')
    if tag_value == 'no':
        exit()  # Exit if maximum retries reached

    # Check if the security group already exists
    if security_group_exists(ec2, group_name, vpc_id):
        print(f"Security group '{group_name}' already exists in VPC '{vpc_id}'.")
    else:
        # Create the security group
        response = create_security_group(ec2, group_name, group_description, vpc_id)
        if isinstance(response, str):
            print(response)  # Print error message
        else:
            # Tag the security group
            tagged_value = tag_security_group(ec2, response['GroupId'], tag_value)
            print(tagged_value)

            print(f"Security Group Created:\n    GroupId: {response['GroupId']}")

            # Initialize rule counters
            ingress_rule_count = 0

            # Prompt to create ingress rules
            while True:
                create_ingress = prompt_with_retries("Do you want to create an ingress rule? (yes/no): ")
                if create_ingress == 'no':
                    break  # Exit the loop if the user doesn't want to create ingress rules
                elif create_ingress == 'yes':
                    protocol = prompt_protocol()
                    if protocol is None:  # Check if the user has exhausted retries
                        print("Maximum retries reached for protocol input. Exiting the script.")
                        exit()  # Exit if maximum retries reached

                    port = prompt_port()
                    if port is None:  # Check if the user has exhausted retries
                        print("Maximum retries reached for port input. Exiting the script.")
                        exit()  # Exit if maximum retries reached

                    ingress_response = create_rule(ec2, response['GroupId'], protocol, port, ingress_rule_count,
                                                   'ingress')
                    print_rule_details(ingress_response)  # Print the result

                    if isinstance(ingress_response, list):
                        ingress_rule_count += len(ingress_response)  # Increment the count of ingress rules added
                        print(f"Total ingress rules now: {ingress_rule_count}")

                    another_ingress = prompt_with_retries("Do you want to create another ingress rule? (yes/no): ")
                    if another_ingress != 'yes':
                        break  # Exit the loop if the user doesn't want to create another rule

            # After exiting the ingress loop, prompt for egress rules
            create_egress = prompt_with_retries("Do you want to create an egress rule? (yes/no): ")
            if create_egress == 'no':
                exit()  # Exit if maximum retries reached or user chooses not to create egress rules
            elif create_egress == 'yes':
                egress_rule_count = 0
                while True:
                    protocol = prompt_protocol()
                    if protocol is None:  # Check if the user has exhausted retries
                        print("Maximum retries reached for protocol input. Exiting the script.")
                        exit()  # Exit if maximum retries reached
                    port = prompt_port()
                    if port is None:  # Check if the user has exhausted retries
                        print("Maximum retries reached for port input. Exiting the script.")
                        exit()  # Exit if maximum retries reached
                    egress_response = create_rule(ec2, response['GroupId'], protocol, port, egress_rule_count, 'egress')
                    print_rule_details(egress_response)  # Print the result
                    if isinstance(egress_response, list):
                        egress_rule_count += len(egress_response)  # Increment the count of egress rules added
                        print(f"Total egress rules now: {egress_rule_count}")

                    another_egress = prompt_with_retries("Do you want to create another egress rule? (yes/no): ")
                    if another_egress != 'yes':
                        break  # Exit the loop if the user doesn't want to create another rule
