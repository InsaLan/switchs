from telnetlib import Telnet
import sys, json

if len(sys.argv) < 3:
    print("Syntax: <config_file.json> <switch_password>")
    sys.exit()

scriptFile = open(sys.argv[1], "r")
data = json.loads(scriptFile.read())

switch_number = data["switch_number"]
switch_ip = f"172.16.1.1{switch_number}"

# 1 - we copy all ports datas to a new dictionnary with all port ranges being split at 48
ports = {}
for element in data["ports"]:
    if "-" in element:
        separation = element.split("-")
        premier = int(separation[0])
        deuxieme = int(separation[1])
    else:
        premier = int(element)
        deuxieme = premier
    
    if premier <= 48 and deuxieme > 48:
        ports["{}-48".format(premier)] = data["ports"][element]
        ports["49-{}".format(deuxieme)] = data["ports"][element]
    else:
        ports["{}-{}".format(premier, deuxieme)] = data["ports"][element]

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
print(f"Creating temporary config for switch {switch_number} with vlans: {vlans}")

tmpConfigName = "config48ports/tmpScript.cfg"
# Début de l'écriture du fichier de config
output = open("/var/tftp/" + tmpConfigName, "w")

output.write("begin\n")
# Config IP
output.write("set ip protocol none\n")
output.write(f"set ip address {switch_ip} mask 255.255.255.0 gateway 172.16.1.1\n")

# system
output.write(
"""set switch stack-port ethernet 
set switch member 1 6 
set system login admin super-user enable  password :4eae55fe808cc25a83205b467c653809073c81e760b4d366e210866c3c26993df315ea69075e1a1598:
"""
)

for vlan in vlans:
    output.write("set vlan create {}\n".format(vlan))
           
for port_range in ports:
    separation = port_range.split("-")
    premier = int(separation[0])
    deuxieme = int(separation[1])
    if premier > 48:
        fege = "ge"
    else:
        fege = "fe"
    
    output.write(f"clear vlan egress 1 {fege}.1.{port_range}\n")
    
    if "untagged" in ports[port_range]:
        untagged = ports[port_range]["untagged"]
        output.write(f"set vlan egress {untagged} {fege}.1.{port_range} untagged\n")
            
    tagged_list = ports[port_range]["tagged"]
    for tagged in tagged_list:
        output.write(f"set vlan egress {tagged} {fege}.1.{port_range} tagged\n")


# vlan
for port_range in ports:
    separation = port_range.split("-")
    premier = int(separation[0])
    deuxieme = int(separation[1])
    if premier > 48:
        fege = "ge"
    else:
        fege = "fe"
    
    if "untagged" in ports[port_range]:
        untagged = ports[port_range]["untagged"]
        for i in range(premier, deuxieme + 1):
            output.write(f"set port vlan {fege}.1.{i} {untagged}\n") 


output.write("""
set snmp community hotlinemontreal securityname hotlinemontreal nonvolatile
set snmp access hotlinemontreal security-model v2c read All notify All nonvolatile
set snmp group public user hotlinemontreal security-model v2c nonvolatile
"""
)

output.close();

print("Done creating config")

# 4 - we send the config!

password = sys.argv[2]
tftp_server_ip = "172.16.1.1"

with Telnet(switch_ip) as tn:
    print("Authenticating...")
    tn.read_until(b"Username:")
    tn.write(b"admin\n")
    tn.read_until(b"Password:")
    tn.write(password.encode()+b"\n")
    tn.read_until(b"->")
    
    print(f"Copying config from {tftp_server_ip}...")
    tn.write(b"copy tftp://" + tftp_server_ip.encode() + b"/" + tmpConfigName.encode() + b" configs/generatedConfig.cfg\n")
    tn.read_until(b"->")
    
    print("Configuring switch to use new config...")
    tn.write(b"configure configs/generatedConfig.cfg\n")
    tn.read_until(b"->")
    # besoin de valider avec un Y askip, à vérifier

print("Done!")
