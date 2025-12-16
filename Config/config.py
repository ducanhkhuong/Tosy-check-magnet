import json
from Define.define import Config , Command , Calib , Sensor 
import sys
import os

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)

    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)


def load_config(json_file):
    with open(json_file) as f:
        raw = json.load(f)
    calibrations = {}
    for key, val in raw.items():
        if key.startswith("Calib"):
            sensor_list = [
                Sensor(id=s["id"], x=s["x"], y=s["y"])
                for s in val["Sensors"]
            ]

            calib = Calib(
                sensor_number=val["SensorNumber"],
                magnet_threshold=val["MagnetThreshold"],
                sensors=sensor_list
            )

            calibrations[key] = calib

    config = Config(
        port=raw["Port"],
        baudrate=raw["Baudrate"],
        logfile=raw["Logfile"],
        image=raw.get("Image", ""),
        calib=calibrations
    )
    return config