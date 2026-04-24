# data-engineering-project-playground

The motivation behind this mock project is to have simple yet complicated enough project in which DE skills improved.
The idea, is to have a project in which you can practice:
- batch spark
- spark streaming
- traditional programming
- streaming/batch pipeline in non-spark technology
- etc
Also, idea is to have somewhat real world project in which you could compare different approaches and compare the dimension like cost, speed, complexity, etc

The device itself does not exist it is completely made up.

# Introduction
You are an data engineer who is tasked to design and implement the data pipeline which will process the data from the device that measures the environmental dimensions like temperature. More about the device itself we will dive in in the coming sections.

You have complete control of the technology stack as long as you are within the budget (that you set) and you delivered the deliverables (later will be explained).

# Device
The data is coming from the device that measures the environmental dimensions.
The device itself is the "state of the art" which can measure in 3D space.
The dimensions the device can measure are:
- Temperature
- Humidity
- Co2
- Ozone
- Nitrogen Dioxide
- Barometric Pressure
- Solar Radiation
- Salinity
- PH
- Amount of plastic that where the size is between xx and zz

We have an technology which can measure all dimensions mentioned above.
Also, some newer devices can measure then 10 meter horizontally/vertically/dept from the device itself.
Devices are deployed in the fleets of 100, in grid of 20m by 20m. In each fleet we have an "flagship" device, which is the most powerful device that could emit storing enough signal so we can collect if wherever the fleet is in the pacific ocean.

Each device has the following components:
- Solar panel
- Battery
- Computer
- Antenna/RF components
- Measuring sensors (for each dimension listed above)

For each of these component we have data to measure the efficiency of said component.
Also, we have multiple generations of these devices as well as multiple firmware versions. The newer the generation, the more datapoint device can measure.

Since we use RF to transfer the data from flagship device to the backend, the payload is design to be efficient as possible. Which means everything is in binary format.
The binary format specification for each firmware version you can [here](#Binary-format-specification).

# Backend
On the receiving end or collector side, we have setup simple backend that receives the data from RF channel and calculates the checksum of given data and pushes it to the queue.

# Requirements-of-pipeline
You job is to design and implement the pipeline that accommodates the following requirements:
- We want to know how many devices are malfunctioning. Malfunctioning could be one of the following:
	- Battery health is not good
	- Energy produced is not sufficient
	- No data is coming from device/fleet
	- Data loss is more that 40% (40% of data per device/fleet is missing)
- We want to be able to calculate the min/max/mean/median/ for each dimension over time (per day/month/year)
- Table should be modeled in such way that we can support various visualization (e.g. see on. the map where the fleet is, visualize each data point and ranges, etc)
- The access to this data should be done in such way that we can easily export it to the interested third party

# Deliverables
You are in the complete control what deliverables you can deliver based on this data.
Suggestions of the following:
- dashboard to measure the efficiency of the battery/solar panel
- dataset of all the dimensions so it can be used for dimension prediction e.g. model that could predict the temperature in XX years
- etc

# CLI for generating mock data
Like we said is before, nothing of this is real. So we have created an CLI which can generate the mock data.

## Usage

```bash
# Validate config and print it
uv run python main.py --config config/sample.yaml --validate-config

# Run the generator
uv run python main.py --config config/sample.yaml
```

All configuration comes from the YAML config file (`--config` is required). There are no CLI flag overrides.

## CLI flags

| Flag | Required | Description |
|---|---|---|
| `--config PATH` | Yes | Path to the YAML configuration file |
| `--validate-config` | No | Validate and print the config, then exit |

## Config file parameters

- `output-format`:
	- `json`
	- `json-with-binary-payload`
	- `xml`
	- `xml-with-binary-payload`
	- `csv`
	- `csv-with-binary-payload`
	- `avro`
	- `avro-with-binary-payload`
- `output-type`:
	- `kafka-only`
	- `rabbitmq-only`
	- `s3-only`
	- `s3-with-kafka`
	- `s3-with-rabbitmq`
- `number-of-devices-per-fleet`: positive integer
- `number-of-fleets`: positive integer
- `dimensions`: for which data will be generated
	- `all`
	- list of dimension strings — valid values: `temperature`, `humidity`, `co2`, `ozone`, `nitrogen-dioxide`, `barometric-pressure`, `solar-radiation`, `salinity`, `ph`, `plastics`, `cpu-temperature`, `cpu-utilization`, `battery-temperature`, `battery-percentage-level`, `current-voltage`, `current-amp`
- `rate-of-emitting-dp`:
	- `1-per-second`
	- `10-per-second`
	- `1-per-minute`
	- `10-per-minute`
	- `1-per-hour`
	- `10-per-hour`
- `error-rate` *(optional)*: nested mapping of component → dimension → rate. Valid components: `sensors`, `computer`, `battery`, `solar-panel`. Valid rates: `0.0`, `0.1`, `0.25`, `0.5`, `0.75`, `1.0`. Omit the key entirely to inject no errors.

Example:
```yaml
error-rate:
  sensors:
    temperature: 0.1
    humidity: 0.25
  computer:
    cpu-temperature: 0.5
```

# Binary-format-specification
When the output is chosen in the binary format, the following will be the specification.
This is WIP, but it will be something like this:
- 1 byte => format version
- 1 byte => fw_version
- 1 byte => device id
- 1 byte => battery_level
- 1 byte => CPU utilization
- 1 byte => CPU temperature
- 1 byte => battery level
- ...
- the data itself
- 1 byte => number of datapoints
- value for each dimensions is repeated for each data point
- ...
- 1 byte => checksum
