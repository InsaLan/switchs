# switchs

This tool sets up the switches used for the InsaLan tournament.

## Configuration

The tool needs two JSON files : the first one defines configuration templates and the second one gives the list of all the switches to configure along with their configuration template.

> [!NOTE]
> All configuration files must be in the `/config` directory.

## How it works?

The main entrypoint is `switchs.py`: you call it with `python3 switchs.py <switch_file> <config_file> <switch_password>`.  
This script detects the model of each switch from the switch file and then automatically calls the right configuration script depending on the model (`enterasys24p`, `enterasys48p`, `procurve24p`...).

`enterasys24p` connects via _telnet_ and sends all configuration commands directly through the virtual terminal.  
`enterasys48p_config` and `procurve24p_config` generate a configuration file locally, place it in the _tftp_ folder, and _then_ connect to the switch via _telnet_ and simply ask the switch to download the configuration file from this very machine with _TFTP_.  
We do that because telnet is unstable and the "basic" way (the `enterasys24p` way) often crashed on 48p.

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
