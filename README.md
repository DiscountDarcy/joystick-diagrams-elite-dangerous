# Elite Dangerous Plugin for [Joystick Diagrams](https://github.com/Rexeh/joystick-diagrams)

Parses Elite Dangerous `.binds` files and generates joystick binding diagrams. Current as of Elite: Dangerous 4.2 -- note that this plugin has not yet been tested against the operations update. PRs welcome, or else I will get around to it!

## Features

- Parses Elite Dangerous XML bindings files (`.binds`)
- Generates separate profiles for Flight, SRV, On Foot, and General control schemes
- Friendly human-readable names for 200+ Elite Dangerous bindings
- Auto-detects control scheme from binding name suffixes (`_Buggy`, `_Humanoid`, `_Landing`)

## Installation

Install via URL by pointing joystick-diagrams at the release .zip URL or else copy this plugin folder into your Joystick Diagrams user plugins directory.

## Usage

1. In Joystick Diagrams, select **Elite Dangerous** from the plugin list
2. Browse to your `.binds` file (typically in `%LOCALAPPDATA%\Frontier Developments\Elite Dangerous\Options\Bindings\`)
3. Run the plugin to generate diagrams

## Structure

```
elite_dangerous_plugin/
├── __init__.py          # Plugin package marker
├── main.py              # Plugin entry point (ParserPlugin)
├── elite_dangerous.py   # XML parser and binding resolver
├── img/
│   └── ed.ico           # Plugin icon
└── README.md
```
