from telnetlib import Telnet
from enterasys24p import Enterasys24p
import sys, json

switchFile = open(sys.argv[1], "r")
listSwitchs = json.load(switchFile)

configFile = open(sys.argv[2], "r")
listConfig = json.load(configFile)

for switch in listSwitchs: 
        
        s = None

        with Telnet(switch["ip"]) as tn:

            if switch["model"] == "24p":
                s = Enterasys24p(tn)

            s.authenticate("admin", sys.argv[3])
            print("Connecté au switch "+switch["name"])

            s.beforeVlan()
            
            ports = listConfig[switch["config"]]["ports"]
            for port, config in [(p, ports[p]) for p in ports]:
            
                s.setInterface(port)
                s.setVlanUntagged(config["untagged"])
                s.setNativeVlan(config["untagged"])
                     
                for taggedVlan in config["tagged"]:
                    s.setVlanTagged(taggedVlan)
            
                s.unsetInterface()
            
            s.afterVlan()
            s.saveConfig()
