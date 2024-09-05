import json
import requests

THINGSBOARD_URL = "https://thingsboard.cloud"
THINGSBOARD_USERNAME = "USERNAME"
THINGSBOARD_PASSWORD = "PASSWORD"
JSON_FILE = 'your_file.json'


def get_thingsboard_token():
    auth_url = f"{THINGSBOARD_URL}/api/auth/login"
    payload = {
        "username": THINGSBOARD_USERNAME,
        "password": THINGSBOARD_PASSWORD
    }
    try:
        response = requests.post(auth_url, json=payload)
        response.raise_for_status()
        return response.json()['token']
    except requests.exceptions.RequestException as e:
        print(f"Error when receiving a ThingsBoard token: {e}")
        return None


def get_device_by_name(device_name, tb_token):
    url = f"{THINGSBOARD_URL}/api/tenant/devices?deviceName={device_name}"
    headers = {
        "X-Authorization": f"Bearer {tb_token}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if 'id' in data:
            print(f"Device {device_name} found in ThingsBoard. ID: {data['id']['id']}")
            return data
        else:
            print(f"Device {device_name} not found in ThingsBoard. response API: {data}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error when searching for a device {device_name}: {e}")
        return None


def create_device(device_name, tb_token):
    url = f"{THINGSBOARD_URL}/api/device"
    headers = {
        "X-Authorization": f"Bearer {tb_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": device_name,
        "type": "Agents"  # Здесь можно указать тип устройства
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        device = response.json()
        print(f"Device {device_name} has been successfully created. ID: {device['id']['id']}")
        return device
    except requests.exceptions.RequestException as e:
        print(f"Error during device creation {device_name}: {e}")
        return None


def get_device_credentials(device_id, tb_token):
    url = f"{THINGSBOARD_URL}/api/device/{device_id}/credentials"
    headers = {
        "X-Authorization": f"Bearer {tb_token}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving device credentials {device_id}: {e}")
        return None

def load_devices():
    try:
        with open(JSON_FILE, 'r') as file:
            devices = json.load(file)
        print(f"Device data loaded from the file {JSON_FILE}.")
        return devices
    except FileNotFoundError:
        print(f"File {JSON_FILE} not found. Return an empty device list.")
        return {}
    except json.JSONDecodeError as e:
        print(f"JSON file decoding error {JSON_FILE}: {e}")
        return {}


def save_devices(devices):
    with open(JSON_FILE, 'w') as file:
        json.dump(devices, file, indent=4)
    print(f"Device data has been successfully saved to a file {JSON_FILE}.")


def update_device_tokens(device_names):
    tb_token = get_thingsboard_token()
    if not tb_token:
        print("Failed to get the ThingsBoard token. Exit...")
        return

    devices = {}
    for name in device_names:
        device = get_device_by_name(name, tb_token)
        if not device:
            print(f"Device {name} not found. Creating a new device...")
            device = create_device(name, tb_token)

        if device:
            credentials = get_device_credentials(device['id']['id'], tb_token)
            if credentials:
                devices[name] = {
                    'token': credentials['credentialsId'],
                    'uuid': device['id']['id']
                }
                print(f"These devices {name} preserved.")
            else:
                print(f"Failed to retrieve credentials for the device {name}.")

    if devices:
        save_devices(devices)
    else:
        print("No data to save.")


if __name__ == "__main__":


    device_names = ["your_device_names"]
    update_device_tokens(device_names)


