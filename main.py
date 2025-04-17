from Config_Convertor import Nokia_Convertor,config_changer
from config_dictionary import *
import json
import ast
import os 
import sys
current_path = os.path.dirname(os.path.abspath(sys.argv[0])) 



with open ("script_config.json","r") as Network_config:
    script_config=Network_config.read()

def Fetch_vlan_range(script_config,city):
    vlan_range = {}
    for key, value in script_config[city]["vlan_range"].items():
        tuples = ast.literal_eval(value)
        vlan_range[key] = [range(t[0], t[1]) for t in tuples]
    return vlan_range

def test(config_dict):
    
    test=open("config.json","w+")

    json.dump(config_dict,test,indent=4)

    test.close()

def cities(system_name):

    city=system_name.split("-")
    if city[0] in script_config:
        return city[0]
    else:
        return 1
    
    


def Huawei_To_Nokia(config_file,city=None):

    with open(config_file,"r") as input:
        input_file=input.read()
    

    config_dict=Huawei(input_file)

    #test(config_dict)

    if city:
        city=city
    else:
        city=cities(config_dict["system_name"])
        if city==1:
            return 1
        else:
            city=city

    Script_config=json.loads(script_config)


    vlan_range=Fetch_vlan_range(Script_config,city)

    """Huawei_dict=open("Huawei_dict","+w")
    Huawei_dict.write(json.dumps(config_dict,indent=4))"""
     
    change=Nokia_Convertor(config_dict,"NOKIA","Nokiaixr7250")

    change.port_changer(config_dict["Port_Configuration"])

    change.connection_profile(config_dict["Eth_Trunk"],vlan_range,Script_config[city]["connection_profile_id"])

    change.Ether_ports_adder(config_dict["Port_Configuration"],config_dict["Eth_Trunk"])

    change.counters(config_dict["isis"],count=0)

    change.vlan_changer(config_dict["vlan"],config_dict["Port_Configuration"],config_dict["Eth_Trunk"],config_dict["isis"])


    change.loopback_changer(config_dict["loopback"])

    change.SAP(config_dict["mpls_peer"],config_dict["vlan"],Script_config[city]["management_vlans"],config_dict["vsi"])

    ouput=open(f"{config_dict['system_name']}.cfg","w+") 



    ouput.write(config_changer(config_dict,"NOKIA",Script_config[city]))


    ouput.close()

    #test(config_dict)


    return (f"{config_dict['system_name']}.cfg")

print(Huawei_To_Nokia("ACCESS_SWITCH.txt","script_config"))


    
    
    




