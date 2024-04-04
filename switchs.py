#!/usr/bin/env python3
from telnetlib import Telnet
from enterasys24p import Enterasys24p
from enterasys48p_config import Enterasys48pConfig
from procurve24p_config import procurve24p_config
from brocade48p_config import brocade48p_config
import json
import argparse


def configure_switch(switch, config, access_password, new_password):
    print(f"Configuring switch {switch['name']} ({switch['ip']})")
    if str(switch["model"]) == "24p-enterasys":
        with Telnet(switch["ip"]) as tn:
            s = Enterasys24p(tn)

            s.authenticate("admin", access_password)
            print(f"Connected to switch {switch['name']}")

            s.beforeVlan()
            s.activateSnmp("hotlinemontreal")

            ports = config["ports"]
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
        s = Enterasys48pConfig(switch["ip"], access_password, config)
        s.configure()

    elif switch["model"] == "48p-brocade":
        brocade48p_config(switch, config, access_password)

    elif switch["model"] == "24p-procurve":
        procurve24p_config(switch, config, access_password)

    else:
        print(f"Unsupported switch model \"{switch['model']}\"")


def main():
    parser = argparse.ArgumentParser(description="Configure switches automatically")

    parser.add_argument(
        "switchs_file", help="JSON file containing the list of switches"
    )
    parser.add_argument(
        "configs_file", help="JSON file containing the list of configurations"
    )
    parser.add_argument("access_password", help="Password to access the switches")
    parser.add_argument(
        "--switch", "-s", help="Switch to configure (by number)", metavar="NUMBER"
    )
    parser.add_argument(
        "--new-password", "-p", help="New password for the switches", metavar="PASSWORD"
    )

    args = parser.parse_args()

    with open(args.switchs_file, "r") as f:
        listSwitchs = json.load(f)

    with open(args.configs_file, "r") as f:
        listConfig = json.load(f)

    if args.switch is not None:
        switch_ip = f"172.16.1.1{args.switch.zfill(2)}"
        switch = list(filter(lambda x: x["ip"] == switch_ip, listSwitchs))[0]
        config = listConfig[switch["config"]]
        configure_switch(switch, config, args.access_password, args.new_password)
    else:
        for switch in listSwitchs:
            i = input(
                f"Switch {switch['ip']} ({switch['name']}) : {switch['model']}, {switch['config']} \t([g]o/[n]ext/[q]uit)"
            )
            if i == "q":
                break
            if i == "g":
                configure_switch(
                    switch,
                    listConfig[switch["config"]],
                    args.access_password,
                    args.new_password,
                )


if __name__ == "__main__":
    main()
