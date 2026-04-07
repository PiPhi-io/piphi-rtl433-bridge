from piphi_rtl433_bridge.config import (
    build_bridge_config,
    build_model_packets_topic,
    build_packet_envelope,
    build_packets_topic,
    load_bridge_config,
    parse_extra_headers,
)


def test_load_bridge_config_parses_command_and_headers(monkeypatch) -> None:
    monkeypatch.setenv("HTTP_FORWARD_ENABLED", "true")
    monkeypatch.setenv("RTL433_COMMAND", "rtl_433 -F json -M time:unix")
    monkeypatch.setenv("RUNTIME_INGEST_URL", "http://runtime.test/ingest/rtl433")
    monkeypatch.setenv("BRIDGE_EXTRA_HEADERS_JSON", '{"X-Test": "true"}')
    monkeypatch.setenv("MQTT_ENABLED", "true")
    monkeypatch.setenv("MQTT_HOSTNAME", "mqtt.test")
    monkeypatch.setenv("MQTT_PORT", "1884")

    config = load_bridge_config()

    assert config.http_forward_enabled is True
    assert config.rtl433_command == ["rtl_433", "-F", "json", "-M", "time:unix"]
    assert config.runtime_ingest_url == "http://runtime.test/ingest/rtl433"
    assert config.extra_headers == {"X-Test": "true"}
    assert config.mqtt_enabled is True
    assert config.mqtt_hostname == "mqtt.test"
    assert config.mqtt_port == 1884


def test_build_bridge_config_uses_explicit_values() -> None:
    config = build_bridge_config(
        http_forward_enabled=False,
        runtime_ingest_url="http://runtime.example/ingest/rtl433",
        rtl433_command_text="rtl_433 -F json -M time:iso",
        forward_timeout_seconds=12.0,
        retry_delay_seconds=4.0,
        startup_delay_seconds=1.5,
        extra_headers_json='{"X-PiPhi":"bridge"}',
        extra_headers={"X-Env": "override"},
        mqtt_enabled=True,
        mqtt_hostname="mqtt.example",
        mqtt_port=2883,
        mqtt_client_id="bridge-1",
        mqtt_qos=1,
        mqtt_topic_root="piphi/sources/rtl433",
    )

    assert config.http_forward_enabled is False
    assert config.runtime_ingest_url == "http://runtime.example/ingest/rtl433"
    assert config.rtl433_command == ["rtl_433", "-F", "json", "-M", "time:iso"]
    assert config.extra_headers == {"X-PiPhi": "bridge", "X-Env": "override"}
    assert config.mqtt_enabled is True
    assert config.mqtt_hostname == "mqtt.example"
    assert config.mqtt_port == 2883
    assert config.mqtt_client_id == "bridge-1"
    assert config.mqtt_qos == 1


def test_parse_extra_headers_returns_empty_dict_for_invalid_json() -> None:
    assert parse_extra_headers("{bad-json") == {}


def test_build_packet_topics_and_envelope() -> None:
    assert build_packets_topic("piphi/sources/rtl433") == "piphi/sources/rtl433/packets"
    assert (
        build_model_packets_topic("piphi/sources/rtl433", "Nexus TH")
        == "piphi/sources/rtl433/models/Nexus_TH/packets"
    )

    envelope = build_packet_envelope(
        {
            "model": "Nexus-TH",
            "id": 42,
            "channel": 1,
        }
    )
    assert envelope["source"] == "rtl433"
    assert envelope["device_hint"]["id"] == "42"
