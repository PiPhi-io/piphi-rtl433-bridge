from piphi_rtl433_bridge.bridge import parse_packet_line


def test_parse_packet_line_accepts_json_object() -> None:
    packet = parse_packet_line(b'{"model":"Nexus-TH","id":42,"temperature_C":21.5}\n')

    assert packet is not None
    assert packet["model"] == "Nexus-TH"
    assert packet["id"] == 42


def test_parse_packet_line_rejects_non_json() -> None:
    assert parse_packet_line("not-json") is None
