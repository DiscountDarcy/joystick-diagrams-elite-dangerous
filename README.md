# Elite Dangerous Plugin for [Joystick Diagrams](https://github.com/Rexeh/joystick-diagrams)

Parses Elite Dangerous `.binds` files and generates joystick binding diagrams.

## Features

- Parses Elite Dangerous XML bindings files (`.binds`)
- Generates separate profiles for Flight, SRV, On Foot, and General control schemes
- Friendly human-readable names for 200+ Elite Dangerous bindings
- Auto-detects control scheme from binding name suffixes (`_Buggy`, `_Humanoid`, `_Landing`)

## Installation

Copy this plugin folder into your Joystick Diagrams user plugins directory.

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
