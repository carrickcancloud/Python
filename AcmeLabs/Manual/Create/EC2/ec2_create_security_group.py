import boto3
from botocore.exceptions import ClientError
from typing import Union, Dict, Any, List, Optional
import re

# Initialize the EC2 client
ec2 = boto3.client('ec2')

def security_group_exists(client: boto3.client, sge_group_name: str, sge_vpc_id: str) -> bool:
    """Check if a security group exists in the specified VPC."""
    try:
        sge_response = client.describe_security_groups(
            Filters=[
                {'Name': 'group-name', 'Values': [sge_group_name]},
                {'Name': 'vpc-id', 'Values': [sge_vpc_id]}
            ]
        )
        return len(sge_response['SecurityGroups']) > 0  # Returns True if at least one security group is found
    except ClientError as e:
        print(f"An error occurred while checking for security group existence: {e}")
        return False

def create_security_group(client: boto3.client, csg_group_name: str, csg_description: str, csg_vpc_id: str) -> Union[
    Dict[str, Any], str]:
    """Create a security group in the specified VPC."""
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
    """Tag a security group with a specified name."""
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

def is_valid_cidr(ivc_cidr: str) -> bool:
    """Check if the input is a valid CIDR block."""
    return re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}/[0-9]{1,2}$', ivc_cidr) is not None

def is_valid_security_group_id(ivsgi_sg_id: str) -> bool:
    """Check if the input is a valid security group ID format."""
    return re.match(r'^sg-[0-9a-f]{8,17}$', ivsgi_sg_id) is not None  # Example format check

def prompt_with_retries(pwr_prompt: str, pwr_max_retries: int = 3) -> str:
    """Prompt the user with a message and allow a maximum number of retries."""
    pwr_retries = 0
    while pwr_retries < pwr_max_retries:
        pwr_response = input(pwr_prompt)
        if pwr_response:
            return pwr_response
        else:
            pwr_retries += 1
            print(f"No input provided. You have {pwr_max_retries - pwr_retries} retry(s) left.")
    return "no"  # Return 'no' if maximum retries reached

def create_ingress_rule(client: boto3.client, cir_group_id: str, cir_protocol: str, cir_port: int,
                        cir_current_rule_count: int) -> Union[List[Dict[str, Any]], str]:
    """Create an ingress rule for a security group."""
    try:
        cir_ip_permissions = []
        cir_sources = []

        # Inform user about the limit
        cir_max_rules = 60
        if cir_current_rule_count >= cir_max_rules:
            return "Maximum number of ingress rules reached. No more rules can be added."

        print("You can specify multiple CIDR blocks, but each rule can only accept one CIDR block or one Security Group ID.")

        while True:
            cir_source_input = prompt_with_retries('Enter CIDR block or Security Group ID (leave blank to finish): ')
            if cir_source_input == "no":
                print("Maximum retries reached. Exiting the script.")
                exit()  # Exit if maximum retries reached

            if is_valid_cidr(cir_source_input):
                cir_sources.append(cir_source_input)
            elif is_valid_security_group_id(cir_source_input):
                cir_sources.append({'GroupId': cir_source_input})
            else:
                print("Invalid input. Please enter a valid CIDR block or Security Group ID.")

            if len(cir_sources) > 0:  # If at least one source has been added, break the loop
                break

        # Create permissions based on the sources
        for cir_source in cir_sources:
            if isinstance(cir_source, str):  # CIDR block
                cir_ip_permissions.append({
                    'IpProtocol': cir_protocol,
                    'FromPort': cir_port,
                    'ToPort': cir_port,
                    'IpRanges': [{'CidrIp': cir_source}],
                })
            elif isinstance(cir_source, dict) and 'GroupId' in cir_source:  # Security group reference
                cir_ip_permissions.append({
                    'IpProtocol': cir_protocol,
                    'FromPort': cir_port,
                    'ToPort': cir_port,
                    'UserIdGroupPairs': [{'GroupId': cir_source['GroupId']}],
                })

        cir_response = client.authorize_security_group_ingress(
            GroupId=cir_group_id,
            IpPermissions=cir_ip_permissions
        )

        # Extracting details from the response
        cir_ingress_details = []
        for cir_rule in cir_response['SecurityGroupRules']:
            cir_ingress_details.append({
                'GroupId': cir_rule['GroupId'],
                'SecurityGroupRuleId': cir_rule['SecurityGroupRuleId'],
                'IpProtocol': cir_rule['IpProtocol'],
                'FromPort': cir_rule['FromPort'],
                'ToPort': cir_rule['ToPort'],
                'CidrIpv4': cir_rule.get('IpRanges', [{}])[0].get('CidrIp', 'N/A')
            })

        return cir_ingress_details
    except ClientError as e:
        return f"An error occurred while adding ingress rule: {e}"

def create_egress_rule(client: boto3.client, cer_group_id: str, cer_protocol: str, cer_port: int,
                       cer_current_rule_count: int) -> Union[List[Dict[str, Any]], str]:
    """Create an egress rule for a security group."""
    try:
        cer_ip_permissions = []
        cer_sources = []

        # Inform user about the limit
        cer_max_rules = 60
        if cer_current_rule_count >= cer_max_rules:
            return "Maximum number of egress rules reached. No more rules can be added."

        print("You can specify multiple CIDR blocks, but each rule can only accept one CIDR block or one Security Group ID.")

        while True:
            cer_source_input = prompt_with_retries('Enter CIDR block or Security Group ID (leave blank to finish): ')
            if cer_source_input == "no":
                print("Maximum retries reached. Exiting the script.")
                exit()  # Exit if maximum retries reached

            if is_valid_cidr(cer_source_input):
                cer_sources.append(cer_source_input)
            elif is_valid_security_group_id(cer_source_input):
                cer_sources.append({'GroupId': cer_source_input})
            else:
                print("Invalid input. Please enter a valid CIDR block or Security Group ID.")

            if len(cer_sources) > 0:  # If at least one source has been added, break the loop
                break

        # Create permissions based on the sources
        for cer_source in cer_sources:
            if isinstance(cer_source, str):  # CIDR block
                cer_ip_permissions.append({
                    'IpProtocol': cer_protocol,
                    'FromPort': cer_port,
                    'ToPort': cer_port,
                    'IpRanges': [{'CidrIp': cer_source}],
                })
            elif isinstance(cer_source, dict) and 'GroupId' in cer_source:  # Security group reference
                cer_ip_permissions.append({
                    'IpProtocol': cer_protocol,
                    'FromPort': cer_port,
                    'ToPort': cer_port,
                    'UserIdGroupPairs': [{'GroupId': cer_source['GroupId']}],
                })

        cer_response = client.authorize_security_group_egress(
            GroupId=cer_group_id,
            IpPermissions=cer_ip_permissions
        )

        # Extracting details from the response
        cer_egress_details = []
        for cer_rule in cer_response['SecurityGroupRules']:
            cer_egress_details.append({
                'GroupId': cer_rule['GroupId'],
                'SecurityGroupRuleId': cer_rule['SecurityGroupRuleId'],
                'IpProtocol': cer_rule['IpProtocol'],
                'FromPort': cer_rule['FromPort'],
                'ToPort': cer_rule['ToPort'],
                'CidrIpv4': cer_rule.get('IpRanges', [{}])[0].get('CidrIp', 'N/A')
            })

        return cer_egress_details
    except ClientError as e:
        return f"An error occurred while adding egress rule: {e}"

def print_rule_details(prd_rules: Union[List[Dict[str, Any]], str]) -> None:
    """Print the details of the ingress or egress rules."""
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
    """Prompt for a valid protocol (tcp or udp)."""
    while True:
        pp_protocol = prompt_with_retries('Enter the protocol (tcp or udp): ')
        if pp_protocol == 'no':  # Check if maximum retries reached
            return None  # Indicate failure to the caller
        if pp_protocol in ['tcp', 'udp']:
            return pp_protocol
        else:
            print("Invalid protocol. Please enter 'tcp' or 'udp'.")

def prompt_port() -> Optional[int]:
    """Prompt for a valid port number."""
    while True:
        try:
            pp_port = int(prompt_with_retries('Enter the port number (0-65535): '))
            if 0 <= pp_port <= 65535:
                return pp_port
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
            egress_rule_count = 0

            # Loop to create ingress rules
            while True:
                create_ingress = prompt_with_retries("Do you want to create an ingress rule? (yes/no): ")
                if create_ingress == 'no':
                    break
                elif create_ingress == 'yes':
                    protocol = prompt_protocol()
                    if protocol is None:  # Check if the user has exhausted retries
                        print("Maximum retries reached for protocol input. Exiting the script.")
                        exit()  # Exit if maximum retries reached
                    port = prompt_port()
                    if port is None:  # Check if the user has exhausted retries
                        print("Maximum retries reached for port input. Exiting the script.")
                        exit()  # Exit if maximum retries reached
                    ingress_response = create_ingress_rule(ec2, response['GroupId'], protocol, port, ingress_rule_count)
                    if isinstance(ingress_response, str):
                        print(ingress_response)  # Print error message
                    else:
                        ingress_rule_count += len(ingress_response)  # Increment the count of ingress rules added
                        print(f"Total ingress rules now: {ingress_rule_count}")

                    another_ingress = prompt_with_retries("Do you want to create another ingress rule? (yes/no): ")
                    if another_ingress != 'yes':
                        break  # Exit the loop if the user doesn't want to create another rule

            # Loop to create egress rules
            while True:
                create_egress = prompt_with_retries("Do you want to create an egress rule? (yes/no): ")
                if create_egress == 'no':
                    break
                elif create_egress == 'yes':
                    protocol = prompt_protocol()
                    if protocol is None:  # Check if the user has exhausted retries
                        print("Maximum retries reached for protocol input. Exiting the script.")
                        exit()  # Exit if maximum retries reached
                    port = prompt_port()
                    if port is None:  # Check if the user has exhausted retries
                        print("Maximum retries reached for port input. Exiting the script.")
                        exit()  # Exit if maximum retries reached
                    egress_response = create_egress_rule(ec2, response['GroupId'], protocol, port, egress_rule_count)
                    if isinstance(egress_response, str):
                        print(egress_response)  # Print error message
                    else:
                        egress_rule_count += len(egress_response)  # Increment the count of egress rules added
                        print(f"Total egress rules now: {egress_rule_count}")

                    another_egress = prompt_with_retries("Do you want to create another egress rule? (yes/no): ")
                    if another_egress != 'yes':
                        break  # Exit the loop if the user doesn't want to create another rule
