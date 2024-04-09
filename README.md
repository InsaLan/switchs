# switchs

This tool sets up the switches used for the InsaLan tournament.

## Configuration

The tool needs two JSON files : 
- `switchs_file`: contains the list of all the switches to configure and
the configuration chosen for each switch
- `configs_file`: describes the configurations to apply (which ports are
tagged/untagged and on which VLANs)

> [!NOTE]
> All configuration files must be in the `/config` directory.

## How to use it?

The main entrypoint is `switchs.py`.
```
usage: switchs.py [-h] [--switch NUMBER] [--new-password PASSWORD] switchs_file configs_file access_password

Configure switches automatically

positional arguments:
  switchs_file          JSON file containing the list of switches
  configs_file          JSON file containing the list of configurations
  access_password       Password to access the switches

options:
  -h, --help            show this help message and exit
  --switch NUMBER, -s NUMBER
                        Switch to configure (by number)
  --new-password PASSWORD, -p PASSWORD
                        New password for the switches (must be at least 8 characters long)
```

For example, if you want to configure the switch number 24 (with IP address `172.16.1.124`), you would run the following command:

```
python3 switchs.py config/switches.json config/config.json password -s 24
```

Run it without `--switch` to be prompted for each switch in the list.

## How it works?


This script detects the model of each switch from the switch file and then automatically calls the right configuration script depending on the model (`enterasys24p`, `enterasys48p`, `procurve24p`...).

`enterasys24p_config` connects via _telnet_ and sends all configuration commands directly through the virtual terminal.  
`enterasys48p_config`, `brocade48p_config` and `procurve24p_config` generate a configuration file locally, place it in the _tftp_ folder, and _then_ connect to the switch via _telnet_ and simply ask the switch to download the configuration file from this very machine with _TFTP_.  
We do that because telnet is unstable and the "basic" way (the `enterasys24p_config` way) often crashed on 48p.

## Configuration template definition

```
{
	"csgo": {
		"ports": {
			"1-24": {
				"untagged": 101,
				"tagged": []
			},

			"25": {
				"untagged": 1,
				"tagged": [ 101 ]
			}
		}
	},

	"tft": {
		"ports": {
			"1-24": {
				"untagged": 104,
				"tagged": []
			},

			"25": {
				"untagged": 1,
				"tagged": [ 104 ]
			}
		}
	},
	...
}
```
