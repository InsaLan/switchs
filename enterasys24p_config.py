from telnetlib import Telnet

def wait_for_prompt(tn):
	print(tn.read_until(b"#")) # <-- print feedback from the switch

def enterasys24p_config(switch, config, access_password, new_password):
	with Telnet(switch["ip"]) as tn:
	
		tn.read_until(b"Username:")
		tn.write(b"admin\n")
		tn.read_until(b"Password:")
		tn.write(access_password.encode()+b"\n")
		wait_for_prompt(tn)
	
		tn.write(b"configure\n")
		wait_for_prompt(tn)

		tn.write(b"username admin password 0 "+new_password+"\n")
		wait_for_prompt(tn)
		
		tn.write(b"snmp-server\n")
		wait_for_prompt()
		tn.write(b"snmp-server community hotlinemontreal ro\n")
		wait_for_prompt(tn)
		
		ports = config["ports"]
		for port, config in [(p, ports[p]) for p in ports]:
			tn.write(b"interface ethernet 1/" + port.encode() + b"\n")
			wait_for_prompt(tn)
			
			tn.write(b"switchport native vlan 1\n") # Clear VLANs
			tn.write(b"no switchport allowed vlan\n")
			wait_for_prompt(tn)
			tn.write(b"switchport allowed vlan add " + str(config["untagged"]).encode() + b" untagged\n")
			wait_for_prompt(tn)
			
			tn.write(b"switchport native vlan " + str(config["untagged"]).encode() + b"\n")
			wait_for_prompt()
			
			for tagged_vlan in config["tagged"]:
				tn.write(b"switchport allowed vlan add " + str(tagged_vlan).encode() + b" tagged\n")
				wait_for_prompt(tn)
			
			tn.write(b"exit\n")
			wait_for_prompt(tn)
		
		tn.write(b"end\n")
		wait_for_prompt(tn)
		
		print("saving configuration")
		tn.write(b"copy running-config startup-config\n")
		tn.read_until(b"[startup]")
		tn.write(b"\n")
		wait_for_prompt(tn)
