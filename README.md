# Device Checker

A simple Python script that fetches an HTML page, extracts a table with id "devices", converts it to objects, and checks for new devices compared to a stored list. If new devices are found, it prints to console and updates the stored list.

## Requirements

- Python 3.x
- [uv](https://github.com/astral-sh/uv) package manager
- Install dependencies: `uv sync`

## Usage

First, ensure dependencies are installed by running `uv sync` in the project directory.

Then, run the script:

```
uv run python main.py [--url <URL>] [--file <file_path>]
```

- `--url`: Optional URL of the webpage containing the table with id "devices" (default: https://linux-hardware.org/?view=search&vendor=amd&name=ryzen%205%20150).
- `--file`: Optional path to the JSON file for storing devices (default: `./output/devices.json`).

Example:

```
uv run python main.py
```

The script will:
1. Fetch the HTML from the URL.
2. Parse the table with id "devices".
3. Compare the devices to the existing ones in `./output/devices.json`.
4. If new devices are detected, print to console.
5. Update `./output/devices.json` with the current devices.

## Docker

Build the Docker image:

```
docker build -t linux-hardware-crawler .
```

Run the container (mount the output directory to persist data):

```
docker run --rm -v ./output:/app/output linux-hardware-crawler
```

## Assumptions

- The table has a `<thead>` with headers, or the first row is treated as headers.
- Each row represents a device, and devices are compared by all their fields.
- The first run will create `devices.json` and consider all devices as existing.

## Troubleshooting

- **Table not found**: Ensure the webpage has a `<table id="devices">`.
- **Network errors**: Check your internet connection and the URL.
- **Permission errors**: Ensure write access to the directory for `./output/devices.json`.

## Dependencies

- `requests`: For HTTP requests.
- `beautifulsoup4`: For HTML parsing.