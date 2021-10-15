# OpenEVSE

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

_Component to integrate with [OpenEVSE][openevse] chargers._

**This component will set up the following platforms.**

Platform | Description
-- | --
`sensor` | Show info from an OpenEVSE charger's API.
`switch` | Switch to toggle "Sleep Mode".


## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `openevse`.
4. Download _all_ the files from the `custom_components/openevse/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "openevse"


## Configuration is done in the UI

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[openevse]: https://openevse.com/
[integration_blueprint]: https://github.com/firstof9/openevse
[buymecoffee]: https://www.buymeacoffee.com/firstof9
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/firstof9/openevse.svg?style=for-the-badge
[commits]: https://github.com/firstof9/openevse/commits/main
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/firstof9/openevse.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Chris%20Nowak%20%40firstof9-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/firstof9/openevse.svg?style=for-the-badge
[releases]: https://github.com/firstof9/openevse/releases
