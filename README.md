# piphi-rtl433-bridge

Small bridge process that runs `rtl_433`, reads decoded JSON packets, and
forwards them to a PiPhi runtime such as `piphi-network-433mhz`.

## Why this project exists

`rtl_433` is already very good at radio decoding.

PiPhi still needs a tiny adapter layer that can:

- run `rtl_433`
- read one JSON packet at a time
- forward packets to the runtime endpoint
- retry if the runtime is temporarily unavailable
- keep the main runtime simpler and more beginner-friendly

That is what this bridge does.

## Mental model

- `rtl_433` is the radio decoder
- this bridge is the adapter
- the main PiPhi runtime is the integration brain

The bridge does not publish PiPhi telemetry itself.
It only forwards decoded packets to the runtime's `/ingest/rtl433` route.

It can also publish the same decoded packets to shared MQTT source topics so
multiple integrations can subscribe without fighting over the SDR device.

## Environment variables

- `RUNTIME_INGEST_URL`
  Default: `http://127.0.0.1:8090/ingest/rtl433`
- `HTTP_FORWARD_ENABLED`
  Default: `true`
- `RTL433_COMMAND`
  Default: `rtl_433 -F json`
- `FORWARD_TIMEOUT_SECONDS`
  Default: `10`
- `RETRY_DELAY_SECONDS`
  Default: `5`
- `STARTUP_DELAY_SECONDS`
  Default: `2`
- `BRIDGE_EXTRA_HEADERS_JSON`
  Optional JSON object of extra headers to send with each forwarded packet
- `MQTT_ENABLED`
  Default: `false`
- `MQTT_HOSTNAME`
  Default: `127.0.0.1`
- `MQTT_PORT`
  Default: `1883`
- `MQTT_USERNAME`
  Optional username
- `MQTT_PASSWORD`
  Optional password
- `MQTT_CLIENT_ID`
  Optional client identifier
- `MQTT_QOS`
  Default: `0`
- `MQTT_TOPIC_ROOT`
  Default: `piphi/sources/rtl433`

## Local development

Install dependencies:

```bash
pdm install -G dev
```

Run the bridge:

```bash
pdm run bridge run
```

Print the resolved bridge config without starting anything:

```bash
pdm run bridge print-config
```

Ping the runtime ingest endpoint:

```bash
pdm run bridge ping-runtime
```

Example custom run command:

```bash
pdm run bridge run \
  --runtime-ingest-url "http://127.0.0.1:8090/ingest/rtl433" \
  --rtl433-command "rtl_433 -F json -M time:unix" \
  --header "X-PiPhi-Bridge=true" \
  --log-level DEBUG
```

MQTT-only collector mode:

```bash
pdm run bridge run \
  --no-http-forward-enabled \
  --mqtt-enabled \
  --mqtt-hostname "127.0.0.1" \
  --mqtt-topic-root "piphi/sources/rtl433"
```

Dry run without launching `rtl_433`:

```bash
pdm run bridge run --dry-run
```

You can still use environment variables if you prefer:

```bash
RUNTIME_INGEST_URL="http://127.0.0.1:8090/ingest/rtl433" \
RTL433_COMMAND="rtl_433 -F json -M time:unix" \
pdm run bridge run
```

## Docker

Build:

```bash
docker build -t piphi-rtl433-bridge .
```

Run:

```bash
docker run --rm \
  --network host \
  --privileged \
  --device /dev/bus/usb:/dev/bus/usb \
  -e RUNTIME_INGEST_URL="http://127.0.0.1:8090/ingest/rtl433" \
  piphi-rtl433-bridge
```

If you want to inspect the SDR device inside the container while debugging, `usbutils` is included so you can run:

```bash
docker run --rm \
  --network host \
  --privileged \
  --device /dev/bus/usb:/dev/bus/usb \
  piphi-rtl433-bridge lsusb
```

## Notes

- This bridge is Linux-first because `rtl_433` sidecar containers fit that path best.
- The bridge keeps retrying packet delivery if the runtime is temporarily unavailable.
- If you later add auth between the helper and runtime, use `BRIDGE_EXTRA_HEADERS_JSON`.
- The image includes `rtl_433`, `rtl-sdr`, `usbutils`, and `tini` so it is better suited for real RTL-SDR helper use.

## MQTT Topic Contract

When MQTT publishing is enabled, the bridge publishes:

- all decoded packets to `piphi/sources/rtl433/packets`
- model-specific packets to `piphi/sources/rtl433/models/<model>/packets`

Each MQTT message is a JSON envelope with:

- `source`
- `received_at`
- `model`
- `device_hint`
- `packet`
