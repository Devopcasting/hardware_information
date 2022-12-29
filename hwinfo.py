#!/usr/bin/env python3
#####################################
# Linux System Hardware Information #
#####################################
import subprocess
import json
import requests
import re

# Function: Get 'lshw' command output
def cmd_lshw(classinfo:str) -> list:
    lshw_cmd = ["lshw","-json","-C", classinfo]
    proc     = subprocess.Popen(lshw_cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    return json.loads(proc.communicate()[0])

# Function: Get Processor Info
def get_cpu_info() -> str:
    cpu_info = cmd_lshw("cpu")
    return cpu_info[0]['product']

# Function: Get Graphic Info
def get_graphic_info() -> str:
    graphic_info = cmd_lshw("display")
    return graphic_info[0]['product']

# Function: Get Memory Info
def get_memory_info() -> str:
    cmd = 'free -mh | grep Mem | awk \'{print $2}\''
    proc = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    return proc.communicate()[0].decode('utf-8').strip('\n')

# Function: Get Audio Info
def get_audio_info() -> list:
    audio_info_list = []
    audio_info = cmd_lshw("multimedia")
    for i in audio_info:
        audio_info_list.append(i['product'])
    return audio_info_list

# Function: Get Hardisk Size
def get_hard_disk_size_info() -> str:
    cmd = 'df -h / | tail -n1 | awk \'{print $2}\''
    proc = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    return proc.communicate()[0].decode('utf-8').strip('\n')

# Function: Get Motherboard Info
def get_motherboard_info() -> str:
    cmd = 'dmidecode -t 2 | grep Product | awk -F": " \'{print $2}\''
    proc = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if proc.communicate()[0].decode('utf-8').strip('\n') == " ":
        cmd = 'dmidecode -t 2 | grep Manufacturer | awk -F": " \'{print $2}\''
        proc = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        return proc.communicate()[0].decode('utf-8').strip('\n')
    else:
        return proc.communicate()[0].decode('utf-8').strip('\n')


# Function: Get Wireless Network Info
def get_wireless_network_info() -> dict:
    wireless_network_info = cmd_lshw("network")
    wireless_network_info_dict = {}

    for i in wireless_network_info:
        if i['description'] == "Wireless interface":
            wireless_network_info_dict["Description"] = "Wireless"
            if 'product' not in i.keys():
                wireless_network_info_dict["Product"] = i['configuration']['driver'].upper()+" Wireless Adapter"
            else:
                wireless_network_info_dict["Product"] = i['product']

            wireless_network_info_dict["Mac Address"] = i['serial'].upper()

    if len(wireless_network_info_dict) == 0 :
        wireless_network_info_dict["Description"] = "NA"
        wireless_network_info_dict["Product"] = "NA"
        wireless_network_info_dict["Mac Address"] = "NA"
        return wireless_network_info_dict
    else:
        return wireless_network_info_dict

# Function: Get Ethernet Network Info
def get_ether_network_info() -> dict:
    ether_network_info = cmd_lshw("network")
    ether_network_info_dict = {}

    for i in ether_network_info:
        if i['description'] == "Ethernet interface":
            ether_network_info_dict["Description"] = i['description']
            ether_network_info_dict["Product"] = i['product']
            ether_network_info_dict["Mac Address"] = i['serial'].upper()

    if len(ether_network_info_dict) == 0:
        ether_network_info_dict["Description"] = "NA"
        ether_network_info_dict["Product"] = "NA"
        ether_network_info_dict["Mac Address"] = "NA"
        return ether_network_info_dict
    else:
        return ether_network_info_dict

# Function: Get Laptop Model
def get_laptop_model() -> str:
    cmd = "dmidecode -s system-version"
    proc = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    return proc.communicate()[0].decode('utf-8').strip('\n')

# Function Push Data to Flask Server
def push_hwinfo(hwinfodict:dict):

    headers = {'Content-Type': 'application/json'}
    response = requests.post(flask_server_url,data=json.dumps(hwinfodict),headers=headers,timeout=10)
    return response.status_code
    
def main() -> dict :
    hw_info_dict = {}

    # Processor Info.
    hw_info_dict['PROCESSOR'] = get_cpu_info()
    # Motherboard Info
    hw_info_dict['MOTHERBOARD'] = get_motherboard_info()
    # Graphic Info
    hw_info_dict['GRAPHICS'] = get_graphic_info()
    # Total RAM Info
    hw_info_dict['TOTAL RAM'] = get_memory_info()
    # Hardisk Size
    hw_info_dict['Hard Disk Size'] = get_hard_disk_size_info()
    # Audio Info
    hw_info_dict['Audio'] = get_audio_info()
    # Ethernet Network Info
    hw_info_dict['Ethernet Network'] = get_ether_network_info()
    # Wireless Network Info
    hw_info_dict['Wireless Network'] = get_wireless_network_info()

    # Check for Laptop or Desktop device
    machine_info = subprocess.check_output(["hostnamectl", "status"], universal_newlines=True)
    m = re.search('Chassis: (.+?)\n', machine_info)
    chassis_type = m.group(1)
    if chassis_type == "laptop":
        hw_info_dict['Model'] = get_laptop_model()
    else:
        hw_info_dict['Model'] = "NA"

    #return hw_info_dict
    return push_hwinfo(hw_info_dict)

if __name__ == '__main__':

    # Flask Server URL
    #flask_server_url = "http://192.168.1.109:5000/push_hwinfo"
    flask_server_url = "http://tpc.pythonanywhere.com/push_hwinfo"
    print(main())
