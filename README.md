# Installation Guide

## Prerequisites

Before you begin, ensure you have Python 3 and pip installed on your macOS system. You can verify if they are installed by running the following commands in the terminal:

```bash
python3 --version


If Python 3 is not installed, you can install it using Homebrew (a package manager for macOS). If you don't have Homebrew, install it first by running:

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

Then, install Python 3:

brew install python3

This will also typically install pip alongside Python. If pip is not installed, you can install it by running:

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py



1. Navigate to the Desired Location on Your Computer:
* Open a terminal or command prompt.
* Use the 'cd' command to navigate to the directory where you want to clone the repository
cd [your desired location]

  Replace '[your desired location]' with the path where you want the project to be.

2. Clone the Repository: Run the following command to clone the repository: git clone gh repo clone ofirUpwind/Admin_Security

3. Open the Project in Visual Studio Code:
   * Once the repository is cloned, open the project in Visual Studio Code.
   * You can do this either by navigating to the folder in Visual Studio Code or by running:

code [project directory]

Replace '[project directory]' with the path to the cloned repository.

4. Install Required Packages:
In Visual Studio Code, open the terminal.
Run the following command to install all required packages:

pip install -r requirements.txt

5. verify installation 
  After installation, you can use 'pip list' to see all the installed packages and ensure that everything required is now installed.

Make sure to replace the placeholders like '[your desired location]' and '[project directory]' with the actual paths on your system.
