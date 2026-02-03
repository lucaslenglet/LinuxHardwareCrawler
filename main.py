import requests
from bs4 import BeautifulSoup
import json
import os
import argparse
from plyer import notification

def fetch_table(url):
    """
    Fetches the HTML from the URL and extracts the table with id 'devices'.
    Returns a list of dictionaries representing the table rows.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an error for bad status codes
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', id='devices')
    if not table:
        raise ValueError("Table with id 'devices' not found in the HTML.")
    
    # Get all rows
    all_tr = table.find_all('tr')
    if not all_tr:
        raise ValueError("No rows found in the table.")
    
    # First row is headers (th elements)
    header_row = all_tr[0]
    headers = [th.text.strip() for th in header_row.find_all('th')]
    
    # Remaining rows are data
    data_rows = all_tr[1:]
    
    devices = []
    for tr in data_rows:
        cells = [td.text.strip() for td in tr.find_all('td')]
        if len(cells) == len(headers):
            device = dict(zip(headers, cells))
            devices.append(device)
    
    return devices

def load_existing(file_path):
    """
    Loads the existing devices from the JSON file.
    Returns a list of dictionaries.
    """
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return []

def save_devices(file_path, devices):
    """
    Saves the devices to the JSON file.
    """
    with open(file_path, 'w') as f:
        json.dump(devices, f, indent=4)

def compare_and_notify(current, existing, file_path):
    """
    Compares current devices with existing ones.
    Notifies if new devices are found and updates the file.
    """
    # Create sets of frozensets for comparison (since dicts are not hashable)
    existing_set = set(frozenset(d.items()) for d in existing)
    new_devices = []
    for device in current:
        device_fs = frozenset(device.items())
        if device_fs not in existing_set:
            new_devices.append(device)
    
    if new_devices:
        for new in new_devices:
            print(f"New device added: {new}")
            notification.notify(
                title="New Device Detected",
                message=f"New device: {new}",
                app_name="Device Checker"
            )
        # Update the file with current devices
        save_devices(file_path, current)
    else:
        print("No new devices detected.")

def main():
    parser = argparse.ArgumentParser(description="Check for new devices in an HTML table from a URL.")
    parser.add_argument('url', help='The URL to fetch the HTML from.')
    parser.add_argument('--file', default='devices.json', help='Path to the JSON file for storing devices (default: devices.json).')
    args = parser.parse_args()
    
    try:
        current_devices = fetch_table(args.url)
        existing_devices = load_existing(args.file)
        compare_and_notify(current_devices, existing_devices, args.file)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()