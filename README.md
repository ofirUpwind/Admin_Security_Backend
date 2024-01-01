# Installation Guide


This guide provides instructions on how to use the provided bash script to set up the Admin_Security project on a macOS system.

Prerequisites
* macOS system
* Terminal access
* Visual Studio Code


Steps to Run the Script
1. Download the Script
First, download the install_script.sh from here https://drive.google.com/drive/folders/11N_JisMBCJeUqDFxx42bJFvhDskJTa7Y

2. Give Execute Permission
Before running the script, you need to give it execute permissions. Open your terminal and navigate to the directory where the script is downloaded. Run the following command:

chmod +x install_script.sh

3. Run the Script
Now, you can run the script. You need to provide the directory path as an argument where you want the repository to be cloned. Replace /path/to/directory with your desired path.

./install_script.sh /path/to/directory


The script will perform the following actions:

Install Homebrew (if not already installed)
Update Homebrew
Install Python 3 and pip (if not already installed)
Clone the 'ofirUpwind/Admin_Security' repository into the specified directory
Open the project in Visual Studio Code
Install required Python packages from 'requirements.txt'
Verify the installation by listing the installed packages
Prompt for input to create a '.env' file with DATABASE_URI_LOCAL, JWT_SECRET_KEY, and DATABASE_URI_PROD

4. Follow the Prompts
During the execution of the script, you will be prompted to enter the required values for the .env file. Enter each value as prompted.


Troubleshooting:

If you encounter any issues, contact Ofir:)
