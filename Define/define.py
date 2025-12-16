from dataclasses import dataclass, field
from typing import List, Optional , ClassVar

@dataclass
class Sensor:
    id: int
    x: int
    y: int

@dataclass
class Calib:
    sensor_number: int
    magnet_threshold: int
    sensors: list

@dataclass
class Config:
    port: str
    logfile: str
    baudrate: int
    image: str
    calib: dict

@dataclass
class Command:
    calib_1: str = "CALIB:1\n"
    calib_2: str = "CALIB:2\n"
    check_1: str = "CHECK:1\n"
    check_2: str = "CHECK:2\n"
    compare_1: str = "COMPARE1:"
    compare_2: str = "COMPARE2:"
    value_compare_1: str = ""
    value_compare_2: str = ""

@dataclass
class Flags:
    is_connected: bool = False
    is_calib1: bool = False
    is_calib2: bool = False
    is_compare1: bool = False
    is_compare2: bool = False
    onclick_compare_1: bool = False
    onclick_compare_2: bool = False
    onclick_mode : bool = False

@dataclass
class Total:
    calib1_manual_is_total: bool = False
    calib2_manual_is_total: bool = False
    calib1_auto_is_total: bool = False
    calib2_auto_is_total: bool = False

    list_false_sensors_calib1: List[int] = field(default_factory=list)
    list_done_sensors_calib1: List[int] = field(default_factory=list)
    list_false_sensors_calib2: List[int] = field(default_factory=list)
    list_done_sensors_calib2: List[int] = field(default_factory=list)

    list_false_sensors_calib1_auto: List[int] = field(default_factory=list)
    list_done_sensors_calib1_auto: List[int] = field(default_factory=list)
    list_false_sensors_calib2_auto: List[int] = field(default_factory=list)
    list_done_sensors_calib2_auto: List[int] = field(default_factory=list)