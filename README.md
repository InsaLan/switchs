# switchs

This tool sets up the switches used for the InsaLan tournament.

## Configuration

The tool needs two JSON files : the first one defines configuration templates and the second one gives the list of all the switches to configure along with their configuration template.

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
