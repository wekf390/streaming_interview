import pytest
from . import weather

def test_empty_stream():
    assert [] == list(weather.process_events([]))


def test_single_station_snapshot_and_reset():
    events = [
        {"type": "sample", "stationName": "A", "timestamp": 1, "temperature": 10.0},
        {"type": "sample", "stationName": "A", "timestamp": 2, "temperature": 12.0},
        {"type": "control", "command": "snapshot"},
        {"type": "sample", "stationName": "A", "timestamp": 3, "temperature":  9.0},
        {"type": "control", "command": "snapshot"},
        {"type": "control", "command": "reset"},
        {"type": "control", "command": "snapshot"},
    ]
    result = list(weather.process_events(events))
    expected = [
        {
            "type": "snapshot",
            "asof": 2,
            "stations": {"A": {"high": 12.0, "low": 10.0}}
        },
        {
            "type": "snapshot",
            "asof": 3,
            "stations": {"A": {"high": 12.0, "low":  9.0}}
        },
        {
            "type": "reset",
            "asof": 3
        }
    ]
    assert result == expected


def test_multiple_stations_and_ignore_early_controls():
    events = [
        {"type": "control", "command": "snapshot"},
        {"type": "control", "command": "reset"},
        {"type": "sample", "stationName": "X", "timestamp": 5, "temperature": 20.0},
        {"type": "sample", "stationName": "Y", "timestamp": 6, "temperature": 25.0},
        {"type": "sample", "stationName": "X", "timestamp": 7, "temperature": 18.0},
        {"type": "control", "command": "snapshot"},
    ]
    result = list(weather.process_events(events))
    expected = [
        {
            "type": "snapshot",
            "asof": 7,
            "stations": {
                "X": {"high": 20.0, "low": 18.0},
                "Y": {"high": 25.0, "low": 25.0},
            }
        }
    ]
    assert result == expected
