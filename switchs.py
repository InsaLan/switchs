from telnetlib import Telnet
from enterasys24p import Enterasys24p
from enterasys48p_config import Enterasys48pConfig
from procurve24p_config import Procurve24pConfig
import sys, json

if len(sys.argv) < 4:
    print("Syntax: <switch_file> <config_file> <switch_password>")
    sys.exit()

switchFile = open(sys.argv[1], "r")
listSwitchs = json.load(switchFile)

configFile = open(sys.argv[2], "r")
listConfig = json.load(configFile)

for switch in listSwitchs:
    i = input("Switch {} ({}) : {}, {} \t([g]o/[n]ext/[q]uit)".format(switch["ip"], switch["name"], switch["model"], switch["config"]))
    if i == "q":
        break
    if i != "g":
        continue

    if str(switch["model"]) == "24p-enterasys":
        with Telnet(switch["ip"]) as tn:
            s = Enterasys24p(tn)

            s.authenticate("admin", sys.argv[3])
            print(f"Connected to switch {switch['name']}")

            s.beforeVlan()
            s.activateSnmp("hotlinemontreal")

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

    elif switch["model"] == "48p-enterasys":
        s = Enterasys48pConfig(switch["ip"], sys.argv[3], listConfig[switch["config"]])
        s.configure()

    elif switch["model"] == "24p-procurve":
        s = Procurve24pConfig(switch["ip"], switch["name"], sys.argv[3], switch["model_id"], listConfig[switch["config"]])
        s.configure()

    else:
        print(f"Unsupported switch model \"{switch['model']}\"")
        continue
