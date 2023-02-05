import telnetlib

class Enterasys24p:
    
    def __init__(self, tn):
        self.telnet = tn

    def authenticate(self, username, password):
        self.telnet.read_until(b"Username:")
        self.telnet.write(username.encode()+b"\n")
        self.telnet.read_until(b"Password:")
        self.telnet.write(password.encode()+b"\n")
        self.waitForPrompt()
    
    def waitForPrompt(self):
        print(self.telnet.read_until(b"#")) # <-- print feedback from the switch
        #self.telnet.read_until(b"#")

    def clearVlan(self, selector, vlan):
        self.telnet.write(b"switchport native vlan 1\n")
        self.telnet.write(b"no switchport allowed vlan\n")
        self.waitForPrompt()

    def beforeVlan(self, upstream_nb=0):
        self.telnet.write(b"configure\n")
        self.telnet.write(b"interface ethernet 1/1-"+str(22+upstream_nb).encode()+b"\n")
        self.telnet.write(b"no switchport allowed vlan\n")
        self.waitForPrompt()

    def setInterface(self, selector):
        self.telnet.write(b"interface ethernet 1/" + selector.encode() + b"\n")
        self.waitForPrompt()

    def setVlanUntagged(self, selector, vlan):
        self.clearVlan(selector, vlan)
        self.telnet.write(b"switchport allowed vlan add " + str(vlan).encode() + b" untagged\n")
        self.waitForPrompt()

    def setVlanTagged(self, selector, vlan):
        # self.clearVlan(selector, vlan) # DO NOT CLEAR OTHER VLANS
        self.telnet.write(b"switchport allowed vlan add " + str(vlan).encode() + b" tagged\n")
        self.waitForPrompt()

    def setNativeVlan(self, selector, vlan):
        self.telnet.write(b"switchport native vlan " + str(vlan).encode() + b"\n")
        self.waitForPrompt()

    def unsetInterface(self):
        self.telnet.write(b"exit\n")
        self.waitForPrompt()

    def afterVlan(self):
        self.telnet.write(b"end\n")
        self.waitForPrompt()

    def saveConfig(self):
        print("saving configuration")
        self.telnet.write(b"copy running-config startup-config\n")
        self.telnet.read_until(b"[startup]")
        self.telnet.write(b"\n")
        self.waitForPrompt()

    def activateSnmp(self, community):
        self.beforeVlan()
        self.telnet.write(b"snmp-server\n")
        self.waitForPrompt()
        self.telnet.write(b"snmp-server community "+str(community).encode()+b" ro\n")
        self.waitForPrompt()
