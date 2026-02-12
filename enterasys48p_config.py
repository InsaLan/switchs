# NEW VERSION
# On préfère cette version à enterasys48p simple car elle push directement la config
# sur le switch et ne rentre pas toutes les commandes via telnet (ce qui bugue sur les 48p)
import re
from telnetlib import Telnet

def enterasys48p_config(switch, config, access_password, new_password):
    ip = switch["ip"]
    # todo: put hostname in switch
    name = switch["name"]

    # 1 - we copy all ports datas to a new dictionnary with all port ranges being split at 48
    ports = {}
    for element in config["ports"]:
        port_range = element.split(".")[-1]
        if "-" in port_range:
            separation = port_range.split("-")
            premier = int(separation[0])
            deuxieme = int(separation[1])
        else:
            premier = int(port_range)
            deuxieme = premier

        if premier <= 48 and deuxieme > 48:
            ports["{}-48".format(premier)] = config["ports"][element]
            ports["49-{}".format(deuxieme)] = config["ports"][element]
        else:
            ports["{}-{}".format(premier, deuxieme)] = config["ports"][element]

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
    print(f"Creating temporary config for switch {ip} with vlans: {vlans}")

    tmpConfigName = "config48ports/tmpScript.cfg"
    # Début de l'écriture du fichier de config
    output = open("/var/tftp/" + tmpConfigName, "w")

    output.write("begin\n")
    # Config IP
    #output.write("set ip protocol none\n")
    #output.write(f"set ip address {ip} mask 255.255.255.0 gateway 172.16.1.1\n")

    # system
    output.write(
        f"""
set switch stack-port ethernet 
set switch member 1 6 
set system login admin super-user enable  password :{new_password}:
"""
    )

    for vlan in vlans:
        output.write("set vlan create {}\n".format(vlan))

    serial_number = get_serial_number(ip, access_password)

    for port_range in ports:
        separation = port_range.split("-")
        premier = int(separation[0])
        deuxieme = int(separation[1])
        if premier > 48 or serial_number in ["B5K125-48P2", "B5G124-48", "B5K125-48"]:
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
        if premier > 48 or serial_number == "B5K125-48P2":
            fege = "ge"
        else:
            fege = "fe"

        if "untagged" in ports[port_range]:
            untagged = ports[port_range]["untagged"]
            for i in range(premier, deuxieme + 1):
                output.write(f"set port vlan {fege}.1.{i} {untagged} modify-egress\n")

    output.write(
        """
set snmp community hotlinemontreal securityname hotlinemontreal
set snmp access hotlinemontreal security-model v2c read All notify All nonvolatile
set snmp group public user hotlinemontreal security-model v2c nonvolatile
"""
    )
    output.write("end\n")

    output.close()

    print("Done creating config")

    # 4 - we send the config!

    tftp_server_ip = "172.16.1.1"

    with Telnet(ip) as tn:
        print("Authenticating...")
        tn.read_until(b"Username:")
        tn.write(b"admin\n")
        tn.read_until(b"Password:")
        tn.write(access_password.encode() + b"\n")
        tn.read_until(b"->")

        print(f"Copying config from {tftp_server_ip}...")
        tn.write(
            b"copy tftp://"
            + tftp_server_ip.encode()
            + b"/"
            + tmpConfigName.encode()
            + b" configs/generatedConfig.cfg\n"
        )
        tn.read_until(b"->")

        print("Configuring switch to use new config...")
        tn.write(b"configure configs/generatedConfig.cfg\n")

        tn.read_until(b"Are you sure you want to continue (y/n) [n]?")
        tn.write(b"y")

    print("Done!")

def get_serial_number(ip, access_password):
    with Telnet(ip) as tn:
        tn.read_until(b"Username:")
        tn.write(b"admin\n")
        tn.read_until(b"Password:")
        tn.write(access_password.encode() + b"\n")
        tn.read_until(b"->")
        tn.write(b"show version\n")
        tn.read_until(b"--\r\n")
        tn.read_until(b"\r\n")
        data = tn.read_until(b"\r\n")
        serial = re.search(r"[A|B]\w+-\w+", data.decode())
        return serial.group(0)
