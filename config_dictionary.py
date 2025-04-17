from Config_Convertor import Fetcher





def Huawei(config):

    config_dict={"vsi":{},
                "vlan":{},
                "syslog":None,
                "Port_Configuration":{},
                "Eth_Trunk":{},
                "loopback":{},
                "isis":{},
                "Policy_Configuration":{"AX_ip_details":[],
                                        "DX_ip_details":[]},
                "LDP":[],
                "tacaus_details":{},
                "NTP":{},
                "network_config":{},
                "mpls_peer":{},
                "DHCP":{}}


    fetch=Fetcher("HUAWEI")
    
    LSP=None
    for i in config.split("#"):
        if "sysname" in i:
            config_dict.update({"system_name":fetch.sysname(i)})

        if "vsi" and "vsi-id" in i:
            peers=fetch.peer(i)
            config_dict["vsi"].update({fetch.vsi_name(i):{
                "peer":peers,
                "list": True if type(peers) == list else None,
                "vsi_id":fetch.vsi_id(i)}})
            for vsi in config_dict["vsi"]:
                if config_dict["vsi"][vsi]['list']:
                    raise Exception(f'VSI: {vsi} Has multiple Peers')

        if "interface Vlanif"  in i:
                vlan=fetch.vlan_name(i)
                if type(vlan)==str:
                    config_dict["vlan"].update({fetch.vlan_name(i)
                                        :{"IP":fetch.IP_subnet(i),
                                        "isis_process_id":fetch.isis_process_id(i),
                                        "description":fetch.description(i),
                                        "keychain":fetch.keychain(i),
                                        "mpls_signal":fetch.mpls_signal(i),
                                        "isis_cost":fetch.isis_cost(i),
                                        "isis_role":"silent" if "isis silent" in i else None,
                                        "vsi_name":fetch.vsi_name(i),
                                        "DHCP":[fetch.dhcp_group(i)] if "dhcp" in i else None}})
        if "loghost" in i:
            config_dict["syslog"]=fetch.IP(i)

        if "interface" in i:
            port_no=fetch.port_no(i)

            if type(port_no)==str:

                config_dict["Port_Configuration"].update({fetch.port_no(i):{
                                                    "description":fetch.description(i),
                                                    "Port_BW":"1" if fetch.port_bandwidth(i)=="GigabitEthernet" else "10",
                                                    "Eth-trunk":fetch.Port_Eth_trunk(i),
                                                    "status":"shutdown" if "shutdown" in i else None,
                                                    "port_vlan":fetch.port_vlan(i)}})
            
            config_dict["Eth_Trunk"].update({fetch.Interface_Eth_trunk(i):{
                                            "description":fetch.description(i),
                                            "vlan":fetch.port_vlan(i),
                                            "qinq_vlan":fetch.qinq_vlans(i),
                                            "stacking_vlan":fetch.stacking_vlan(i),
                                            "ports":[]}})
           
          
        
        if "interface LoopBack"in i:
            config_dict["loopback"].update({fetch.loopback_id(i):{
                                            "IP_subnet":fetch.IP_subnet(i),
                                            "isis_process_id":fetch.isis_process_id(i)}})
            
        if  "isis" in i:
            config_dict["isis"].update({fetch.isis_system_id(i):{
                                        "level":fetch.isis_level(i),
                                        "isis_cost_style":fetch.isis_cost_style(i),
                                        "area_id":fetch.isis_area_id(i)}})
            

        
        if "LSP_AX_IP" in i:
            LSP=i.split("\n")
        
        if "mpls ldp remote-peer" in i:
            config_dict["LDP"].append(fetch.peer(i))

        if "hwtacacs-server" in i:
            server_ip=fetch.Server_IP(i)
            if server_ip:
                for server_ips,role in server_ip.items():
                    config_dict["tacaus_details"].update({server_ips:role})

        if "ntp-service" in i:
            config_dict["NTP"].update(fetch.Server_IP(i))

        if "mpls ldp" in i:
            peer=fetch.mpls_peer(i)
            if peer:
                config_dict["mpls_peer"].update({peer:{}})

        if "dhcp-server" in i:
            group=fetch.dhcp_server_group(i)
            IP=fetch.IP(i)
            config_dict["DHCP"].update({group:IP})
                       
    if LSP:
        for lsp_ip in LSP:
            if lsp_ip:
                IP_prefix=fetch.Ip_prefix(lsp_ip)
                if IP_prefix:
                    if "LSP_AX_IP" in lsp_ip:
                        config_dict["Policy_Configuration"]["AX_ip_details"].append(IP_prefix) 
                    if "LSP_DX_IP" in lsp_ip:
                        config_dict["Policy_Configuration"]["DX_ip_details"].append(IP_prefix) 
                else:
                    config_dict["Policy_Configuration"].clear()
    else:
        config_dict.pop("Policy_Configuration")           

    return config_dict

def nokia_config_dict():
    pass
    


    





    

    

            







