import boto3
from typing import List, Dict, Any

# Initialize the EC2 client
ec2 = boto3.client('ec2')

def list_ec2_instances(client: Any) -> List[str]:
    """
    List EC2 instances with specific details.

    Args:
        client: The EC2 client to use for API calls.

    Returns:
        A list of strings containing details about each EC2 instance.

    Raises:
        Exception: If the API call fails or if the response format is unexpected.
    """
    try:
        # Describe EC2 instances with a filter for architecture
        response = client.describe_instances() # No filter applied, retrieves all instances
    except Exception as e:
        print(f"Error retrieving EC2 instances: {e}")
        return []  # Return an empty list on error

    instance_details = []  # List to store instance details as strings

    # Iterate through the reservations and instances in the response
    for reservation in response.get('Reservations', []):
        for instance in reservation.get('Instances', []):
            try:
                instance_info = (
                    f"Instance in {instance['Tags'][1]['Value']} found:\n"
                    f"      Name: {instance['Tags'][0]['Value']}\n"
                    f"      InstanceId: {instance['InstanceId']}\n"
                    f"      State: {instance['State']['Name']}\n"
                    f"      LaunchTime: {instance['LaunchTime'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"          TimeZone: {instance['LaunchTime'].tzinfo}\n"
                    f"          ClientTimeZone: {instance['LaunchTime'].astimezone().tzinfo}\n"
                    f"  HardwareDetails:\n"
                    f"      Architecture: {instance['Architecture']}\n"
                    f"      InstanceType: {instance['InstanceType']}\n"
                    f"      AMI: {instance['ImageId']}\n"
                    f"      HDD Info:\n"
                    f"          RootDeviceType: {instance['RootDeviceType']}\n"
                    f"          RootDeviceName: {instance['RootDeviceName']}\n"
                    f"          BlockDeviceMappings:\n"
                    f"              DeviceName: {instance['BlockDeviceMappings'][0]['DeviceName']}\n"
                    f"              Ebs:\n"
                    f"                  VolumeId: {instance['BlockDeviceMappings'][0]['Ebs']['VolumeId']}\n"
                    f"                  Status: {instance['BlockDeviceMappings'][0]['Ebs']['Status']}\n"
                    f"                  DeleteOnTermination: {instance['BlockDeviceMappings'][0]['Ebs']['DeleteOnTermination']}\n"
                    f"      CPU Info:\n"
                    f"              CoreCount: {instance['CpuOptions']['CoreCount']}\n"
                    f"              ThreadsPerCore: {instance['CpuOptions']['ThreadsPerCore']}\n"
                    f"  VirtualizationDetails:\n"
                    f"      VirtualizationType: {instance['VirtualizationType']}\n"
                    f"      Hypervisor: {instance['Hypervisor']}\n"
                    f"      PlatformDetails: {instance['PlatformDetails']}\n"
                    f"      BootMode: {instance.get('BootMode', 'N/A')}\n"
                    f"  SecurityDetails:\n"
                    f"      SecurityGroups: {instance['SecurityGroups'][0]['GroupName']}\n"
                    f"      KeyName: {instance['KeyName']}\n"
                    f"  NetworkDetails:\n"
                    f"      VPCId: {instance['VpcId']}\n"
                    f"      SubnetId: {instance['SubnetId']}\n"
                    f"      AvailabilityZone: {instance['Placement']['AvailabilityZone']}\n"
                    f"      PrivateIpAddress: {instance['PrivateIpAddress']}\n"
                    f"      PublicIpAddress: {instance.get('PublicIpAddress', 'N/A')}\n"
                    f"      InterfaceDetails:\n"
                    f"          InterfaceId: {instance['NetworkInterfaces'][0]['NetworkInterfaceId']}\n"
                    f"          InterfaceType: {instance['NetworkInterfaces'][0]['InterfaceType']}\n"
                    f"          MacAddress: {instance['NetworkInterfaces'][0]['MacAddress']}\n"
                    f"          Status: {instance['NetworkInterfaces'][0]['Status']}\n"
                    f"          Attachment:\n"
                    f"              AttachmentId: {instance['NetworkInterfaces'][0]['Attachment']['AttachmentId']}\n"
                    f"              DeviceIndex: {instance['NetworkInterfaces'][0]['Attachment']['DeviceIndex']}\n"
                    f"              Status: {instance['NetworkInterfaces'][0]['Attachment']['Status']}\n"
                    f"              DeleteOnTermination: {instance['NetworkInterfaces'][0]['Attachment']['DeleteOnTermination']}\n"
                )
                instance_details.append(instance_info)  # Add instance info to the list
            except KeyError as e:
                print(f"Missing data for instance {instance.get('InstanceId', 'unknown')}: {e}")

    return instance_details  # Return the list of instance details

if __name__ == "__main__":
    instances = list_ec2_instances(ec2)
    for instance_detail in instances:
        print(instance_detail)  # Print each instance detail
