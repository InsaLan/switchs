import telnetlib

class Enterasys48p:
    
    def __init__(self, tn):
        self.telnet = tn

    def authenticate(self, username, password):
        print("authenticating")
        self.telnet.read_until(b"Username:")
        self.telnet.write(username.encode()+b"\n")
        self.telnet.read_until(b"Password:")
        self.telnet.write(password.encode()+b"\n")
        self.waitForPrompt()
    
    def waitForPrompt(self):
        #print(self.telnet.read_until(b"->")) # <-- print feedback from the switch
        self.telnet.read_until(b"->")

    def beforeVlan(self):
        pass

    def setInterface(self, selector):
        pass

    def clearVlan(self, selector, vlan):
        # don't clear vlan on upstream, otherwise we loose the connection to the switch
        if not "ge" in selector:
            self.telnet.write(b"clear vlan egress " + str(vlan).encode() + b" " + str(selector).encode() + b"\n")
            self.waitForPrompt()                                                                                                  
            self.telnet.write(b"clear vlan "+str(vlan).encode()+b"\n")
            self.waitForPrompt()

    def setVlanUntagged(self, selector, vlan):
        self.clearVlan(selector, vlan)

        self.telnet.write(b"set vlan create " + str(vlan).encode() + b"\n")
        self.waitForPrompt()

        self.telnet.write(b"set vlan egress " + str(vlan).encode() + b" " + str(selector).encode() + b" untagged\n")
        
        self.waitForPrompt()

    def setVlanTagged(self, selector, vlan):
        self.clearVlan(selector, vlan)

        self.telnet.write(b"set vlan create " + str(vlan).encode() + b"\n")
        self.waitForPrompt()

        self.telnet.write(b"set vlan egress " + str(vlan).encode() + b" " + str(selector).encode() + b" tagged\n")

        self.waitForPrompt()

    def setNativeVlan(self, selector, vlan):
        self.telnet.write(b"set port vlan " + str(selector).encode() + b" " + str(vlan).encode() + b" modify-egress\n")
        self.waitForPrompt()

    def unsetInterface(self):
        pass

    def afterVlan(self):
        pass

    def saveConfig(self):
        self.telnet.write(b"save config\n")
        self.waitForPrompt()

    def activateSnmp(self, community):
        self.beforeVlan()
        self.telnet.write(b"set snmp community "+community+" securityname "+community+"\n")
        self.waitForPrompt()
        self.telnet.write(b"set snmp access "+community+" security-model v2c read All notify All nonvolatile\n")
        self.waitForPrompt()
        self.telnet.write(b"set snmp group public user "+community+" security-model v2c nonvolatile\n") 
        self.waitForPrompt()
