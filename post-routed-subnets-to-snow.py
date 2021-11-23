#!/usr/bin/env python3

'''Post Routed Subnets

post-routed-subnets-to-snow.py

Author: David Cruz (davidcruz72@gmail.com)

Python version >= 3.6

Required Python packages:
    none

Features:
    Gets routed subnets from NetBrain and posts them to ServiceNow
'''

from ipaddress import IPv4Interface
import json
from netbrain import NetBrain
import os
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

def get_subnets(nb, device_group):
    subnets = []
    devices = get_devices(nb, device_group)
    devices_count = len(devices)
    count = 0
    for device in devices:
        device = device.lower()
        count += 1
        print(f'Collecting {device} IP info ({count}/{devices_count})')

        ip_addresses = nb.get_interface_ipv4_addresses(device)
        for ip in ip_addresses:
            hostname = device
            subnet = IPv4Interface(ip).network

            subnets.append(json.dumps({
                    'u_layer_3_device_name': hostname,
                    'u_layer_3_subnet_range': str(subnet),
                }, sort_keys=True, indent=4)
            )

    return subnets

def post_subnets(url, user, password,subnets):
    headers = {
        'Content-Type':'application/json',
        'Accept':'application/json',
    }
    for s in subnets:
        print(s)
        # response = requests.post(url, auth=(user, password), headers=headers ,data=s)
        # if response.status_code != 200:
        #     print(f'Status: {response.status_code}, Headers: {response.headers}, Error: {response.json()}')

def main():
    t1_start = time.process_time()

    # device_group = 'DC_Test'
    device_group = 'All_Cisco_Corp_Routing_Devices'

    env = import_env('env.json')

    nb = NetBrain(env['netbrain_url'], env['netbrain_user'], env['netbrain_password'])
    subnets = get_subnets(nb, device_group)

    # with open('subnets.txt', 'w') as f:
    #     f.write('\n'.join(subnets))

    post_subnets(env['snow_url'], env['snow_user'], env['snow_password'], subnets)

    t1_stop = time.process_time()
    print(f'\n Took {t1_stop-t1_start :.3f} seconds to complete')


if __name__ == '__main__':
    main()
