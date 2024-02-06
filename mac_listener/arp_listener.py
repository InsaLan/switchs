#!/bin/python3
import subprocess
import re
import time
import csv

allowed_ifaces = ["eno2.1@eno2", "wlp0s20f3", "eno2.1", "eno2.150"]
models = ["Enterasys 24p", "Enterasys 48p", "Enterasys 50p", "ProCurve"]
models_help = ", ".join([f"{model_id}: {models[model_id]}" for model_id in range(len(models))])
output_filename = "output.txt"
periodic_table = {}
arp_row_pattern = re.compile(r"^((?:[0-9]{1,3}\.){3}[0-9]{1,3})\s+\w+\s+((?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2}))\s+\w+\s+([\w.]+)$")

known_macs = []

with open("periodic_table.csv", newline='') as periodic_csv:
    periodic_csv.readline()
    periodic_reader = csv.reader(periodic_csv)
    for row in periodic_reader:
        periodic_table[int(row[0])] = row[1]

def parse_row(row):
    row_match = arp_row_pattern.match(row)
    # little regex to directly get what we want (ip address, mac and interface) from the arp row
    # it will also automatically filter out not full lines
    return None if row_match == None else {"ip": row_match.group(1), "mac": row_match.group(2), "iface": row_match.group(3)}

def new_device(row):
    print("Found new device: " + str(row))

    prompt = input("Do you want to add this device as a switch? (y/n) ")
    if prompt.lower() == "y":
        id = int(input("Which number is it? "))

        model_id = input(f"Which model is it? {models_help} ")
        try:
            model = models[int(model_id)]
        except:
            model = ""

        confline = f"dhcp-host=management,{row['mac']},172.16.1.{100 + id} # {model} - {periodic_table[id]}"

        with open(output_filename, "a") as output_file:
            output_file.write(confline + "\n")
            # it will get added at the end of the file as we opened it with mode "a"
        
        print(f"Added {confline}")

def filter_device(row):
    if row["mac"] in known_macs:
        return False
    if row["iface"] not in allowed_ifaces:
        print(f"Dropped {row['ip']} ({row['mac']}) : wrong interface ({row['iface']})")
        return False
    return True

def read_arp(first_run = False):
    arp_rows = subprocess.run(["arp", "-n"], stdout=subprocess.PIPE).stdout.decode("utf-8").split("\n")
    arp_rows.pop(0) # we remove the first row which is column names
    # it's not exactly csv so we cannot get it easily :(

    arp_rows = [parse_row(row) for row in arp_rows]
    arp_rows = [row for row in arp_rows if row != None]
    
    added = False
    for row in arp_rows:
        if not first_run and filter_device(row):
            new_device(row)
            added = True
        known_macs.append(row["mac"])
    
    return added
    
read_arp(first_run=True)
# we run it one first time to fill the "known_macs" list with all already connected devices

while True:
    time.sleep(1) # we wait 1 second not to fetch arp too frequently and overload the cpu
    if read_arp():
        print("Waiting for more...\n")
