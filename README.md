# FuelWatch WA for Home Assistant

![GitHub release](https://img.shields.io/github/v/release/jamiergrs/fuelwatchwa_ha)

A Home Assistant integration that provides **real-time FuelWatch WA pricing** based on your location.

---

## ✨ Features

- 🚗 Sensors for:
  - Cheapest fuel price
  - Average fuel price
  - Most expensive fuel price
- 📍 Configure **multiple locations** (e.g. home, work, city)
- 🧭 Flexible location options:
  - Home location (`zone.home`)
  - Any Home Assistant zone
  - Custom coordinates (latitude/longitude)
- 🏷️ Clean, automatic sensor naming based on your **location name**
- ⚡ Fast and lightweight

---

## 📦 Installation

### HACS (Recommended)

1. Open **HACS**
2. Click **⋮ → Custom repositories**
3. Add this repository  
   - Category: **Integration**
4. Search for **FuelWatch WA**
5. Click **Download**
6. Restart Home Assistant
7. Go to **Settings → Devices & Services → Add Integration**

---

### Manual Installation

1. Download or clone this repository
2. Copy: custom_components/fuelwatch_ha into your Home Assistant `custom_components` directory
3. Restart Home Assistant
4. Go to **Settings → Devices & Services → Add Integration**

---

## ⚙️ Configuration

When adding a location, you’ll be prompted for:

- **Location name**  
Used to generate sensor names

- **Fuel type**  
(e.g. ULP, Diesel, etc.)

- **Search radius (km)**  
Defines how far to look for fuel stations

- **Location source**

---

### 📍 Location Source Options

Choose how your location is determined:

- **Home location**  
Uses your Home Assistant home (`zone.home`)

- **Zone**  
Select an existing zone (e.g. `zone.work`)

- **Coordinates**  
Enter latitude and longitude manually

---

## 📊 Example Sensors

If you configure a location named **Perth CBD**, you’ll get:

- `sensor.cheapest_fuel_perth_cbd`
- `sensor.average_fuel_perth_cbd`
- `sensor.most_expensive_fuel_perth_cbd`

Cheapest Fuel and Most Expensive Fuel Sensors expose the following attributes to provide more information

- `Station` - Provides the station name i.e Costco Perth Airport
- `Address` - Provides the street address of the station
- `Suburb` - Station Suburb
- `Distance km` - How many KM station is from defined location
  
Average Fuel Sensors provide the number of stations used to calculate the average 
- `Stations count` - i.e 97 Stations 
---

## 🛠️ Development

- Powered by the FuelWatcher API:  
https://github.com/danielmichaels/fuelwatcher

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

If you find a bug or have an idea, feel free to open an issue or PR.

---

## 📄 License

This project is licensed under the MIT License.

---

## ⭐ Support

If you find this integration useful, consider giving it a star on GitHub ⭐
