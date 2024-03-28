# Procurve is awesome

from telnetlib import Telnet

import re

def printbytes(x):
    regex = re.compile(b"\\x1b[^hH]*?[hH]")
    x = regex.sub(b"", x).decode()
    print(x.split('\n')[-1])



class Procurve24pConfig:
    def __init__(self, ip, name, password, model_id, data):
        self.ip = ip
        self.name = name
        self.model_id = model_id
        self.data = data
        self.password = password

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

        tmpConfigName = "tmpScript.cfg"
        # Début de l'écriture du fichier de config
        output = open("/var/tftp/" + tmpConfigName, "w")

        output.write(
            f"; {self.model_id} Configuration Editor; Created on release #Y.11.51\n\n"
        )
        output.write(f'hostname "{self.name}"\n')
        output.write('snmp-server community "hotlinemontreal" Unrestricted\n')

        for vlan in vlans:
            output.write("vlan {}\n".format(vlan))
            output.write(f'  name "vlan{vlan}"\n')
            output.write("  ip address dhcp-bootp\n")
            for port_range, data in ports.items():
                if data["untagged"] == vlan:
                    output.write(f"  untagged {port_range}\n")
                elif vlan in data["tagged"]:
                    output.write(f"  tagged {port_range}\n")
            output.write("  exit\n")

        output.write("password manager\n")

        output.close()

        print("Config :")
        output = open("/var/tftp/" + tmpConfigName, "r")
        print(output.read())

        # 4 - we send the config!

        tftp_server_ip = "172.16.1.1"

        with Telnet(self.ip) as tn:
            is_password_set = bypass_dumb_prompts(tn, self.password)

            if not is_password_set:
                setpassword(tn, self.password)

            print(f"Copying config from {tftp_server_ip}...")
            tn.write(
                b"copy tftp startup-config "
                + tftp_server_ip.encode()
                + b" "
                + tmpConfigName.encode()
                + b"\n"
            )
            buf = tn.read_until(b"[y/n]", timeout=1)
            printbytes(buf)
            tn.write(b"y")

        print("Done!")


def bypass_dumb_prompts(tn, password):
    # this is dumb
    # keep giving the switch what it wants until it doesn't ask for anything anymore
    idx = 1
    ls_users = [b"manager", b"admin"]
    i_usr = 0
    is_password_set = False
    while idx >= 0:
        idx, match, buf = tn.expect([b"Password", b"continue", b"Username"], timeout=3)
        printbytes(buf)
        if match is None:
            break
        if match.group(0).lower() == b"username":
            print(f"username requested. sending {ls_users[i_usr]}")
            tn.write(ls_users[i_usr] + b"\n")
            i_usr += 1

        elif match.group(0).lower() == b"continue":
            print("continue requested. sending newline")
            tn.write(b"\n")

        elif match.group(0).lower() == b"password":
            print("Authenticating...")
            tn.write(password.encode() + b"\n")
            is_password_set = True
        else:
            print(f"Shit broke my dude, match={match}")
            break

    if not is_password_set:
        print(
            "\n\n[WARNING] (SPOOKY) No password configured! This script will try to set it.\n\n")

    return is_password_set
        

def setpassword(tn, password):
    tn.write(b"config\n")
    idx, match, buf = tn.expect([b'#'], timeout=3)
    printbytes(buf)
    if match is None:
        print("BROKE: couldn't set password, couldn't enter config")
        return
    tn.write(b"password manager\n")

    idx, match, buf = tn.expect([b':'], timeout=3)
    printbytes(buf)
    if match is None:
        print("BROKE: couldn't set password, couldn't put password")
        return
    tn.write(password.encode("ascii") + b"\n")

    idx, match, buf = tn.expect([b':'], timeout=3)
    printbytes(buf)
    if match is None:
        print("BROKE: couldn't set password, couldn't put password again")
        return
    tn.write(password.encode("ascii") + b"\n")

    idx, match, buf = tn.expect([b'#'], timeout=3)
    printbytes(buf)
    if match is None:
        print("BROKE: couldn't set password, couldn't enter config")
        return
    tn.write(b"write memory\n")

    idx, match, buf = tn.expect([b'#'], timeout=3)
    printbytes(buf)
    if match is None:
        print("BROKE: couldn't set password, couldn't enter config")
        return
    tn.write(b"exit\n")

    print("password set successfully")

if __name__ == "__main__":
    import sys, json

    if len(sys.argv) < 4:
        print(
            "Syntax: <config_file.json> <config_name> <switch_password> <switch_number>"
        )
        sys.exit()

    scriptFile = open(sys.argv[1], "r")
    config_name = sys.argv[2]
    switch_password = sys.argv[3]
    switch_number = sys.argv[4]
    data = json.loads(scriptFile.read())[config_name]

    switch = Procurve24pConfig(f"172.16.1.1{switch_number}", switch_password, data)
    switch.configure()

