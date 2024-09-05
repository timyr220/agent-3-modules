import json
import requests
import threading
import time
import xml.etree.ElementTree as ET
import test2  # Модуль для роботи з пристроями
import test1  # Модуль для роботи з профілями пристроїв

TEAMCITY_URL = "your_url"
TELEGRAM_BOT_TOKEN = "123c"
JSON_FILE = 'your_file.json'

users = set()
last_message_confirmed = True

def fetch_data_from_teamcity(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Error when receiving data from TeamCity: {response.status_code} {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error when receiving data from TeamCity: {e}")
    return None

def parse_agents(xml_data):
    agents = []
    try:
        root = ET.fromstring(xml_data)
        for agent in root.findall('agent'):
            name = agent.get('name')
            agent_id = agent.get('id')
            href = agent.get('href')

            if name:
                agents.append({
                    'name': name,
                    'id': agent_id,
                    'href': href
                })
            else:
                print(f"Missing an agent without a name. {ET.tostring(agent, 'utf-8')}") # found an agent without a name???
    except ET.ParseError as e:
        print(f"Agent data parsing error: {e}")
    return agents

def send_telemetry_to_thingsboard(device_name, key, value):
    devices = test2.load_devices()
    if device_name in devices:
        device = devices[device_name]
        url = f"{test2.THINGSBOARD_URL}/api/v1/{device['token']}/telemetry"
        payload = {key: value}
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print(f"Telemetry for the device {device_name} has been successfully dispatched.")
            else:
                print(f"Error sending telemetry for the device {device_name}: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error when sending telemetry for the device {device_name}: {e}")
    else:
        print(f"Device {device_name} not found in DEVICES.")

def check_agent_status(agent_id):
    return True  # или False в зависимости от статуса

def check_teamcity_status():
    while True:
        try:
            response = requests.get(TEAMCITY_URL)
            if response.status_code == 200:
                send_telemetry_to_thingsboard('TeamCity', 'status', 1)
            else:
                send_telemetry_to_thingsboard('TeamCity', 'status', 0)
        except requests.exceptions.RequestException as e:
            print(f"Status check error TeamCity: {e}")
            send_telemetry_to_thingsboard('TeamCity', 'status', 0)

        time.sleep(300)

def check_teamcity_agents_status():
    tb_token = test2.get_thingsboard_token()
    while True:
        xml_data = fetch_data_from_teamcity(TEAMCITY_URL)
        if xml_data:
            agents = parse_agents(xml_data)

            for agent in agents:
                agent_name = agent['name']
                devices = test2.load_devices()

                if agent_name in devices:
                    is_online = check_agent_status(agent['id'])
                    if is_online:
                        send_telemetry_to_thingsboard(agent_name, 'online', 0)
                        send_telemetry_to_thingsboard(agent_name, 'offline', 1)
                    else:
                        send_telemetry_to_thingsboard(agent_name, 'offline', 0)
                        send_telemetry_to_thingsboard(agent_name, 'online', 1)
                else:
                    print(f"Device {agent_name} not found in DEVICES. Create it...")
                    test2.update_device_tokens([agent_name])  # Створюємо пристрій
                    is_online = check_agent_status(agent['id'])
                    if is_online:
                        send_telemetry_to_thingsboard(agent_name, 'online', 0)
                        send_telemetry_to_thingsboard(agent_name, 'offline', 1)
                    else:
                        send_telemetry_to_thingsboard(agent_name, 'offline', 0)
                        send_telemetry_to_thingsboard(agent_name, 'online', 1)

                if agent_name in devices:
                    device = {
                        "id": {"id": devices[agent_name]['uuid'], "entityType": "DEVICE"},
                        "name": agent_name,
                        "type": devices[agent_name].get('type', 'Agents'),
                        "label": devices[agent_name].get('label', ''),
                        "deviceProfileId": {"id": test1.get_profile_id_by_name(tb_token, "Agents"), "entityType": "DEVICE_PROFILE"}
                    }
                    test1.update_device_profile(tb_token, device)

        time.sleep(60)


if __name__ == "__main__":
    device_names = ["your_device_names"]
    test2.update_device_tokens(device_names)

    teamcity_status_thread = threading.Thread(target=check_teamcity_status)
    teamcity_agents_thread = threading.Thread(target=check_teamcity_agents_status)

    teamcity_status_thread.start()
    teamcity_agents_thread.start()

    teamcity_status_thread.join()
    teamcity_agents_thread.join()
