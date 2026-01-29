# HEMS – Home Energy Management System

HEMS is a Home Assistant integration that dynamically manages
multiple solar inverters and batteries to optimize self-consumption.

## Features

- Multi-inverter support
- Native Home Assistant config flow
- ECO / NORMAL / RECHARGE modes
- Native select entity for mode control
- Battery-aware power distribution
- No cloud dependency

## Installation (HACS)

1. Open HACS
2. Add a custom repository:
    - URL: https://github.com/vachkirit/hems
    - Category: Integration
3. Install "HEMS"
4. Restart Home Assistant
5. Add integration "HEMS" from the UI

## Configuration

All configuration is done through the Home Assistant UI.

## License

MIT

## Information

### Setpoint Modes

#### RECHARGE
All solar production is redirected to the battery.

#### ECO
The setpoint is calculated to prioritize the use of solar energy to cover the energy needs of the house and the electric vehicle.
In this mode, the battery is not used to supply the house.
Any excess solar production is stored in the battery.

#### NORMAL
The setpoint prioritizes the use of solar energy from all inverters to meet the energy needs of the house and the electric vehicle.
The battery is used to compensate for any solar production deficit and the house consumption.
The battery is not used to compensate for electric vehicle charging.
Any excess solar production is stored in the battery.

