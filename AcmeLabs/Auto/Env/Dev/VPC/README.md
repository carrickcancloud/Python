# AcmeLabs VPC Management
This package provides a set of Python scripts to manage AWS VPC (Virtual Private Cloud) resources using the Boto3 library. It allows you to create, delete, and manage VPCs, subnets, route tables, and internet gateways in a structured manner.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Functions](#functions)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites
- Python 3.13x
- Boto3 library
- AWS account with appropriate permissions

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/carrickcancloud/Python.git
   
   cd acmelabs-vpc-management
   ```

2.	Install the required Python packages:
    ```bash
    pip install boto3
    ```
    
## Configuration
Before using the scripts, you need to configure the ⁠config.json file. This file contains settings for your VPC configuration such as CIDR blocks, tags, and availability zones. Below is a sample configuration:

    ```json
    {
      "TAG_ENV": "Dev",
      "CIDR_BLOCK": "10.0.0.0/16",
      "CIDR_PUBLIC_SUBNETS": [
        "10.0.1.0/24",
        "10.0.2.0/24",
        "10.0.3.0/24"
      ],
      "TAG_SUBNETS": [
        "AcmeLabs-Dev-Public-Subnet-1",
        "AcmeLabs-Dev-Public-Subnet-2",
        "AcmeLabs-Dev-Public-Subnet-3"
      ],
      "AVAILABILITY_ZONES": [
        "us-east-1a",
        "us-east-1b",
        "us-east-1c"
      ],
      "DEST_CIDR_BLOCK": "0.0.0.0/0",
      "TAG_SUBNET": "AcmeLabs-Dev-Public-Subnet",
      "TAG_RTB": "AcmeLabs-Dev-RouteTable",
      "TAG_IGW_NAME": "AcmeLabs-Dev-IGW",
      "TAG_VPC_NAME": "AcmeLabs-Dev"
    }
    ```
    
## Usage
To run the main script, execute the following command:
```bash
python main.py
```

You will be prompted to choose whether to create or delete resources. Follow the on-screen instructions to proceed with your chosen operation.

## Functions
main.py
The main.py script includes the following key functions:
- create_vpc_operation(): Creates a VPC if it does not already exist.
- create_subnet_operation(): Creates subnets based on the configuration provided in config.json.
- create_route_table_operation(): Creates a route table if it does not already exist.
- associate_subnets_operation(): Associates subnets with the created route table.
- create_internet_gateway_operation(): Creates an Internet Gateway if it does not already exist.
- attach_internet_gateway_operation(): Attaches the Internet Gateway to the VPC.
- create_route_operation(): Creates a route in the Route Table to direct traffic to the Internet Gateway.
- delete_route_operation(): Handles the route deletion operation.
- delete_route_table_operation(): Deletes the specified route table.
- detach_internet_gateway_operation(): Detaches the Internet Gateway from the VPC.
- delete_internet_gateway_operation(): Deletes the specified Internet Gateway.
- disassociate_subnets_operation(): Disassociates subnets from the route table.
- delete_subnets_operation(): Deletes the specified subnets.
- delete_vpc_operation(): Deletes the specified VPC.
- main(): The entry point of the script that prompts the user to create or delete resources.
	
helper.py
The helper.py script contains utility functions that support the operations in main.py. Key functions include:
- vpc_exists(): Checks if a VPC exists with the specified CIDR block and tags.
- subnet_exists(): Checks if a subnet exists based on CIDR block, tag name, VPC ID, and availability zone.
- route_table_exists(): Checks if a route table exists in the specified VPC with the given tags.
- internet_gateway_exists(): Checks if an Internet Gateway exists with the specified tags.
- get_vpc_id(): Retrieves the VPC ID based on the specified name tag.
- get_route_table_id(): Retrieves the Route Table ID based on the given tag.
- get_internet_gateway_id(): Retrieves the Internet Gateway ID based on the specified name tag.
- get_subnet_info(): Retrieves subnet information based on the specified tag prefix.
- create_vpc(): Creates a new VPC with the specified CIDR block and tags.
- create_subnet(): Creates a subnet if it does not already exist.
- associate_route_table(): Associates the specified route table with the given subnets.
- create_internet_gateway(): Creates an Internet Gateway with specified tags.
- attach_internet_gateway(): Attaches an Internet Gateway to the specified VPC.
- create_route(): Creates a route in the specified route table to direct traffic to the Internet Gateway.
- delete_route(): Deletes a route from the specified Route Table.
- detach_internet_gateway(): Detaches an Internet Gateway from a specified VPC.
- delete_internet_gateway(): Deletes the specified Internet Gateway.
- disassociate_subnets_from_route_table(): Disassociates non-main subnets from a route table identified by the given tag.
- delete_route_table(): Deletes a Route Table by its ID.
- delete_vpc(): Deletes the specified VPC by its ID.
	
## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the GNU General Public License v3.0 (GPL-3.0). See the [LICENSE](https://github.com/carrickcancloud/Python/blob/main/LICENSE) file for details.