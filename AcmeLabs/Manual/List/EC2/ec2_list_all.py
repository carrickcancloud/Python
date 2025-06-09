import boto3
from botocore.exceptions import ClientError
from typing import List, Optional

# Initialize the EC2 client
ec2 = boto3.client('ec2')

def list_ec2_instances(client: boto3.client) -> List[str]:
    """
    List EC2 instances with specific details.

    Args:
        client: The EC2 client to use for API calls.

    Returns:
        A list of strings containing details about each EC2 instance.

    Raises:
        ClientError: If the API call fails.
    """
    instance_details: List[str] = []  # List to store instance details as strings
    next_token: Optional[str] = None  # Initialize next_token for pagination

    while True:
        try:
            # Describe EC2 instances with pagination
            response = client.describe_instances(NextToken=next_token) if next_token else client.describe_instances()
        except ClientError as e:
            print(f"Failed to describe instances: {e}")  # Log the error message
            return []  # Return an empty list on error

        # Iterate through the reservations and instances in the response
        for reservation in response.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                try:
                    instance_info = (
                        f"Instance in {instance.get('Tags', [{}])[1].get('Value', 'N/A')} found:\n"
                        f"      Name: {instance.get('Tags', [{}])[0].get('Value', 'N/A')}\n"
                        f"      InstanceId: {instance.get('InstanceId', 'N/A')}\n"
                        f"      State: {instance.get('State', {}).get('Name', 'N/A')}\n"
                        f"      LaunchTime: {instance.get('LaunchTime', 'N/A')}\n"
                        f"          TimeZone: {instance.get('LaunchTime', {}).tzinfo if instance.get('LaunchTime') else 'N/A'}\n"
                        f"          ClientTimeZone: {instance.get('LaunchTime', {}).astimezone().tzinfo if instance.get('LaunchTime') else 'N/A'}\n"
                        f"  HardwareDetails:\n"
                        f"      Architecture: {instance.get('Architecture', 'N/A')}\n"
                        f"      InstanceType: {instance.get('InstanceType', 'N/A')}\n"
                        f"      AMI: {instance.get('ImageId', 'N/A')}\n"
                        f"      HDD Info:\n"
                        f"          RootDeviceType: {instance.get('RootDeviceType', 'N/A')}\n"
                        f"          RootDeviceName: {instance.get('RootDeviceName', 'N/A')}\n"
                        f"          BlockDeviceMappings:\n"
                        f"              DeviceName: {instance.get('BlockDeviceMappings', [{}])[0].get('DeviceName', 'N/A')}\n"
                        f"              Ebs:\n"
                        f"                  VolumeId: {instance.get('BlockDeviceMappings', [{}])[0].get('Ebs', {}).get('VolumeId', 'N/A')}\n"
                        f"                  Status: {instance.get('BlockDeviceMappings', [{}])[0].get('Ebs', {}).get('Status', 'N/A')}\n"
                        f"                  DeleteOnTermination: {instance.get('BlockDeviceMappings', [{}])[0].get('Ebs', {}).get('DeleteOnTermination', 'N/A')}\n"
                        f"      CPU Info:\n"
                        f"              CoreCount: {instance.get('CpuOptions', {}).get('CoreCount', 'N/A')}\n"
                        f"              ThreadsPerCore: {instance.get('CpuOptions', {}).get('ThreadsPerCore', 'N/A')}\n"
                        f"  VirtualizationDetails:\n"
                        f"      VirtualizationType: {instance.get('VirtualizationType', 'N/A')}\n"
                        f"      Hypervisor: {instance.get('Hypervisor', 'N/A')}\n"
                        f"      PlatformDetails: {instance.get('PlatformDetails', 'N/A')}\n"
                        f"      BootMode: {instance.get('BootMode', 'N/A')}\n"
                        f"  SecurityDetails:\n"
                        f"      SecurityGroups: {instance.get('SecurityGroups', [{}])[0].get('GroupName', 'N/A')}\n"
                        f"      KeyName: {instance.get('KeyName', 'N/A')}\n"
                        f"  NetworkDetails:\n"
                        f"      VPCId: {instance.get('VpcId', 'N/A')}\n"
                        f"      SubnetId: {instance.get('SubnetId', 'N/A')}\n"
                        f"      AvailabilityZone: {instance.get('Placement', {}).get('AvailabilityZone', 'N/A')}\n"
                        f"      PrivateIpAddress: {instance.get('PrivateIpAddress', 'N/A')}\n"
                        f"      PublicIpAddress: {instance.get('PublicIpAddress', 'N/A')}\n"
                        f"      InterfaceDetails:\n"
                        f"          InterfaceId: {instance.get('NetworkInterfaces', [{}])[0].get('NetworkInterfaceId', 'N/A')}\n"
                        f"          InterfaceType: {instance.get('NetworkInterfaces', [{}])[0].get('InterfaceType', 'N/A')}\n"
                        f"          MacAddress: {instance.get('NetworkInterfaces', [{}])[0].get('MacAddress', 'N/A')}\n"
                        f"          Status: {instance.get('NetworkInterfaces', [{}])[0].get('Status', 'N/A')}\n"
                        f"          Attachment:\n"
                        f"              AttachmentId: {instance.get('NetworkInterfaces', [{}])[0].get('Attachment', {}).get('AttachmentId', 'N/A')}\n"
                        f"              DeviceIndex: {instance.get('NetworkInterfaces', [{}])[0].get('Attachment', {}).get('DeviceIndex', 'N/A')}\n"
                        f"              Status: {instance.get('NetworkInterfaces', [{}])[0].get('Attachment', {}).get('Status', 'N/A')}\n"
                        f"              DeleteOnTermination: {instance.get('NetworkInterfaces', [{}])[0].get('Attachment', {}).get('DeleteOnTermination', 'N/A')}"
                    )
                    instance_details.append(instance_info)  # Add instance info to the list
                except KeyError as e:
                    print(f"Missing data for instance {instance.get('InstanceId', 'unknown')}: {e}")  # Log specific EC2 Instance processing errors

        # Check if there is a next token for pagination
        next_token = response.get('NextToken')
        if not next_token:
            break  # Exit the loop if there are no more pages

    return instance_details  # Return the list of instance details

if __name__ == "__main__":
    instances = list_ec2_instances(ec2)
    if instances:  # Check if instances were retrieved successfully
        for instance_detail in instances:
            print(instance_detail)  # Print each instance detail
    else:
        print("No instances found or an error occurred.")  # Message for no instances found
