import boto3
from botocore.exceptions import ClientError
from typing import List

# Initialize EC2 client
ec2 = boto3.client('ec2')

def list_instance_types(client: boto3.client) -> List[str]:
    """
    Retrieve and list details of EC2 instance types.

    Args:
        client (boto3.client): The EC2 client to interact with the AWS EC2 service.

    Returns:
        List[str]: A list of strings containing details of each instance type.
    """
    instance_types_details = []  # List to store instance type details
    next_token = None  # Initialize NextToken for pagination

    while True:
        try:
            # Describe EC2 instance types with pagination
            response = client.describe_instance_types(NextToken=next_token) if next_token else client.describe_instance_types()

            # Iterate through the instance types in the response
            for instance_type in response.get('InstanceTypes', []):
                try:
                    # Construct instance type information
                    instance_type_info = (
                        f"Instance Type: {instance_type.get('InstanceType', 'N/A')}\n"
                        f"    CurrentGeneration: {instance_type.get('CurrentGeneration', 'N/A')}\n"
                        f"    FreeTierEligible: {instance_type.get('FreeTierEligible', 'N/A')}\n"
                        f"    SupportedUsageClasses: {instance_type.get('SupportedUsageClasses', 'N/A')}\n"
                        f"    SupportedRootDeviceTypes: {instance_type.get('SupportedRootDeviceTypes', 'N/A')}\n"
                        f"    SupportedVirtualizationTypes: {instance_type.get('SupportedVirtualizationTypes', 'N/A')}\n"
                        f"    BareMetal: {instance_type.get('BareMetal', 'N/A')}\n"
                        f"    Hypervisor: {instance_type.get('Hypervisor', 'N/A')}\n"
                        f"    Processor Info:\n"
                        f"        SupportedArchitecture: {instance_type.get('ProcessorInfo', {}).get('SupportedArchitectures', 'N/A')}\n"
                        f"        SustainedClockSpeedInGhz: {instance_type.get('ProcessorInfo', {}).get('SustainedClockSpeedInGhz', 'N/A')}\n"
                        f"        SupportedFeatures: {instance_type.get('ProcessorInfo', {}).get('SupportedFeatures', 'N/A')}\n"
                        f"        Manufacturer: {instance_type.get('ProcessorInfo', {}).get('Manufacturer', 'N/A')}\n"
                        f"    VCpuInfo:\n"
                        f"        DefaultVCpus: {instance_type.get('VCpuInfo', {}).get('DefaultVCpus', 'N/A')}\n"
                        f"        DefaultCores: {instance_type.get('VCpuInfo', {}).get('DefaultCores', 'N/A')}\n"
                        f"        DefaultThreadsPerCore: {instance_type.get('VCpuInfo', {}).get('DefaultThreadsPerCore', 'N/A')}\n"
                        f"        ValidCores: {instance_type.get('VCpuInfo', {}).get('ValidCores', 'N/A')}\n"
                        f"        ValidThreadsPerCore: {instance_type.get('VCpuInfo', {}).get('ValidThreadsPerCore', 'N/A')}\n"
                        f"    MemoryInfo:\n"
                        f"        SizeInMiB: {instance_type.get('MemoryInfo', {}).get('SizeInMiB', 'N/A')}\n"
                        f"    InstanceStorageSupported: {instance_type.get('InstanceStorageSupported', 'N/A')}\n"
                        f"    InstanceStorageInfo:\n"
                        f"        TotalSizeInGB: {instance_type.get('InstanceStorageInfo', {}).get('TotalSizeInGB', 'N/A')}\n"
                        f"        Disks: {instance_type.get('InstanceStorageInfo', {}).get('Disks', 'N/A')}\n"
                        f"        NvmeSupport: {instance_type.get('InstanceStorageInfo', {}).get('NvmeSupport', 'N/A')}\n"
                        f"        EncryptionSupport: {instance_type.get('InstanceStorageInfo', {}).get('EncryptionSupport', 'N/A')}\n"
                        f"    EbsInfo:\n"
                        f"        EbsOptimizedSupport: {instance_type.get('EbsOptimizedSupport', 'N/A')}\n"
                        f"        EbsOptimizedInfo:\n"
                        f"            BaselineBandwidthInMbps: {instance_type.get('EbsOptimizedInfo', {}).get('BaselineBandwidthInMbps', 'N/A')}\n"
                        f"            BaselineThroughputInMBps: {instance_type.get('EbsOptimizedInfo', {}).get('BaselineThroughputInMBps', 'N/A')}\n"
                        f"            BaselineIops: {instance_type.get('EbsOptimizedInfo', {}).get('BaselineIops', 'N/A')}\n"
                        f"            MaximumBandwidthInMbps: {instance_type.get('EbsOptimizedInfo', {}).get('MaximumBandwidthInMbps', 'N/A')}\n"
                        f"            MaximumThroughputInMBps: {instance_type.get('EbsOptimizedInfo', {}).get('MaximumThroughputInMBps', 'N/A')}\n"
                        f"            MaximumIops: {instance_type.get('EbsOptimizedInfo', {}).get('MaximumIops', 'N/A')}\n"
                        f"            NvmeSupport: {instance_type.get('EbsOptimizedInfo', {}).get('NvmeSupport', 'N/A')}\n"
                        f"    NetworkInfo:\n"
                        f"        NetworkPerformance: {instance_type.get('NetworkInfo', {}).get('NetworkPerformance', 'N/A')}\n"
                        f"        MaximumNetworkInterfaces: {instance_type.get('NetworkInfo', {}).get('MaximumNetworkInterfaces', 'N/A')}\n"
                        f"        MaximumNetworkCards: {instance_type.get('NetworkInfo', {}).get('MaximumNetworkCards', 'N/A')}\n"
                        f"        DefaultNetworkCardIndex: {instance_type.get('NetworkInfo', {}).get('DefaultNetworkCardIndex', 'N/A')}\n"
                        f"        NetworkCards:\n"
                        f"            NetworkCardIndex: {instance_type.get('NetworkCards', {}).get('NetworkCardIndex', 'N/A')}\n"
                        f"            NetworkPerformance: {instance_type.get('NetworkCards', {}).get('NetworkPerformance', 'N/A')}\n"
                        f"            MaximumNetworkInterfaces: {instance_type.get('NetworkCards', {}).get('MaximumNetworkInterfaces', 'N/A')}\n"
                        f"            BaselineBandwidthInGbps: {instance_type.get('NetworkCards', {}).get('BaselineBandwidthInGbps', 'N/A')}\n"
                        f"            PeakBandwidthInGbps: {instance_type.get('NetworkCards', {}).get('PeakBandwidthInGbps', 'N/A')}\n"
                        f"            DefaultEnaQueueCountPerInterface: {instance_type.get('NetworkCards', {}).get('DefaultEnaQueueCountPerInterface', 'N/A')}\n"
                        f"            MaximumEnaQueueCount: {instance_type.get('NetworkCards', {}).get('MaximumEnaQueueCount', 'N/A')}\n"
                        f"            MaximumEnaQueueCountPerInterface: {instance_type.get('NetworkCards', {}).get('MaximumEnaQueueCountPerInterface', 'N/A')}\n"
                        f"        Ipv4AddressesPerInterface: {instance_type.get('NetworkCards', {}).get('Ipv4AddressesPerInterface', 'N/A')}\n"
                        f"        Ipv6AddressesPerInterface: {instance_type.get('NetworkCards', {}).get('Ipv6AddressesPerInterface', 'N/A')}\n"
                        f"        Ipv6Supported: {instance_type.get('NetworkInfo', {}).get('Ipv6Supported', 'N/A')}\n"
                        f"        EnaSupport: {instance_type.get('NetworkInfo', {}).get('EnaSupport', 'N/A')}\n"
                        f"        EfaSupported: {instance_type.get('NetworkInfo', {}).get('EfaSupport', 'N/A')}\n"
                        f"        EfaInfo:\n"
                        f"            MaximumEfaInterfaces: {instance_type.get('EfaInfo', {}).get('MaximumEfaInterfaces', 'N/A')}\n"
                        f"        EncryptionInTransitSupported: {instance_type.get('NetworkInfo', {}).get('EncryptionInTransitSupport', 'N/A')}\n"
                        f"        EnaSrdSupported: {instance_type.get('NetworkInfo', {}).get('EnaSrdSupport', 'N/A')}\n"
                        f"        BandwidthWeightings: {instance_type.get('NetworkInfo', {}).get('BandwidthWeightings', 'N/A')}\n"
                        f"        FlexibleEnaQueuesSupport: {instance_type.get('NetworkInfo', {}).get('FlexibleEnaQueuesSupport', 'N/A')}"
                    )
                    instance_types_details.append(instance_type_info)  # Append the instance type info to the list
                except Exception as e:
                    print(f"Error processing instance type data: {e}")  # Print error for individual instance type processing

            # Check if there's a NextToken for pagination
            next_token = response.get('NextToken')
            if not next_token:
                break  # Exit the loop if there's no more data

        except ClientError as e:
            print(f"ClientError retrieving EC2 instance types: {e.response['Error']['Message']}")  # Print AWS error message
            break  # Exit the loop on error
        except Exception as e:
            print(f"Error retrieving EC2 instance types: {e}")  # Print error for EC2 instance types retrieval
            break  # Exit the loop on error

    return instance_types_details  # Return the list of instance types

if __name__ == "__main__":
    instance_types = list_instance_types(ec2)  # Call the function to list instance types
    for instance_detail in instance_types:
        print(instance_detail)  # Print each instance type's details
