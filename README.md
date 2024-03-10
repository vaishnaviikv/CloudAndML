# CloudAndML - Report
This Python script automates the process of creating Virtual Machine (VM) instances equipped with NVIDIA Tesla P4 GPUs across multiple zones within the Google Cloud Platform (GCP). It's designed to iterate through a randomly selected list of GCP zones, check GPU availability, and attempt to create a VM in each zone until successful. The script logs the outcomes of these attempts, including success or failure reasons, into a CSV file named vm_creation_log_vaish.txt. 

Authentication and Google Cloud API Setup
The script begins by importing necessary modules and setting up authentication using the default credentials found in the environment. It then creates a service object to interact with the Compute Engine API.

## Configuration Variables

project_id : The GCP project ID where the VMs will be created.

gpu_type : The type of GPU to attach to the VM, in this case, nvidia-tesla-p4.

machine_type, image_family, image_project: Specifications for the VM, including the machine type and the operating system image to use.

regions : Random  list of GCP regions to search for available zones.

## Function Definitions

get_zones_for_regions() : Fetches available zones within specified regions.

wait_for_operation_completion() : Polls GCP operations (like VM creation) until they are completed, indicating success or failure.

check_gpu_availability() : Checks if the specified GPU type is available in a given zone.

## Main Process
The script performs the following steps in its main process:

Zone Iteration : It iterates through the zones derived from the specified regions, aiming to find a zone where the specified GPU is available.

VM Creation Attempt : For each zone, the script constructs a VM configuration including the desired GPU and attempts to create the VM.
The VM configuration specifies a custom disk with a specific image, disk size, and type, alongside network and GPU accelerator configurations.

Logging : The outcome of each attempt is logged into vm_creation_log_vaish.txt. The log includes the VM name, zone, GPU type, and creation status ("Success", "Failed", or "GPU Not Available").

VM Deletion : Optionally (currently commented out), the script can also delete the created VMs, although this section requires further completion to function as intended.

## Error Handling
Upon encountering an error during VM creation, the script logs the failure reason. It catches exceptions and includes them in the output log, providing insights into why 
creation might have failed.

## Reporting and Clean-up
The deletion process is intended to clean up resources which can be used for clean-up after testing or in case of partial success.

# Running the Python Script in Google Cloud Shell

## Open Google Cloud Console: Go to the Google Cloud Console.
Activate Cloud Shell: Click on the Cloud Shell icon in the top right corner of the console to open a new shell session.

## Upload the Script:
Click on the three-dot menu in the Cloud Shell panel.
Select "Upload File" and upload your Python script file from your local machine.

## Run the Script:
Make your script executable by running chmod +x your_script.py.
Run the script by typing python your_script.py (use python3 if your shell defaults to Python 2).

This image has the terminal output when the script is run.
<img width="1499" alt="Screenshot 2024-03-08 at 10 05 14 PM" src="https://github.com/vaishnaviikv/CloudAndML/assets/35933479/5e071834-97d6-4cf2-b1ba-6d507294e700">

## Check the Text File Output:
Once the script execution is complete, use cat vm_creation_log_vaish.txt to display the content of your log file.
Alternatively, use the Cloud Shell code editor to open and review the log file.

This image is a snapshot of the vm_creation_log_vaish.txt. It contains the following details : 'VM Name', 'Zone', 'GPU Type', 'Creation Status
<img width="1512" alt="Screenshot 2024-03-08 at 10 05 45 PM" src="https://github.com/vaishnaviikv/CloudAndML/assets/35933479/65882eee-244c-4cbd-bfd2-c88fefb4aaa6">

# SSH into the VM from Cloud Console
Once your VM is created and running, you can SSH into it directly from the Google Cloud Console:

Go to VM Instances Page: Navigate to "Compute Engine" > "VM instances".
Find Your VM: Locate the VM instance you want to SSH into.
Open SSH in Browser: Click the "SSH" button in the row of the VM instance you wish to access. This will open a new window with a terminal session connected to your VM.
Verify CUDA Installation: Once you're SSH'd into the VM, run nvidia-smi to check the status of the GPUs and the installed CUDA version.

SSH into the VM instance : output of the following commands : lspci | grep -i nvidia; nvidia-smi 
<img width="701" alt="Screenshot 2024-03-09 at 10 25 59 PM" src="https://github.com/vaishnaviikv/CloudAndML/assets/35933479/8d530a5c-b08d-4b4f-a44e-7129776e9b10">
