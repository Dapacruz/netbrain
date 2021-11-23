import requests

class NetBrain():
    def __init__(self, url, username, password, verify=False):
        self.base_url = f'{url}/ServicesAPI/API/V1'
        self.verify = verify

        payload = {
            'username': username,
            'password': password,
        }

        response = requests.get(f'{self.base_url}/Session',
                                json=payload,
                                verify=self.verify)
        response.raise_for_status()

        # Capture the session token
        self.token = response.json()['token']

        self.base_headers = {'Token': self.token}

    def get_tenants(self):
        response = requests.get(f'{self.base_url}/CMDB/Tenants',
                                headers=self.base_headers,
                                verify=self.verify)
        response.raise_for_status()
        return response.json()['tenants']

    def get_domains(self, tenant_id):
        response = requests.get(f'{self.base_url}/CMDB/Domains',
                                params={"tenantid": tenant_id},
                                headers=self.base_headers,
                                verify=self.verify)
        response.raise_for_status()
        return response.json()['domains']

    def set_current_domain(self, tenant_id, domain_id):
        payload = {
            'tenantId': tenant_id,
            'domainId': domain_id,
        }
        response = requests.put(f'{self.base_url}/Session/CurrentDomain',
                                json=payload,
                                headers=self.base_headers,
                                verify=self.verify)
        response.raise_for_status()

    def get_devices(self):
        response = requests.get(f'{self.base_url}/CMDB/Devices',
                                headers=self.base_headers,
                                verify=self.verify)
        response.raise_for_status()
        return response.json()['devices']

    def get_device_groups(self):
        response = requests.get(f'{self.base_url}/CMDB/DeviceGroups',
                                headers=self.base_headers,
                                verify=self.verify)
        response.raise_for_status()
        return response.json()['deviceGroups']

    def get_group_devices(self, group_name):
        url = f'{self.base_url}/CMDB/Devices/GroupDevices/{group_name}'
        response = requests.get(url,
                                headers=self.base_headers,
                                verify=self.verify)

        response.raise_for_status()
        return response.json()['devices']

    def get_device_attributes(self, hostname):
        response = requests.get(f'{self.base_url}/CMDB/Devices/Attributes',
                                params={"hostname": hostname},
                                headers=self.base_headers,
                                verify=self.verify)
        response.raise_for_status()
        return response.json()['attributes']

    def get_device_config_file(self, hostname):
        params = {
            'hostname': hostname,
            'dataType': 'ConfigurationFile',
        }

        response = requests.get(f'{self.base_url}/CMDB/DataEngine/DeviceData/Configuration',
                                params=params,
                                headers=self.base_headers,
                                verify=self.verify)
        response.raise_for_status()
        return response.json()

    def get_device_interfaces(self, hostname):
        response = requests.get(f'{self.base_url}/CMDB/Interfaces',
                                params={"hostname": hostname},
                                headers=self.base_headers,
                                verify=self.verify)
        response.raise_for_status()
        return response.json()['interfaces']

    def get_interface_attributes(self, hostname, interface_name):
        params = {
            'hostname': hostname,
            'interfaceName': interface_name,
        }

        response = requests.get(f'{self.base_url}/CMDB/Interfaces/Attributes',
                                params=params,
                                headers=self.base_headers,
                                verify=self.verify)
        response.raise_for_status()
        return response.json()['attributes']

    def get_interface_type_attributes(self, hostname, interface_type='ipIntfs'):
        params = {
            'hostname': hostname,
            'interfaceType': interface_type,
        }

        response = requests.get(f'{self.base_url}/CMDB/Interfaces/Attributes',
                                params=params,
                                headers=self.base_headers,
                                verify=self.verify)
        response.raise_for_status()
        return response.json()['attributes']

    def get_mac_addr_table(self, hostname):
        params = {
            'hostname': hostname,
            'dataType': 1,
            'tableName': 'macTable'
        }

        response = requests.get(f'{self.base_url}/CMDB/Devices/DeviceRawData',
                                params=params,
                                headers=self.base_headers,
                                verify=self.verify)
        if(response.status_code != 200):
            return None
        else:
            return response.json()['content']

    def get_arp_cache_table(self, hostname):
        params = {
            'hostname': hostname,
            'dataType': 1,
            'tableName': 'arpTable'
        }

        response = requests.get(f'{self.base_url}/CMDB/Devices/DeviceRawData',
                                params=params,
                                headers=self.base_headers,
                                verify=self.verify)
        if(response.status_code != 200):
            return None
        else:
            return response.json()['content']

    def get_interface_ipv4_addresses(self, hostname):
        ip_addrs = []
        for int in self.get_interface_type_attributes(hostname).keys():
            if not int.split()[1].endswith('/32') and not int.split()[1].startswith('1.'):
                ip_addrs.append(int.split()[1])
        return ip_addrs

    def get_site_devices(self, site_path):
        params = {
            'sitePath': site_path,
        }
        response = requests.get(f'{self.base_url}/CMDB/Sites/Devices',
                                params=params,
                                headers=self.base_headers,
                                verify=self.verify)
        response.raise_for_status()
        return response.json()['devices']
