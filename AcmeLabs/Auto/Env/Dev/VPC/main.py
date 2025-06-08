import boto3
from botocore.exceptions import ClientError
from helper import (
    vpc_exists, route_table_exists, internet_gateway_exists,
    get_vpc_id, get_route_table_id, get_internet_gateway_id, get_subnet_info,
    create_vpc, create_subnet, associate_route_table,
    create_internet_gateway, attach_internet_gateway, create_route,
    delete_route, detach_internet_gateway, delete_internet_gateway,
    disassociate_subnets_from_route_table, delete_route_table, delete_vpc
)
import json

# Load configuration from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Initialize the EC2 client
ec2 = boto3.client('ec2')

def create_vpc_operation() -> None:
    """Creates a VPC if it does not already exist."""
    # Check if the specified VPC exists
    vpc_exists_result, vpc_exists_error = vpc_exists(ec2, config["CIDR_BLOCK"], config["TAG_VPC_NAME"], config["TAG_ENV"])

    if vpc_exists_result:
        print(
            f"VPC Exits:\n"
            f"    Name: {config['TAG_VPC_NAME']}\n"
            f"    Environment: {config['TAG_ENV']}\n"
            f"    CIDR Block: {config['CIDR_BLOCK']}"
        )
    else:
        vpc_id, create_vpc_error = create_vpc(ec2, config["CIDR_BLOCK"], config["TAG_VPC_NAME"], config["TAG_ENV"])

        if create_vpc_error:
            print(f"Error: {create_vpc_error}")  # Handle error if VPC creation fails
        else:
            # Print details of the newly created VPC
            print(f"VPC Details:\n  VPC ID: {vpc_id}\n  Name: {config['TAG_VPC_NAME']}")

def create_subnet_operation() -> None:
    """Creates subnets based on the configuration."""
    for cidr, az, tag in zip(config["CIDR_PUBLIC_SUBNETS"], config["AVAILABILITY_ZONES"], config["TAG_SUBNETS"]):
        subnet_id, error = create_subnet(ec2, cidr, az, tag, config['TAG_ENV'])  # Create the subnet
        if error:
            print(f"{error}")  # Handle the error if occurred
        else:
            print(f"Created Subnet ID: {subnet_id}")  # Print the created subnet ID

def create_route_table_operation() -> None:
    """Creates a route table if it does not already exist."""
    vpc_id = get_vpc_id(ec2)  # Get the VPC ID

    if route_table_exists(ec2, config["TAG_RTB"], config["TAG_ENV"], vpc_id[0]):
        print(
            f"RouteTable Exits:\n"
            f"    Name: {config['TAG_RTB']}\n"
            f"    Environment: {config['TAG_ENV']}\n"
            f"    VPC: {vpc_id}")
    else:
        # Create a new route table if it does not exist
        rtb = ec2.create_route_table(
            TagSpecifications=[
                {
                    'ResourceType': 'route-table',  # Specify the resource type
                    'Tags': [
                        {
                            'Key': 'Name',  # Key for the Name tag
                            'Value': config['TAG_RTB']  # Value for the Name tag
                        },
                        {
                            'Key': 'Environment',  # Key for the Environment tag
                            'Value': config['TAG_ENV']  # Value for the Environment tag
                        }
                    ]
                }
            ],
            VpcId=vpc_id[0]  # ID of the VPC to create the route table in
        )
        # Print details of the created route table
        print(
            f"RouteTable Created:\n"
            f"    RouteTable ID: {rtb['RouteTable']['RouteTableId']}\n"
            f"    Name: {rtb['RouteTable']['Tags'][0]['Value']}")

def associate_subnets_operation() -> None:
    """Associates subnets with the route table."""
    try:
        rtb_id = get_route_table_id(ec2, config['TAG_RTB'])
        if "Error" in rtb_id:
            print(f"Error: {rtb_id}")
            return

        subnet_details, subnet_ids = get_subnet_info(ec2, config['TAG_SUBNET'])
        if isinstance(subnet_ids, str):  # Check if it's an error message
            print(f"Error: {subnet_ids}")
            return

        if not subnet_ids:
            print("Error: No subnets found with the specified tag.")
        else:
            # Print details of each found subnet
            for subnet_id in subnet_ids:
                details = subnet_details[subnet_id]
                print(f"Subnet Found:\n  Subnet ID: {subnet_id}\n  CIDR Block: {details['CIDR Block']}\n  Availability Zone: {details['Availability Zone']}\n  VPC ID: {details['VPC ID']}")

            print("Subnet IDs:", subnet_ids)

            # Associate the route table with the subnets
            response = associate_route_table(ec2, subnet_ids, rtb_id)

            # Print results of the association
            for subnet, result in response:
                if isinstance(result, dict):
                    print(f"Successfully associated RouteTable {rtb_id} with Subnet {subnet}.")
                else:
                    print(f"Error: Failed to associate RouteTable {rtb_id} with Subnet {subnet}. Error: {result}")
    except Exception as e:
        print(f"Error: An error occurred in the main execution: {str(e)}")

def create_internet_gateway_operation() -> None:
    """Creates an Internet Gateway if it does not already exist."""
    exists = internet_gateway_exists(ec2, config['TAG_IGW_NAME'], config['TAG_ENV'])

    if exists:
        print(f"Internet Gateway with name '{config['TAG_IGW_NAME']}' for environment '{config['TAG_ENV']}' already exists.")
        return  # Exit if the Internet Gateway already exists

    create_igw = create_internet_gateway(ec2)
    if 'Error' in create_igw:
        print(f"Error: {create_igw}")
    else:
        print(f"Internet Gateway created with ID: {create_igw}")

def attach_internet_gateway_operation() -> None:
    """Attaches the Internet Gateway to the VPC."""
    vpc_id, error = get_vpc_id(ec2)
    if error:
        print(f"Error: {error}")
        return

    igw_id, error = get_internet_gateway_id(ec2, config['TAG_IGW_NAME'])
    if error:
        print(f"Error: {error}")
        return

    success, response_or_error = attach_internet_gateway(ec2, vpc_id, igw_id)
    if not success:
        print(f"Error: {response_or_error}")  # Handle the error if attachment fails
    else:
        print(f"Internet Gateway successfully attached to VPC: {vpc_id}.")

def create_route_operation() -> None:
    """Creates a route in the Route Table to direct traffic to the Internet Gateway."""
    igw_id, error = get_internet_gateway_id(ec2, config['TAG_IGW_NAME'])
    if error:
        print(f"Error: {error}")
        return

    rtb_id = get_route_table_id(ec2, config['TAG_RTB'])
    if isinstance(rtb_id, str) and "No route table found" in rtb_id:
        print(f"Error: {rtb_id}")
        return

    route_result = create_route(ec2, config['DEST_CIDR_BLOCK'], igw_id, rtb_id)
    if isinstance(route_result, tuple) and route_result[1]:
        print(f"Error: {route_result[1]}")  # Print error if route creation fails
    else:
        print(f"Route created successfully in RouteTable ID: {route_result[0]}")

def delete_route_operation() -> None:
    """Handles the route deletion operation."""
    route_table_id = get_route_table_id(ec2, config["TAG_RTB"])
    if isinstance(route_table_id, str) and "No route table found" in route_table_id:
        print(f"Error: {route_table_id}")
    else:
        result = delete_route(ec2, route_table_id, config["DEST_CIDR_BLOCK"])
        print(result)

def delete_route_table_operation() -> None:
    """Handles the deletion of the route table."""
    route_table_id = get_route_table_id(ec2, config["TAG_RTB"])
    if 'No route table found' in route_table_id or 'error' in route_table_id.lower():
        print(f"Error: {route_table_id}")
    else:
        result = delete_route_table(ec2, route_table_id)
        print(result)

def detach_internet_gateway_operation() -> None:
    """Handles the Internet Gateway detachment operation."""
    vpc_id, error = get_vpc_id(ec2)
    if error:
        print(f"Error: {error}")
        return

    igw_id, error = get_internet_gateway_id(ec2, config["TAG_IGW_NAME"])
    if error:
        print(f"Error: {error}")
        return

    result = detach_internet_gateway(ec2, igw_id, vpc_id)
    print(result)

def delete_internet_gateway_operation() -> None:
    """Handles the Internet Gateway deletion operation."""
    igw_id, error = get_internet_gateway_id(ec2, config["TAG_IGW_NAME"])
    if error:
        print(f"Error: {error}")
        return

    result = delete_internet_gateway(ec2, igw_id)
    print(result)

def disassociate_subnets_operation() -> None:
    """Handles the disassociation of subnets from the route table."""
    result = disassociate_subnets_from_route_table(ec2, config["TAG_RTB"])
    print(result)

def delete_subnets_operation() -> None:
    """Handles the deletion of subnets."""
    subnet_details, subnet_ids = get_subnet_info(ec2, config["TAG_SUBNET"])
    if subnet_ids:
        for subnet_id in subnet_ids:
            print(f"Subnet ID: {subnet_id}, Details: {subnet_details.get(subnet_id, {})}")
    else:
        print("Error: No subnets found or an error occurred.")

    for subnet_id in subnet_ids:
        try:
            response = ec2.delete_subnet(SubnetId=subnet_id)
            print(f"Deleted Subnet ID: {subnet_id}")
        except ClientError as e:
            print(f"Error: Failed to delete Subnet ID: {subnet_id}, Error: {e.response['Error']['Message']}")
        except Exception as e:
            print(f"Error: Failed to delete Subnet ID: {subnet_id}, Error: {str(e)}")

def delete_vpc_operation() -> None:
    """Handles the deletion of the VPC."""
    vpc_id, error_message = get_vpc_id(ec2)
    if error_message:
        print(f"Error: {error_message}")
    elif vpc_id:
        delete_status = delete_vpc(ec2, vpc_id)
        if isinstance(delete_status, int):
            print(f"VPC {vpc_id} deleted successfully with status code: {delete_status}")
        else:
            print(f"Error: {delete_status}")
    else:
        print("Error: No VPC to delete.")

def main():
    operation = input("Do you want to create or delete resources? (create/delete): ").strip().lower()

    if operation == "create":
        # Execute the operations to create the VPC and its associated resources
        create_vpc_operation()              # Step 1: Create VPC if it does not exist
        create_subnet_operation()           # Step 2: Create subnets
        create_route_table_operation()      # Step 3: Create route table if it does not exist
        associate_subnets_operation()       # Step 4: Associate subnets with the route table
        create_internet_gateway_operation() # Step 5: Create Internet Gateway if it does not exist
        attach_internet_gateway_operation() # Step 6: Attach Internet Gateway to the VPC
        create_route_operation()            # Step 7: Create a route in the route table to direct traffic to the Internet Gateway

    elif operation == "delete":
        # Execute the operations to delete the VPC and its associated resources
        delete_route_operation()            # Step 1: Delete the route
        detach_internet_gateway_operation() # Step 2: Detach the Internet Gateway
        delete_internet_gateway_operation() # Step 3: Delete the Internet Gateway
        disassociate_subnets_operation()    # Step 4: Disassociate subnets from the route table
        delete_route_table_operation()      # Step 5: Delete the route table
        delete_subnets_operation()          # Step 6: Delete subnets
        delete_vpc_operation()              # Step 7: Delete the VPC

    else:
        print("Invalid operation. Please specify 'create' or 'delete'.")

if __name__ == "__main__":
    main()
