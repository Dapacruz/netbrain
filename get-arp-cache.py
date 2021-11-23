#!/usr/bin/env python3

'''Get ARP Cache

get-arp-cache.py

Author: David Cruz (davidcruz72@gmail.com)

Python version >= 3.6

Required Python packages:
    none

Features:
    Gets ARP cache from Cisco switches in NetBrain
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

def get_arp_cache(nb, device_group):
    re_mac_addr = re.compile(r'([0-9a-f]{4}\.){2}[0-9a-f]{4}')
    re_ip_addr = re.compile(r'([0-9]{1,3}\.){3}[0-9]{1,3}')
    arp_cache = {}
    devices = get_devices(nb, device_group)
    devices_count = len(devices)
    count = 0
    for device in devices:
        device = device.lower()
        count += 1

        print(f'Collecting {device} ARP cache ({count}/{devices_count})')

        arp_cache_table = nb.get_arp_cache_table(device)
        if(arp_cache_table):
            for e in arp_cache_table.split('\n'):
                if(match := re_mac_addr.search(e)):
                    mac = match.group(0)
                    ip = re_ip_addr.search(e).group(0)

                    arp_cache[mac] = {
                        'ip': ip,
                        'device': device
                    }

    return arp_cache

def main():
    t1_start = time.process_time()

    device_group = 'All_Cisco_Corp_Switches'

    env = import_env('env.json')

    nb = NetBrain(env['netbrain_url'], env['netbrain_user'], env['netbrain_password'])
    arp_cache = get_arp_cache(nb, device_group)

    # print('\n'.join(arp_cache))

    with open('arp-cache.txt', 'w') as f:
        f.write(json.dumps(arp_cache, indent=4, sort_keys=True))

    t1_stop = time.process_time()
    print(f'\n Took {t1_stop-t1_start :.3f} seconds to complete')


if __name__ == '__main__':
    main()
