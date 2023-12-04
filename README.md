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
`switch` | Switch to toggle various charger modes.
`select` | Select the ampers limit and service level.

## Installation via HACS (recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=firstof9&repository=openevse)

1. Follow the link [here](https://hacs.xyz/docs/faq/custom_repositories/)
2. Use the custom repo link https://github.com/firstof9/openevse
3. Select the category type `integration`
4. Then once it's there (still in HACS) click the INSTALL button
5. Restart Home Assistant
6. Once restarted, in the HA UI go to `Configuration` (the ⚙️ in the lower left) -> `Devices and Services` click `+ Add Integration` and search for `openevse`

## Manual (non-HACS)
<details>
<summary>Instructions</summary>
  
<br>
You probably do not want to do this! Use the HACS method above unless you know what you are doing and have a good reason as to why you are installing manually
<br>
  
1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `openevse`.
4. Download _all_ the files from the `custom_components/openevse/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. Once restarted, in the HA UI go to `Configuration` (the ⚙️ in the lower left) -> `Devices and Services` click `+ Add Integration` and search for `openevse`
</details>

## Configuration is done in the UI

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

## TODO

- [ ] Add tests
- [x] Current
- [x] Voltage
- [x] Power
- [x] Session Energy
- [x] Total Energy
- [x] Status
- [x] Temps
- [x] Vehicle connected
- [x] Rssi
- [x] Max current
- [x] Charge current
- [X] Manual Override
- [ ] Schedule
- [X] Divert mode
- [X] Auto discovery
- [x] Setup via Home Assistant UI
- [x] Real time updates via web socket
- [x] Support energy integration
- [x] Use newer OpenEVSE APIs


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
