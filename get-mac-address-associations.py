#!/usr/bin/env python3

'''Get MAC Address Associations

get-mac-address-associations.py

Author: David Cruz (davidcruz72@gmail.com)

Python version >= 3.6

Required Python packages:
    none

Features:
    Gets MAC address associations from NetBrain
'''

import json
from netbrain import NetBrain
import os
import re
import requests
import time

# Disable SSL certificate verification warnings
requests.packages.urllib3.disable_warnings()

def import_env(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    else:
        return None

def get_devices(nb, device_group):
    tenant_name = 'Initial Tenant'
    domain_name = 'WSI_NB_Domain'
    tenant_id = next(dict['tenantId'] for dict in nb.get_tenants() if dict['tenantName'] == tenant_name)
    domain_id = next(dict['domainId'] for dict in nb.get_domains(tenant_id) if dict['domainName'] == domain_name)
    nb.set_current_domain(tenant_id, domain_id)

    devices = [dict['hostname'] for dict in nb.get_group_devices(device_group)]
    devices.sort()

    return devices

def get_mac_address_associations(nb, device_group):
    re_mac_addr = re.compile(r'([0-9a-f]{4}\.){2}[0-9a-f]{4}')
    mac_address_associations = []
    devices = get_devices(nb, device_group)
    devices_count = len(devices)
    count = 0
    for device in devices:
        device = device.lower()
        count += 1

        print(f'Collecting {device} MAC address table ({count}/{devices_count})')

        mac_addresses = []
        mac_address_table = nb.get_mac_addr_table(device)
        if(mac_address_table):
            mac_address_table = mac_address_table.split('\n')
            for e in mac_address_table:
                if(match := re_mac_addr.search(e)):
                    mac_addresses.append(match.group(0))

        mac_address_associations.append(json.dumps({
                'device': device,
                'mac_addresses': mac_addresses,
            }, indent=4, sort_keys=True)
        )

    return mac_address_associations

def main():
    t1_start = time.process_time()

    device_group = 'All_Cisco_Corp_Switches'

    env = import_env('env.json')

    nb = NetBrain(env['netbrain_url'], env['netbrain_user'], env['netbrain_password'])
    mac_address_associations = get_mac_address_associations(nb, device_group)

    # print('\n'.join(mac_address_associations))

    with open('mac-address-associations.txt', 'w') as f:
        f.write('\n'.join(mac_address_associations))

    t1_stop = time.process_time()
    print(f'\n Took {t1_stop-t1_start :.3f} seconds to complete')


if __name__ == '__main__':
    main()
