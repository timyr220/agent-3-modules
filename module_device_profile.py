import requests

THINGSBOARD_URL = "https://thingsboard.cloud"
THINGSBOARD_USERNAME = "USERNAME"
THINGSBOARD_PASSWORD = "PASSWORD"


def get_thingsboard_token():
    """Get ThingsBoard token"""
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
        print(f"Error getting ThingsBoard token: {e}")
        return None

def get_devices(token):
    """Get list of all devices"""
    headers = {
        'X-Authorization': f'Bearer {token}'
    }
    url = f'{THINGSBOARD_URL}/api/deviceInfos/all?pageSize=1000&page=0&sortProperty=createdTime&sortOrder=DESC&includeCustomers=true'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['data']
    except requests.exceptions.RequestException as e:
        print(f"Error getting devices: {e}")
        return []

def get_profile_id_by_name(token, profile_name):
    """Get device profile ID by name"""
    headers = {
        'X-Authorization': f'Bearer {token}'
    }
    url = f'{THINGSBOARD_URL}/api/deviceProfiles?pageSize=100&page=0'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        profiles = response.json()['data']
        for profile in profiles:
            if profile['name'] == profile_name:
                return profile['id']['id']
        print(f"Profile with name {profile_name} not found.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error getting profiles: {e}")
        return None

def update_device_profile(token, device):
    """Update device with a new device profile"""
    headers = {
        'X-Authorization': f'Bearer {token}'
    }
    url = f'{THINGSBOARD_URL}/api/device'
    device_payload = {
        "id": device['id'],
        "name": device['name'],
        "type": device['type'],
        "deviceProfileId": device['deviceProfileId'],
        "label": device.get('label', ''),  # Set default value
        "additionalInfo": device.get('additionalInfo', {})  # Set default value
        # "tenantId": device['tenantId'],  # Remove tenantId
        # "customerId": device['customerId']  # Optionally remove customerId
    }
    try:
        response = requests.post(url, json=device_payload, headers=headers)
        response.raise_for_status()
        print(f"Device '{device['name']}' updated successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error updating device {device['name']}: {e}")

def main():
    token = get_thingsboard_token()
    if not token:
        return

    # List of device names to update
    devices_to_update = ["your_device_names"]

    # Get the profile ID for "Agents"
    agents_profile_id = get_profile_id_by_name(token, "Agents")
    if not agents_profile_id:
        return

    # Get all devices
    devices = get_devices(token)

    # Update device profile by name
    for device in devices:
        if device['name'] in devices_to_update:
            device['deviceProfileId'] = {"id": agents_profile_id, "entityType": "DEVICE_PROFILE"}
            update_device_profile(token, device)

if __name__ == '__main__':
    main()
