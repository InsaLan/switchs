from telnetlib import Telnet
from enterasys24p import Enterasys24p
from enterasys48p import Enterasys48p
import sys, json

switchFile = open(sys.argv[1], "r")
listSwitchs = json.load(switchFile)

configFile = open(sys.argv[2], "r")
listConfig = json.load(configFile)

for switch in listSwitchs: 
        
        s = None
        i = input("next switch {} ([g]o/[n]ext)".format(switch["ip"]))
        if i == "n":
            continue

        with Telnet(switch["ip"]) as tn:

            if switch["model"] == "24p":
                s = Enterasys24p(tn)

            elif switch["model"] == "48p":
                s = Enterasys48p(tn)

            s.authenticate("admin", sys.argv[3])
            print("Connecté au switch "+switch["name"])
            
            s.activateSnmp("hotlinemontreal")

            s.beforeVlan()
            
            ports = listConfig[switch["config"]]["ports"]
            for port, config in [(p, ports[p]) for p in ports]:
            
                s.setInterface(port)
                s.setVlanUntagged(port, config["untagged"])
                s.setNativeVlan(port, config["untagged"])
                     
                for taggedVlan in config["tagged"]:
                    s.setVlanTagged(port, taggedVlan)
            
                s.unsetInterface()
            
            s.afterVlan()
            s.saveConfig()
