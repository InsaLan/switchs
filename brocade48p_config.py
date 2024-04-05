from telnetlib import Telnet


def brocade48p_config(switch, data, access_password, new_password):
    ip = switch["ip"]

    # TODO: put hostname
    name = switch["name"]

    # 1 - do nothing
    ports = data["ports"]

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

    # start writing config file
    output = open("/var/tftp/" + tmpConfigName, "w")

    # system
    output.write(
        """ver 08.0.30qT311
!
stack unit 1
module 1 icx6430-48p-poe-port-management-module
module 2 icx6430-sfp-4port-4g-module\n!\n!\n!\n!
"""
    )
    for vlan in vlans:
        output.write(f"vlan {vlan} name vlan{vlan} by port\n")
        if vlan != 1:  # Vlan #1's config is done later via dual mode
            for port_range, data in ports.items():
                if vlan in data["tagged"]:
                    output.write(f" tagged ethe {port_range_to_brocade(port_range)}\n")
                elif data["untagged"] == vlan:
                    output.write(
                        f" untagged ethe {port_range_to_brocade(port_range)}\n"
                    )
        output.write(" no spanning-tree\n!\n")

    output.write(
        f"""!\n!\n!\n!
enable super-user-password {new_password}
snmp-server community hotlinemontreal ro
!
hostname management
ip address {ip} 255.255.255.0 dynamic
ip default-gateway 172.16.1.1
!
!
clock timezone us Alaska
web-management https\n"""
    )

    for port_range, data in ports.items():
        if data["untagged"] == 1:
            if "-" in port_range:
                separation = port_range.split("-")
                premier = int(separation[0])
                deuxieme = int(separation[1])
                if premier <= 48 and deuxieme > 48:
                    for i in range(premier, 49):
                        output.write(f"interface ethernet 1/1/{i}\n" " dual-mode\n!\n")
                else:
                    for i in range(premier, deuxieme + 1):
                        output.write(f"interface ethernet 1/1/{i}\n" " dual-mode\n!\n")
            else:
                output.write(f"interface ethernet 1/1/{port_range}\n" " dual-mode\n!\n")

    output.write(
        f"""!
!
!
!
!
!
end
"""
    )
    output.close()

    print("Done creating config")

    # 4 - we send the config!

    tftp_server_ip = "172.16.1.1"

    with Telnet(ip) as tn:
        print("Authenticating...")
        tn.read_until(b">")
        tn.write(b"enable\n")
        tn.read_until(b"Password:")
        tn.write(access_password.encode() + b"\n")
        tn.read_until(b"#")

        print(f"Copying and applying config from {tftp_server_ip}...")
        tn.write(
            b"copy tftp startup-config "
            + tftp_server_ip.encode()
            + b" "
            + tmpConfigName.encode()
            + b"\n"
        )
        tn.read_until(b"Download startup-config from TFTP server done.")

        print("Config saved, rebooting switch...")
        tn.write(b"reload\n")
        tn.read_until(b"Are you sure? (enter 'y' or 'n'):")
        tn.write(b"y")
        tn.read_until(b"(enter 'y' or 'n'):", 10)
        tn.write(b"y")

    print("Done!")


def port_range_to_brocade(
    port_range,
):  # Convert "1-48" to "1/1/1 to 1/1/48" for example, weird brocade syntax
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
