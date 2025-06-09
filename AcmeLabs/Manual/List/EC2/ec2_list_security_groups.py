import boto3
from botocore.exceptions import ClientError
from typing import List, Any

# Initialize EC2 client
ec2 = boto3.client('ec2')

def list_security_groups(client: Any) -> List[str]:
    """
    List security groups and their details from AWS EC2.

    Args:
        client (Any): The Boto3 EC2 client.

    Returns:
        List[str]: A list of strings containing details of each security group.
    """
    security_group_details = []
    next_token = None

    while True:
        try:
            # Fetch security groups with pagination support
            response = client.describe_security_groups(NextToken=next_token) if next_token else client.describe_security_groups()

            for sg in response.get('SecurityGroups', []):
                try:
                    security_group_info = (
                        f"GroupName: {sg.get('GroupName', 'N/A')}\n"
                        f"GroupId: {sg.get('GroupId', 'N/A')}\n"
                        f"VpcId: {sg.get('VpcId', 'N/A')}\n"
                    )

                    has_ingress = False
                    has_egress = False

                    # Capture Ingress Rules
                    if sg.get('IpPermissions'):
                        for permission in sg.get('IpPermissions', []):
                            ip_protocol = permission.get('IpProtocol', 'N/A')
                            from_port = permission.get('FromPort', 'N/A')
                            to_port = permission.get('ToPort', 'N/A')
                            # Check if there are valid ingress rules
                            if ip_protocol != 'N/A' and from_port != 'N/A' and to_port != 'N/A':
                                has_ingress = True
                                if not security_group_info.endswith("IpPermissions (Ingress):\n"):
                                    security_group_info += "IpPermissions (Ingress):\n"
                                for ip_range in permission.get('IpRanges', []):
                                    cidr_block = ip_range.get('CidrIp', 'N/A')
                                    security_group_info += (
                                        f"    IpProtocol: {ip_protocol}\n"
                                        f"    FromPort: {from_port}\n"
                                        f"    ToPort: {to_port}\n"
                                        f"    CIDR Block: {cidr_block}\n"
                                    )

                    # Capture Egress Rules
                    if sg.get('IpPermissionsEgress'):
                        for permission in sg.get('IpPermissionsEgress', []):
                            ip_protocol = permission.get('IpProtocol', 'N/A')
                            from_port = permission.get('FromPort', 'N/A')
                            to_port = permission.get('ToPort', 'N/A')
                            # Check if there are valid egress rules
                            if ip_protocol != '-1' and from_port != 'N/A' and to_port != 'N/A':
                                has_egress = True
                                if not security_group_info.endswith("IpPermissionsEgress (Egress):\n"):
                                    security_group_info += "IpPermissionsEgress (Egress):\n"
                                for ip_range in permission.get('IpRanges', []):
                                    cidr_block = ip_range.get('CidrIp', 'N/A')
                                    security_group_info += (
                                        f"    IpProtocol: {ip_protocol}\n"
                                        f"    FromPort: {from_port}\n"
                                        f"    ToPort: {to_port}\n"
                                        f"    CIDR Block: {cidr_block}\n"
                                    )

                    # Only append if there is any valid ingress or egress information
                    if has_ingress or has_egress:
                        security_group_details.append(security_group_info)

                except KeyError as e:
                    print(f"Error processing Security Group data: {e}")

            next_token = response.get('NextToken')
            if not next_token:
                break

        except ClientError as e:
            print(f"Client error while retrieving security group data: {e}")
            return []  # Return an empty list on error
        except Exception as e:
            print(f"Unexpected error while retrieving security group data: {e}")
            return []  # Return an empty list on unexpected error

    return security_group_details

if __name__ == '__main__':
    security_groups = list_security_groups(ec2)
    for security_group in security_groups:
        print(security_group)
