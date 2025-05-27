import random
import string

def generate_ec2_names(num_names: int, department: str) -> list[str]:
    """
    Generate a list of unique EC2 instance names based on the specified department.

    Args:
        num_names (int): The number of EC2 instance names to generate.
        department (str): The department for which to generate the names.
                          Must be one of 'Marketing', 'Accounting', or 'FinOps'.

    Returns:
        list[str]: A list of generated EC2 instance names, or None if the department is invalid.
    """
    valid_departments = ['Marketing', 'Accounting', 'FinOps']
    if department not in valid_departments:
        print("This Name Generator is only for the Marketing, Accounting, and FinOps departments.")
        return None
    ec2_names = []
    for _ in range(num_names):
        random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))  # Generate random string
        ec2_name = f"EC2-{department}-{random_string}"  # Create the unique EC2 name
        ec2_names.append(ec2_name)  # Add the generated name to the list
    return ec2_names

def main() -> None: # "-> None:" indicates that this function does not return a value, optional but recommended for clarity
    """
    Main function to handle user input and generate EC2 instance names.
    Prompts the user for the number of names and their department, validating input.
    """
    attempts = 0
    max_attempts = 3
    num_names = None
    while attempts < max_attempts:
        try:
            num_names = int(input("How many EC2 instance names do you want? "))  # Get number of names from user
            break  # Exit loop if input is valid
        except ValueError:
            attempts += 1  # Increment attempts if input is invalid
            if attempts == max_attempts:
                exit_choice = input("You have exceeded the maximum attempts. Do you want to exit? (Y/n): ").strip().lower()
                if exit_choice in ['y', 'yes', '']:
                    print("Exiting the script.")
                    return
                else:
                    attempts = 0  # Reset attempts if user chooses to continue
    attempts = 0
    while attempts < max_attempts:
        department = input("Enter your department (Marketing, Accounting, FinOps): ").strip()  # Get department from user
        if department in ['Marketing', 'Accounting', 'FinOps']:
            break  # Exit loop if department is valid
        else:
            attempts += 1  # Increment attempts if department is invalid
            if attempts == max_attempts:
                exit_choice = input("You have exceeded the maximum attempts. Do you want to exit? (Y/n): ").strip().lower()
                if exit_choice in ['y', 'yes', '']:
                    print("Exiting the script.")
                    return
                else:
                    attempts = 0  # Reset attempts if user chooses to continue
    if num_names is not None:
        ec2_names = generate_ec2_names(num_names, department)  # Generate EC2 names
        if ec2_names:
            print("\nGenerated EC2 Instance Names:")
            for name in ec2_names:
                print(name)  # Print each generated EC2 name

if __name__ == "__main__":
    main()  # Execute the main function
