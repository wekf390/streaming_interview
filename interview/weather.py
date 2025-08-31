from typing import Any, Iterable, Generator, Dict

def process_events(
    events: Iterable[Dict[str, Any]]
) -> Generator[Dict[str, Any], None, None]:
    station_data: Dict[str, Dict[str, float]] = {}
    last_ts = None
    for event in events:
        msg_type = event.get("type")
        if msg_type == "sample":
            ts = event["timestamp"]
            temp = event["temperature"]
            name = event["stationName"]
            last_ts = ts
            if name not in station_data:
                station_data[name] = {"high": temp, "low": temp}
            else:
                if temp > station_data[name]["high"]:
                    station_data[name]["high"] = temp
                if temp < station_data[name]["low"]:
                    station_data[name]["low"] = temp
        elif msg_type == "control":
            cmd = event.get("command")
            if cmd == "snapshot":
                if last_ts is None:
                    continue
                stations_out: Dict[str, Dict[str, float]] = {}
                for sname, extremes in station_data.items():
                    stations_out[sname] = {
                        "high": extremes["high"],
                        "low": extremes["low"]
                    }
                yield {
                    "type": "snapshot",
                    "asof": last_ts,
                    "stations": stations_out
                }
            elif cmd == "reset":
                if last_ts is None:
                    continue
                yield {
                    "type": "reset",
                    "asof": last_ts
                }
                station_data.clear()
                last_ts = None
            else:
                raise Exception("Please verify input")
        else:
            raise Exception("Please verify input")
