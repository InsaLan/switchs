import telnetlib

class Enterasys24p:
    
    def __init__(self, tn):
        self.telnet = tn

    def authenticate(self, username, password):
        self.telnet.read_until(b"Username:")
        self.telnet.write(username+b"\n")
        self.telnet.read_until(b"Password:")
        self.telnet.write(password+b"\n")
        self.waitForPrompt()
    
    def waitForPrompt(self):
        self.telnet.read_until(b"#")

    def beforeVlan(self):
        self.telnet.write(b"configure")
        self.waitForPrompt()

    def setInterface(self, selector):
        self.telnet.write(b"interface ethernet 1/" + selector.encode() + b"\n")
        self.waitForPrompt()

    def setVlanUntagged(self, vlan):
        self.telnet.write(b"switchport allowed vlan add " + str(vlan).encode() + b" untagged\n")
        self.waitForPrompt()

    def setVlanTagged(self, vlan):
        self.telnet.write(b"switchport allowed vlan add " + str(vlan).encode() + b" tagged\n")
        self.waitForPrompt()

    def setNativeVlan(self, vlan):
        self.telnet.write(b"switchport native vlan " + str(vlan).encode() + b"\n")
        self.waitForPrompt()

    def unsetInterface(self):
        self.telnet.write(b"exit\n")
        self.waitForPrompt()

    def afterVlan(self):
        self.telnet.write(b"end\n")
        self.waitForPrompt()

    def saveConfig(self):
        self.telnet.write(b"copy running-config startup-config\n")
        self.telnet.read_until(b"[startup]")
        self.telnet.write(b"\n")
        self.telnet.waitForPrompt()
