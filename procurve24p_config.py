# Procurve is awesome

from telnetlib import Telnet

import string

def printbytes(x):
    #x = x.decode()
    #x = "".join(filter(lambda x: x.isalnum() or x.isspace(), x))
    # TODO: make this print cleanly
    print(x)


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

        output.write(f"; {self.model_id} Configuration Editor; Created on release #Y.11.51\n\n")
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
            bypass_dumb_prompts(tn, self.password)

            #buf = tn.read_until(b"#", timeout=2)
            #if b"#" not in buf:
            #    print("shit broke fam")

            #printbytes(buf)

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
    idx = 1
    while idx >= 0:
        idx, match, buf = tn.expect([b"Password", b"continue", b"Username"], timeout=3)
        print(buf)
        if match is None:
            break
        if match.group(0).lower() == b"username":
            print("username requested. sending 'manager'")
            tn.write(b"manager\n")

        elif match.group(0).lower() == b"continue":
            print("continue requested. sending newline")
            tn.write(b"\n")
            #print("\n\n[WARNING] (SPOOKY) No password configured! you should configure it manually.\n\n")

        elif match.group(0).lower() == b"password":
            print("Authenticating...")
            tn.write(password.encode() + b"\n")
        else:
            print(f"Shit broke my dude, match={match}")
            break


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
