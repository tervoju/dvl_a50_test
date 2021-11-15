import socket
import time
import os
import logging
import json
from flatten_json import flatten
from datetime import datetime
from datetime import timezone
import csv

dvl_json = {
    "time": 393.4316711425781,
    "vx": 0,
    "vy": 0,
    "vz": 0,
    "fom": 2.661566972732544,
    "altitude": -1,
    "transducers": [
        {
            "id": 0,
            "velocity": 0,
            "distance": -1,
            "rssi": -119.50314331054688,
            "nsd": -95.97090148925781,
            "beam_valid": False
        },
        {
            "id": 1,
            "velocity": 0,
            "distance": -1,
            "rssi": -119.97660064697266,
            "nsd": -94.66395568847656,
            "beam_valid": False
        },
        {
            "id": 2,
            "velocity": 0,
            "distance": -1,
            "rssi": -120.99003601074219,
            "nsd": -96.87013244628906,
            "beam_valid": False
        },
        {
            "id": 3,
            "velocity": 0,
            "distance": -1,
            "rssi": -116.98272705078125,
            "nsd": -91.95513916015625,
            "beam_valid": False
        }
    ],
    "velocity_valid": False,
    "status": 0,
    "format": "json_v2",
    "type": "velocity"
}

def generate_csv_data(data: dict) -> str:
  
    # Defining CSV columns in a list to maintain
    # the order
    csv_columns = data.keys()
  
    # Generate the first row of CSV 
    csv_data = ",".join(csv_columns) + "\n"
  
    # Generate the single record present
    new_row = list()
    for col in csv_columns:
        new_row.append(str(data[col]))
  
    # Concatenate the record with the column information 
    # in CSV format
    csv_data += ",".join(new_row) + "\n"
  
    return csv_data

def normalize_json(data: dict) -> dict:
  
    new_data = dict()
    for key, value in data.items():
        if not isinstance(value, dict):
            new_data[key] = value
        else:
            for k, v in value.items():
                new_data[key + "_" + k] = v
  
    return new_data

def dvl_json2csv(dvl_object):
    normalized_data = normalize_json(dvl_object)
    csv_data = generate_csv_data(normalized_data)
    print(csv_data)


def main():
    #dvl_json2csv(dvl_json)
    csv_s = flatten(dvl_json)
    #print(csv_s)
    csv_data = generate_csv_data(csv_s)
    csv_only = csv_data.split('\n')
    print(csv_only[0])
    print(csv_only[1])




if __name__ == '__main__' : 
    main()