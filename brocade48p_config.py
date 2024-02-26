from telnetlib import Telnet

class Brocade48pConfig:
    def __init__(self, ip, password, data):
        self.ip = ip
        self.password = password
        self.data = data

    def configure(self):
        # 1 - do nothing
        ports = self.data["ports"]

        # 2 - we create an array of all existing (untagged AND tagged) VLANs in the configuration
        vlans = []
        for port_range in ports:
            if "untagged" in ports[port_range]:
                untagged = ports[port_range]["untagged"]
                if untagged not in vlans:
                    vlans.append(untagged)

            tagged_list = ports[port_range]["tagged"]
            for tagged in tagged_list:
                if tagged not in vlans:
                    vlans.append(tagged)
        
        # 3 - we have all required datas, so let's go for creating the config file that will get pushed to the switch
        print(f"Creating temporary config for switch {self.ip} with vlans: {vlans}")

        tmpConfigName = "config48ports/tmpScript.cfg"
        
        # start writing config file
        output = open("/var/tftp/" + tmpConfigName, "w")

        # system
        output.write("""
ver 08.0.30qT311

stack unit 1
  module 1 icx6430-48p-poe-port-management-module
  module 2 icx6430-sfp-4port-4g-module\n\n\n\n
""")
        for vlan in vlans:
            output.write(f"vlan {vlan} name vlan{vlan} by port\n")
            for port_range, data in ports.items():
                if data["untagged"] == vlan:
                    output.write(f" untagged ethe {port_range_to_brocade(port_range)}\n")
                elif vlan in data["tagged"]:
                    output.write(f" tagged ethe {port_range_to_brocade(port_range)}\n")
            output.write(" no spanning-tree\n\n")
        
        output.write("""
\n\n
""")
        #output.write("end\n")

        output.close()

        print("Done creating config")
        
        # 4 - we send the config!

        tftp_server_ip = "172.16.1.1"

        with Telnet(self.ip) as tn: #check all commented parts with real switch
            print("Authenticating...")
            '''tn.read_until(b"Username:")
            tn.write(b"admin\n")
            tn.read_until(b"Password:")
            tn.write(self.password.encode()+b"\n")
            tn.read_until(b"->")
            '''
            
            print(f"Copying and applying config from {tftp_server_ip}...")
            tn.write(b"copy tftp startup-config " + tftp_server_ip.encode() + b" " + tmpConfigName.encode())
            '''
            tn.read_until(b"->")
            
            tn.read_until(b"Are you sure you want to continue (y/n) [n]?")
            tn.write(b"y")
            '''

        print("Done!")

def port_range_to_brocade(port_range):
    if "-" in port_range:
        separation = port_range.split("-")
        premier = int(separation[0])
        deuxieme = int(separation[1])
        if premier <= 48 and deuxieme > 48:
            return "1/1/{} to 1/1/48".format(premier)
        else:
            return "1/1/{} to 1/1/{}".format(premier, deuxieme)
    else:
        return "1/1/{}".format(port_range)

if __name__ == "__main__":
    import sys, json
    
    if len(sys.argv) < 4:
        print("Syntax: <config_file.json> <config_name> <switch_password> <switch_number>")
        sys.exit()    
    
    scriptFile = open(sys.argv[1], "r")
    config_name = sys.argv[2]
    switch_password = sys.argv[3]
    switch_number = sys.argv[4]
    data = json.loads(scriptFile.read())[config_name]
    
    switch = Brocade48pConfig(f"172.16.1.1{switch_number}", switch_password, data)
    switch.configure()