# Procurve is awesome

from telnetlib import Telnet


class Procurve24pConfig:
    def __init__(self, ip, password, data):
        self.ip = ip
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
        # output = open("/var/tftp/" + tmpConfigName, "w")
        output = open("" + tmpConfigName, "w")

        # TODO put something here
        hostname = "script configured switch"
        output.write(f'hostname "{hostname}"\n')
        output.write('snmp-server community "hotlinemontreal" Unrestricted\n')

        for vlan in vlans:
            output.write("vlan {}\n".format(vlan))
            output.write(f"  name vlan{vlan}\n")
            output.write(f"  ip address dhcp-bootp\n")
            for port_range, data in ports.items():
                if data["untagged"] == vlan:
                    output.write(f"  untagged {port_range}\n")
                elif vlan in data["tagged"]:
                    output.write(f"  tagged {port_range}\n")
            output.write("  exit\n")

        output.write("password manager\n")

        output.close()

        print("Done creating config")

        # 4 - we send the config!

        tftp_server_ip = "172.16.1.1"

        with Telnet(self.ip) as tn:
            print("Authenticating...")
            tn.read_until(b"Password:")
            tn.write(self.password.encode() + b"\n")
            tn.read_until(b"#")

            print(f"Copying config from {tftp_server_ip}...")
            tn.write(
                b"copy tftp startup-config "
                + tftp_server_ip.encode()
                + b" "
                + tmpConfigName.encode()
                + b"\n"
            )
            tn.read_until(b"Device may be rebooted, do you want to continue [y/n]?")
            tn.write(b"y")

        print("Done!")


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

