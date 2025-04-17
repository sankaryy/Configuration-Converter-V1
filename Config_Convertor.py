import configparser
import re
from jinja2 import FileSystemLoader, Environment
import ipaddress



class Fetcher:
    def __init__(self,Vendor) -> None:
        self.Vendor=Vendor
        self.config=configparser.ConfigParser()
        self.config.read("patterns.ini")

    def extract(self,key,line):
        pattern=self.config[f"{self.Vendor}"][key]
        if pattern:
            find=re.findall(pattern,line)
            if find:
                if len(find)==1:
                    return find[0]
                else:
                    return find
    
    def space_remover(self,line):
        contiguous_lines=re.sub("\s","-",line)
        return contiguous_lines
    
    def sysname(self,line):
        return self.extract("sysname",line)

    def vsi_name(self,line):
        return self.extract("vsi_name",line)
    
    def peer(self,line):
        return self.extract("peer",line)
    
    def vsi_id(self,line):
        return self.extract("vsi_id",line)
    
    def vlan_name(self,line):
        return self.extract("vlan_name",line)
    
    def Server_IP(self,line):
        server_ips={}
        server_ip=self.extract("Server_IP",line)
        if server_ip:
            for tuple in server_ip:
                for ips in tuple:
                    if "." in ips:
                        server_ips.update({ips:[]})
                    else:
                        server_ips[tuple[0]].append(ips)
        return server_ips
                        
    def IP_subnet(self,line):
        return self.extract("IP_subnet",line)
    
    def Ip_prefix(self,line):
        return self.extract("Ip_prefix",line)

    def description(self,line):
        description=self.extract("description",line)
        if description:
            if " " in description:
                return self.space_remover(description)
            else:
                return self.extract("description",line)

    def keychain(self,line):
        return self.extract("keychain",line)
    
    def mpls_signal(self,line):
        return self.extract("mpls_signal",line)
    
    def dhcp(self,line):
        return self.extract("dhcp_server",line)
    
    def isis_process_id(self,line):
        return self.extract("isis_process_id",line)
    
    def isis_cost(self,line):
        return self.extract("isis_cost",line)
    
    def isis_system_id(self,line):
        return self.extract("isis_system_id",line)
    
    def isis_level(self,line):
        return self.extract("isis_level",line)
    
    def isis_cost_style(self,line):
        return self.extract("isis_cost_style",line)
    
    def isis_area_id(self,line):
        area_id=self.extract("isis_area_id",line)

        if area_id=="49":
            return "49."+self.extract("isis_area_id_2",line)
        else:
            return area_id
    
    def IP(self,line):
        return self.extract("IP",line)
    
    def port_no(self,line):
        return self.extract("port_no",line)
    
    def Above_10GIG_port(self,line):
        return self.extract("Above_10GIG_port",line)

    def port_bandwidth(self,line):
        return self.extract("port_bandwidth",line)
    
    def Port_Eth_trunk(self,line):
        return self.extract("Port_Eth-trunk",line)
    
    def port_vlan(self,line):
        port_vlan=self.extract("port_vlan",line)
        if port_vlan:
            if type(port_vlan)==str:
                return port_vlan.split()
            else:
                return [vlans for item in port_vlan for vlans in item.split()]
        
    def Interface_Eth_trunk(self,line):
        return self.extract("interface_Eth-trunk",line)
    
    def qinq_vlans(self,line):
        qinq_vlan_dict={}
        qinq_vlan= self.extract("qinq_vlan",line) 
        if qinq_vlan==None:
            qinq_vlan= self.extract("qinq_vlan_2",line)
            if qinq_vlan:
                for i in qinq_vlan:
                    if type (i)==tuple:
                        qinq_vlan_dict.update({i[1]:[]})
                        for key,items in qinq_vlan_dict.items():
                            if items == i[0]:
                                continue
                            else:
                                qinq_vlan_dict[key].append(i[0])
                if type(qinq_vlan)==tuple:
                    qinq_vlan_dict.update({qinq_vlan[1]:[]})
                    for key,items in qinq_vlan_dict.items():
                            if items == qinq_vlan[0]:
                                continue
                            else:
                                qinq_vlan_dict[key].append(qinq_vlan[0])
                return qinq_vlan_dict           
        else:
            return qinq_vlan
    
    def stacking_vlan(self,line):
        return self.extract("stacking_vlan",line)


    def loopback_id(self,line):
        return self.extract("loopback_id",line)
    
    def mpls_peer(self,line):
        return self.extract("mpls_peer",line)
    
    def dhcp_group(self,line):
        return self.extract("dhcp_group",line)
    
    def dhcp_server_group(self,line):
        return self.extract("dhcp_server_group",line)



class Nokia_Convertor(Fetcher):

    def __init__(self,config_json,vendor,model) -> None:

        self.config_json=config_json
        self.Vendor=vendor
        self.model=model

    def port_changer (self,config_dict):
        super().__init__("NOKIA")
        if config_dict:
            if self.model== "Nokiaixr7250":
                changed_port_no=23
                for keys in list(config_dict.keys()):
                    Nokia_ports=super().extract("port_no",str(keys))
                    if Nokia_ports:
                        if int(Nokia_ports) > 32 or "0/1/" in keys:
                            if config_dict[keys]["status"] != "shutdown":
                                values=config_dict.pop(keys)
                                config_dict["1/1/"+str(changed_port_no)]=values
                                changed_port_no+=1
                                if changed_port_no > 32:
                                    raise Exception("port overflow")
                                
                        elif int(Nokia_ports) < 32:
                            values=config_dict.pop(keys)
                            config_dict["1/1/"+Nokia_ports]=values
                return config_dict
    
    def connection_profile(self,config_dict,vlan_range=None,connection_profile_id=None):
        if config_dict and vlan_range :
            for ether_id in list(config_dict.keys()):
                for service_type, vlan_ranges in vlan_range.items():
                    for vlans in vlan_ranges :
                        if config_dict[ether_id]["stacking_vlan"]:
                            if int(config_dict[ether_id]["stacking_vlan"]) in vlans:
                                config_dict[ether_id].update({"lag":ether_id.split(".")[0]})
                                config_dict[ether_id].update({"connection_profile":connection_profile_id[service_type]})
                                connection_profile_id[service_type]+=1
        return config_dict

    def Ether_ports_adder(self,port_config_dict,Eth_trunk_config_dict):
        for ports in port_config_dict:
            for ether_id in Eth_trunk_config_dict:
                if port_config_dict[ports]["Eth-trunk"]==ether_id:
                    if ether_id and ports:
                        Eth_trunk_config_dict[ether_id]["ports"].append(ports) 
        return Eth_trunk_config_dict
    
    def vlan_changer(self,vlan_config_dict,port_config_dict,ether_config_dict,isis_config_dict):
        for vlans in list(vlan_config_dict.keys()):
            for isis_id in isis_config_dict:
                if isis_id and vlans:
                    if isis_id == vlan_config_dict[vlans]["isis_process_id"]:
                        vlan_config_dict.update({"isis":{isis_id:isis_config_dict[isis_id]}})
            for ports in port_config_dict:
                if port_config_dict[ports]["port_vlan"] and vlans:
                    if vlans in port_config_dict[ports]["port_vlan"]:
                        vlan_config_dict[vlans].update({"port":ports})
                elif ether_config_dict:
                    for ether_id in ether_config_dict:
                        if vlans and ether_config_dict[ether_id]["vlan"]:
                            if vlans in ether_config_dict[ether_id]["vlan"]:
                                if "lag" not in vlan_config_dict[vlans]:
                                    vlan_config_dict[vlans]["lag"]=[]
                                if ether_id not in vlan_config_dict[vlans]["lag"]:
                                    vlan_config_dict[vlans]["lag"].append(ether_id)
            if vlan_config_dict[vlans]["IP"]:
                if type(vlan_config_dict[vlans]['IP'][0])==str:
                    prefix=ipaddress.IPv4Network(f"{vlan_config_dict[vlans]['IP'][0]}/{vlan_config_dict[vlans]['IP'][1]}",strict=False)
                    vlan_config_dict[vlans].update({"prefixlen":prefix.prefixlen})
                if type(vlan_config_dict[vlans]['IP'][0])==tuple:
                    count=1
                    for ips in vlan_config_dict[vlans]["IP"]:
                            if count==1:
                                prefix=ipaddress.IPv4Network(f"{ips[0]}/{ips[1]}",strict=False)
                                vlan_config_dict[vlans].update({ips[0]:{"prefixlen":prefix.prefixlen,"Role":"address"}})
                            elif count >=2:
                                prefix=ipaddress.IPv4Network(f"{ips[0]}/{ips[1]}",strict=False)
                                vlan_config_dict[vlans].update({ips[0]:{"prefixlen":prefix.prefixlen,"Role":"secondary"}})
                            count+=1             
        return vlan_config_dict
    
    def loopback_changer(self,loopback_config_dict):
        counter=0
        for loopback_id in loopback_config_dict:
            if loopback_id:
                if counter ==1:
                    loopback_config_dict[loopback_id].update({"system_id":counter})
                prefix=ipaddress.IPv4Network(f"{loopback_config_dict[loopback_id]['IP_subnet'][0]}/{loopback_config_dict[loopback_id]['IP_subnet'][1]}",strict=False)
                loopback_config_dict[loopback_id].update({"prefixlen":prefix.prefixlen})
                counter+=1
        return loopback_config_dict
    
    def SAP(self,peer_config_dict,vlan_config_dict,management_vlans,vsi):

        self.counters(peer_config_dict,count=1)

        management_vlan_ids=[]
        vlan_id=[]

        for vlan_ids in vlan_config_dict:
            vlan_id.append(vlan_ids)

            if vlan_ids in management_vlans:
                if vlan_config_dict[vlan_ids]["IP"]:
                    management_vlan_ids.append(vlan_ids)
            
            if "vsi_name" in vlan_config_dict[vlan_ids]:
                if vlan_config_dict[vlan_ids]["vsi_name"]:
                    for vsi_id in vsi :
                        if vsi_id == vlan_config_dict[vlan_ids]["vsi_name"]:
                            vsi[vsi_id].update({"Type":"mangement_vsi"})

        if len(management_vlan_ids) >= 2:
            customer=2
            for vlan_ids in management_vlan_ids:
                if str(customer) in vlan_id:
                    customer+=1
                vlan_config_dict[vlan_ids].update({"customer_id":customer})
                vlan_config_dict[vlan_ids].update({"IES":customer})
                customer+=1

        else:
            for vlan_ids in management_vlan_ids:
                vlan_config_dict[vlan_ids].update({"customer_id":2})
                vlan_config_dict[vlan_ids].update({"IES":1})
        

    
    def counters(self,config_dict,count):
        for id in config_dict:
            config_dict[id].update({"changed_id":count})
            count+=1
        return config_dict
    




def config_changer(Source_config_dict,destination_config,Network_config=None):


    if Network_config:
        Source_config={**Source_config_dict,**Network_config}

    config_template_file=Environment(loader=FileSystemLoader("config_changer_templates"))

    template=config_template_file.get_template(f"{destination_config}.jinja")

    return template.render(Source_config)





  