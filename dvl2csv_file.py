import time
import sys
import os
import logging
import json
import csv

from flatten_json import flatten
from datetime import datetime
from datetime import timezone

class dvl2csv_file:
    def __init__(self):
        #DVL distance message
        timestr = time.strftime("%Y%m%d-%H%M%S")
        csv_header_time = ['timestamp','time','vx','vy','vz','fom','altitude','transducers_0_id','transducers_0_velocity','transducers_0_distance','transducers_0_rssi','transducers_0_nsd','transducers_0_beam_valid','transducers_1_id','transducers_1_velocity','transducers_1_distance','transducers_1_rssi','transducers_1_nsd','transducers_1_beam_valid','transducers_2_id','transducers_2_velocity','transducers_2_distance','transducers_2_rssi','transducers_2_nsd','transducers_2_beam_valid','transducers_3_id','transducers_3_velocity','transducers_3_distance','transducers_3_rssi','transducers_3_nsd','transducers_3_beam_valid','velocity_valid','status','format','type']
        csv_file_time = open(timestr + 'dvl_data_time.csv', 'w')
        self.csv_writer_time = csv.writer(csv_file_time)
        #DVL IMU message
        csv_header_ts = ["timestamp","ts","x","y","z","std","roll","pitch","yaw","type","status","format"]
        csv_file_ts = open(timestr + 'dvl_data_ts.csv', 'w')
        self.csv_writer_ts = csv.writer(csv_file_ts)

        self.csv_writer_time.writerow(csv_header_time)
        self.csv_writer_ts.writerow(csv_header_ts)


    def generate_csv_data(self, data: dict) -> str:
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

    #def create_csv_files():
    #    global csv_file_time, csv_writer_time, csv_file_ts, csv_writer_ts    
    #    csv_writer_time.writerow(csv_header_time)
    #    csv_writer_ts.writerow(csv_header_ts)

    def write_csv_data(self, dvl_jsondata):
        try:
            # ct stores current time
            ct = datetime.now()
            # ts store timestamp of current time
            ts = ct.timestamp()            
            csv_s = flatten(dvl_jsondata)
            csv_data = self.generate_csv_data(csv_s)
            csv_rows = csv_data.split('\n')
            if csv_rows[1]:
                dvl_array = csv_rows[1].split(',')
                dvl_array.insert(0, ts)  
                if "time" in dvl_jsondata:  
                    self.csv_writer_time.writerow(dvl_array)
                if  "ts" in dvl_jsondata:
                    self.csv_writer_ts.writerow(dvl_array)

        except:
            logging.info('fails to write csv')
