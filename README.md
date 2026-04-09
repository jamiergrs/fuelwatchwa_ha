# FuelWatch WA HA

Custom Home Assistant integration for FuelWatch WA pricing.

## Features

- Creates `cheapest`, `average`, and `most_expensive` fuel sensors.
- Supports multiple config entries.
- Lets each entry use either:
  - `zone.home`
  - another Home Assistant zone
  - explicit latitude/longitude coordinates
- Uses the entry name in the entity ID suggestion, so names like `Perth CBD` become entities such as `sensor.average_fuel_perth_cbd`.

## Installation

### HACS

1. In HACS, add this repository as a custom repository.
2. Choose category `Integration`.
3. Install `FuelWatch WA HA`.
4. Restart Home Assistant.
5. Add the integration from Settings > Devices & services.

### Manual

1. Copy `custom_components/fuelwatch_ha` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Add the integration from Settings > Devices & services.

## Configuration

Each config entry asks for:

- a friendly name
- fuel type
- radius in kilometers
- a location source

Location source can be:

- `home_zone`: uses `zone.home`
- `zone`: uses a named zone such as `work` or an entity ID such as `zone.work`
- `coordinates`: uses explicit latitude/longitude

## Brand Images

Home Assistant 2026.3 and newer support local integration brand assets inside:

`custom_components/fuelwatch_ha/brand/`

Add at least:

- `icon.png`
- `logo.png`

Optional dark-mode variants:

- `icon_dark.png`
- `logo_dark.png`

## Development

- Dependency: `fuelwatcher==1.0.0`
- Integration version: `1.1.0`
