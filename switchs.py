#!/usr/bin/env python3
from telnetlib import Telnet
from enterasys24p_config import enterasys24p_config
from enterasys48p_config import enterasys48p_config
from procurve24p_config import procurve24p_config
from brocade48p_config import brocade48p_config
import json
import argparse
import sys

def configure_switch(switch, config, access_password, new_password):
    print(f"Configuring switch {switch['name']} ({switch['ip']})")
    if str(switch["model"]) == "24p-enterasys":
        enterasys24p_config(switch, config, access_password, new_password)

    elif switch["model"] == "48p-enterasys":
        enterasys48p_config(switch, config, access_password, new_password)

    elif switch["model"] == "48p-brocade":
        brocade48p_config(switch, config, access_password, new_password)

    elif switch["model"] == "24p-procurve":
        procurve24p_config(switch, config, access_password, new_password)

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
        "--new-password", "-p", help="New password for the switches (must be at least 8 characters long)", metavar="PASSWORD"
    )

    args = parser.parse_args()

    with open(args.switchs_file, "r") as f:
        listSwitchs = json.load(f)

    with open(args.configs_file, "r") as f:
        listConfig = json.load(f)
    
    if args.new_password is None:
        args.new_password = args.access_password
    elif len(args.new_password) < 8:
        print("Error : new password must be at least 8 characters long.")
        sys.exit()

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
