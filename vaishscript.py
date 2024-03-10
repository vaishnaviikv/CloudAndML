from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import random
import csv 

# Authentication and service setup
credentials = GoogleCredentials.get_application_default()
service = discovery.build('compute', 'v1', credentials=credentials)

project_id = 'core-verbena-328218'
gpu_type = 'nvidia-tesla-p4'  # Example GPU, adjust as needed
machine_type = 'n1-standard-1'  # Example machine type, adjust as needed
image_family = 'debian-10'
image_project = 'debian-cloud'

regions = [
    'us-central1', 'us-west1', 'us-west2',
    'us-east1', 'us-east4', 'europe-west1',
    'europe-west2', 'europe-west3', 'europe-north1',
    'asia-east1', 'asia-northeast1', 'asia-southeast1'
]

def get_zones_for_regions(service, project_id, regions):
    available_zones = []
    request = service.zones().list(project=project_id)
    response = request.execute()
    for zone in response['items']:
        for region in regions:
            if zone['name'].startswith(region):
                available_zones.append(zone['name'])
    return available_zones

def wait_for_operation_completion(service, project, zone, operation_name):
    print(f"Waiting for operation {operation_name} to finish...")
    while True:
        result = service.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation_name).execute()

        if result['status'] == 'DONE':
            print("Operation completed.")
            if 'error' in result:
                raise Exception(result['error'])
            return
        #time.sleep(1)

def check_gpu_availability(service, project, zone, gpu_type):
    request = service.acceleratorTypes().list(project=project, zone=zone)
    response = request.execute()
    for accelerator in response.get('items', []):
        if accelerator['name'] == gpu_type:
            return True
    return False

available_zones = get_zones_for_regions(service, project_id, regions)
selected_zones = random.sample(available_zones, min(len(available_zones), 12))


vm_names = []
log_file_path = 'vm_creation_log_vaish.txt'

# Ensure the CSV headers are written if the file is created for the first time
with open(log_file_path, 'w', newline='') as file:
    writer = csv.writer(file)
    # Write headers only if the file is newly created or empty
    if file.tell() == 0:
        writer.writerow(['VM Name', 'Zone', 'GPU Type', 'Creation Status'])

for zone in selected_zones:
    vm_name = f"test-vm-{zone.replace('-', '')}"
    if check_gpu_availability(service, project_id, zone, gpu_type): 
        try:
            config = {
    'name': vm_name,
    'machineType': f"zones/{zone}/machineTypes/{machine_type}",
    'disks': [{
        'initializeParams': {
            'diskSizeGb': '50',
            'diskType': f"zones/{zone}/diskTypes/pd-balanced",
            'sourceImage': 'projects/ml-images/global/images/c0-deeplearning-common-gpu-v20240128-debian-11-py310',
        },
        'autoDelete': True,
        'boot': True,
        'deviceName': 'instance-20240309-025317',
        'mode': 'READ_WRITE',
    }],
    'networkInterfaces': [{
        'network': 'global/networks/default',
        'accessConfigs': [{'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}]
    }],
    'guestAccelerators': [{
        'acceleratorType': f"zones/{zone}/acceleratorTypes/{gpu_type}",
        'acceleratorCount': 1
    }],
    'scheduling': {
        'onHostMaintenance': 'TERMINATE',  # Set the VM to be terminated on host maintenance
        'automaticRestart': False,  # Do not automatically restart the VM
    },
    
}
            operation = service.instances().insert(project=project_id, zone=zone, body=config).execute()
            wait_for_operation_completion(service, project_id, zone, operation['name'])
            print(f"VM {vm_name} created successfully with {gpu_type} GPU")
            vm_names.append((zone, vm_name))
            with open(log_file_path, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([vm_name, zone, gpu_type, "Success"])
        except Exception as e:
            print(f"Failed to create VM - {e}")
            with open(log_file_path, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([vm_name, zone, gpu_type, "Failed",{e} ])
    else:
        print(f"{gpu_type} is not available in {zone}, skipping VM creation.")
        with open(log_file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([vm_name, zone, gpu_type, "GPU Not Available"])
# Optional: Wait for user input to proceed with VM deletions
#input("Press Enter to continue with VM deletions...")

# Delete VMs
for zone, vm_name in vm_names:
    try:
        print(f"Deleting VM {vm_name} in zone {zone}...")
        response = service.instances().delete(project=project_id, zone=zone, instance=vm_name).execute()
        wait_for_operation_completion(service, project_id, zone, response['name'])
        print(f"{zone}: VM {vm_name} deleted successfully")
    except Exception as e:
        print(f"{zone}: Failed to delete VM {vm_name} - {str(e)}")
