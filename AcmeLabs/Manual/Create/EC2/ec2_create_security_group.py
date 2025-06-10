import boto3
from botocore.exceptions import ClientError
from typing import Union, Dict, Any, List
import re

# Initialize the EC2 client
ec2 = boto3.client('ec2')

def create_security_group(client: boto3.client, csg_group_name: str, csg_description: str, csg_vpc_id: str) -> Union[Dict[str, Any], str]:
    """
    Create a security group in the specified VPC.

    :param client: Boto3 EC2 client
    :param csg_group_name: Name of the security group
    :param csg_description: Description of the security group
    :param csg_vpc_id: VPC ID where the security group will be created
    :return: Response from the create_security_group API or an error message
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
    """
    Tag a security group with a specified name.

    :param client: Boto3 EC2 client
    :param tsg_group_id: ID of the security group to tag
    :param tsg_tag_value: Value for the 'Name' tag
    :return: Success or error message
    """
    try:
        csg_response = client.create_tags(
            Resources=[tsg_group_id],
            Tags=[{'Key': 'Name', 'Value': tsg_tag_value}]
        )
        if csg_response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return "Security group tagged successfully."
        else:
            return f"Failed to tag security group id: {tsg_group_id}"
    except ClientError as e:
        return f"An error occurred while tagging security group: {e}"

def create_ingress_rule(client: boto3.client, cir_group_id: str, cir_protocol: str, cir_port: int, cir_cidr_ip: str) -> Union[List[Dict[str, Any]], str]:
    """
    Create an ingress rule for a security group.

    :param client: Boto3 EC2 client
    :param cir_group_id: ID of the security group
    :param cir_protocol: Protocol for the ingress rule
    :param cir_port: Port number for the ingress rule
    :param cir_cidr_ip: CIDR IP range for the ingress rule
    :return: Response details or an error message
    """
    try:
        cir_response = client.authorize_security_group_ingress(
            GroupId=cir_group_id,
            IpPermissions=[{
                'IpProtocol': cir_protocol,
                'FromPort': cir_port,
                'ToPort': cir_port,
                'IpRanges': [{'CidrIp': cir_cidr_ip}],
            }]
        )

        # Extracting details from the response
        cir_ingress_details = []
        for rule in cir_response['SecurityGroupRules']:
            cir_ingress_details.append({
                'GroupId': rule['GroupId'],
                'SecurityGroupRuleId': rule['SecurityGroupRuleId'],
                'IpProtocol': rule['IpProtocol'],
                'FromPort': rule['FromPort'],
                'ToPort': rule['ToPort'],
                'CidrIpv4': rule.get('IpRanges', [{}])[0].get('CidrIp', 'N/A')
            })

        return cir_ingress_details
    except ClientError as e:
        return f"An error occurred while adding ingress rule: {e}"

def create_egress_rule(client: boto3.client, cer_group_id: str, cer_protocol: str, cer_port: int, cer_cidr_ip: str) -> Union[List[Dict[str, Any]], str]:
    """
    Create an egress rule for a security group.

    :param client: Boto3 EC2 client
    :param cer_group_id: ID of the security group
    :param cer_protocol: Protocol for the egress rule
    :param cer_port: Port number for the egress rule
    :param cer_cidr_ip: CIDR IP range for the egress rule
    :return: Response details (list of dictionaries) or an error message
    """
    try:
        cer_response = client.authorize_security_group_egress(
            GroupId=cer_group_id,
            IpPermissions=[{
                'IpProtocol': cer_protocol,
                'FromPort': cer_port,
                'ToPort': cer_port,
                'IpRanges': [{'CidrIp': cer_cidr_ip}],
            }]
        )

        # Extracting details from the response
        cer_egress_details = []
        for rule in cer_response['SecurityGroupRules']:
            cer_egress_details.append({
                'GroupId': rule['GroupId'],
                'SecurityGroupRuleId': rule['SecurityGroupRuleId'],
                'IpProtocol': rule['IpProtocol'],
                'FromPort': rule['FromPort'],
                'ToPort': rule['ToPort'],
                'CidrIpv4': rule.get('IpRanges', [{}])[0].get('CidrIp', 'N/A')
            })

        return cer_egress_details
    except ClientError as e:
        return f"An error occurred while adding egress rule: {e}"

def get_int_input(gii_prompt: str, gii_max_retries: int = 3) -> int:
    """
    Prompt the user for an integer input with retry logic.

    :param gii_prompt: Input prompt message
    :param gii_max_retries: Maximum number of retries for input
    :return: Validated integer input from the user
    """
    gii_retries = 0
    while gii_retries < gii_max_retries:
        gii_user_input = input(gii_prompt)
        try:
            return int(gii_user_input)
        except ValueError:
            gii_retries += 1
            print(f"Invalid input. Please enter an integer. You have {gii_max_retries - gii_retries} retries left.")
            if gii_retries == gii_max_retries:
                print("Maximum retries reached.")
    return -1  # Return a sentinel value if maximum retries are reached

def get_cidr_input(gci_prompt: str, gci_max_retries: int = 3) -> str:
    """
    Prompt the user for a valid CIDR notation input with retry logic.

    :param gci_prompt: Input prompt message
    :param gci_max_retries: Maximum number of retries for input
    :return: Validated CIDR input from the user
    """
    gci_cidr_regex = re.compile(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}/[0-9]{1,2}$')
    gci_retries = 0
    while gci_retries < gci_max_retries:
        gci_cidr_input = input(gci_prompt)
        if gci_cidr_regex.match(gci_cidr_input):
            return gci_cidr_input
        else:
            gci_retries += 1
            print(f"Invalid CIDR notation. Please enter a valid CIDR (e.g., 0.0.0.0/0). You have {gci_max_retries - gci_retries} retries left.")
            if gci_retries == gci_max_retries:
                print("Maximum retries reached.")
    return "0.0.0.0/0"  # Return a default value if maximum retries are reached

def get_protocol_input(gpi_prompt: str, gpi_max_retries: int = 3) -> str:
    """
    Prompt the user for a valid protocol (tcp or udp) with retry logic.

    :param gpi_prompt: Input prompt message
    :param gpi_max_retries: Maximum number of retries for input
    :return: Validated protocol input from the user
    """
    gpi_valid_protocols = {'tcp', 'udp'}
    gpi_retries = 0
    while gpi_retries < gpi_max_retries:
        gpi_protocol = input(gpi_prompt).strip().lower()
        if gpi_protocol in gpi_valid_protocols:
            return gpi_protocol
        else:
            gpi_retries += 1
            print(f"Invalid protocol. Please enter 'tcp' or 'udp'. You have {gpi_max_retries - gpi_retries} retries left.")
            if gpi_retries == gpi_max_retries:
                print("Maximum retries reached.")
    return 'tcp'  # Return a default value if maximum retries are reached

def security_group_exists(client: boto3.client, sge_group_name: str, sge_vpc_id: str) -> Union[bool, str]:
    """
    Check if a security group exists in the specified VPC.

    :param client: Boto3 EC2 client
    :param sge_group_name: Name of the security group
    :param sge_vpc_id: VPC ID to check
    :return: True if the security group exists, False otherwise, or an error message
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
        return f"An error occurred while checking security group existence: {e}"

def print_rule_details(prd_rules: Union[List[Dict[str, Any]], str]) -> None:
    """
    Print the details of the ingress or egress rules.

    :param prd_rules: List of rule details or error message
    """
    if isinstance(prd_rules, str):
        print(prd_rules)  # Print error message
    elif isinstance(prd_rules, list):
        for rule in prd_rules:
            if isinstance(rule, dict):  # Ensure each rule is a dictionary
                print(f"GroupId: {rule.get('GroupId', 'N/A')}")
                print(f"SecurityGroupRuleId: {rule.get('SecurityGroupRuleId', 'N/A')}")
                print(f"IpProtocol: {rule.get('IpProtocol', 'N/A')}")
                print(f"FromPort: {rule.get('FromPort', 'N/A')}")
                print(f"ToPort: {rule.get('ToPort', 'N/A')}")
                print(f"CidrIpv4: {rule.get('CidrIpv4', 'N/A')}")
                print()  # Print a new line for better readability
            else:
                print("Unexpected rule format. Expected a dictionary.")
    else:
        print("Unexpected input type. Expected a list or a string.")

def prompt_with_retries(pwr_prompt: str, pwr_max_retries: int = 3) -> str:
    """
    Prompt the user with a message and allow a maximum number of retries.

    :param pwr_prompt: Input prompt message
    :param pwr_max_retries: Maximum number of retries for input
    :return: Validated input from the user
    """
    pwr_retries = 0
    while pwr_retries < pwr_max_retries:
        pwr_response = input(pwr_prompt).strip().lower()
        if pwr_response:
            return pwr_response
        else:
            pwr_retries += 1
            print(f"No input provided. You have {pwr_max_retries - pwr_retries} retry(s) left.")
    return "no"  # Return 'no' if maximum retries reached

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

            # Loop to create ingress rules
            ingress_created = False
            while True:
                create_rule = prompt_with_retries('Do you want to create an ingress rule? (yes/no): ')
                if create_rule == 'no':
                    break

                protocol = get_protocol_input('Enter the protocol (tcp or udp): ')
                port = get_int_input('Enter the port number: ')
                cidr_ip = get_cidr_input('Enter the CIDR IP range (e.g., 0.0.0.0/0): ')

                ingress_response = create_ingress_rule(ec2, response['GroupId'], protocol, port, cidr_ip)
                print_rule_details(ingress_response)

                if isinstance(ingress_response, list) and ingress_response:
                    ingress_created = True

            if ingress_created:
                print("Ingress rule creation completed successfully.")
            else:
                print("No ingress rules were created.")

            # Loop to create egress rules
            egress_created = False
            while True:
                create_rule = prompt_with_retries('Do you want to create an egress rule? (yes/no): ')
                if create_rule == 'no':
                    break

                protocol = get_protocol_input('Enter the protocol (tcp or udp): ')
                port = get_int_input('Enter the port number: ')
                cidr_ip = get_cidr_input('Enter the CIDR IP range (e.g., 0.0.0.0/0): ')

                egress_response = create_egress_rule(ec2, response['GroupId'], protocol, port, cidr_ip)
                print_rule_details(egress_response)

                if isinstance(egress_response, list) and egress_response:
                    egress_created = True

            if egress_created:
                print("Egress rule creation completed successfully.")
            else:
                print("No egress rules were created.")
