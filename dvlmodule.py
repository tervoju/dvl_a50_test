# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

# Requires direct Ethernet connection to Waterlinkd DVL A50
#  
import time
import os
import sys
import asyncio
from six.moves import input
import threading
#from azure.iot.device.aio import IoTHubModuleClient
#from azure.iot.device import Message

import csv
import socket
import logging
import json
from datetime import datetime
from datetime import timezone

# '{"time":81.95233154296875,"vx":0.0010110485600307584,"vy":-0.0007144125993363559,"vz":-0.00028028266387991607,"fom":0.0006783335120417178,"altitude":0.09129234403371811,"transducers":[{"id":0,"velocity":-0.0008826721459627151,"distance":0.14160001277923584,"rssi":-25.902250289916992,"nsd":-96.84258270263672,"beam_valid":true},{"id":1,"velocity":-0.00025184592232108116,"distance":0.1534000039100647,"rssi":-26.17237663269043,"nsd":-95.73751068115234,"beam_valid":true},{"id":2,"velocity":0.000026558060199022293,"distance":0.08260000497102737,"rssi":-25.71442413330078,"nsd":-95.33403778076172,"beam_valid":true},{"id":3,"velocity":0.00035340990871191025,"distance":0.08260000497102737,"rssi":-26.227529525756836,"nsd":-96.07746124267578,"beam_valid":true}],"velocity_valid":true,"status":0,"format":"json_v2","type":"velocity"}

TCP_IP = "192.168.194.95"
TCP_PORT = 16171
deviceid = "SUB"
csv_header = "time,vx,vy,vz,fom,altitude,transducers_0_id,transducers_0_velocity,transducers_0_distance,transducers_0_rssi,transducers_0_nsd,transducers_0_beam_valid,transducers_1_id,transducers_1_velocity,transducers_1_distance,transducers_1_rssi,transducers_1_nsd,transducers_1_beam_valid,transducers_2_id,transducers_2_velocity,transducers_2_distance,transducers_2_rssi,transducers_2_nsd,transducers_2_beam_valid,transducers_3_id,transducers_3_velocity,transducers_3_distance,transducers_3_rssi,transducers_3_nsd,transducers_3_beam_valid,velocity_valid,status,format,type\n"
save_locally = True
csv_writer = ""

dataJson = b''

class TCPConnection:
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        try:
            self.sock.connect((host, port))
            print('Successful Connection')
        except:
            print('Connection Failed')

    def readlines(self):
        data = self.sock.recv(1024)
        print(data)

    def read_dvl(self):
        global dataJson, deviceid, save_locally
        vx = 0
        vy = 0
        vz = 0
        altitude = 0
        measurement_cnt = 0
        dataJson = b''
        rawdata = b''
        data = b''
        time_delta = 0
        logging.info('read dvl')
        while(1):
            logging.info('read dvl - loop')
            rawdata = b''
            while not b'\n' in rawdata:
                try:
                    data = self.sock.recv(1)
                    if len(data) == 0:
                        logging.info('dvl socket lost, no data, reconnecting')
                        #self.connect(TCP_IP, TCP_PORT)
                        continue
                except:
                    logging.info('Lost connection to DVL, reconnecting')
                    self.connect(TCP_IP, TCP_PORT)
                    continue
                rawdata = rawdata + data
        
            rawdata = dataJson + rawdata
            dataJson = b''
            strdata = rawdata.decode("utf-8").split('\n')
            dJson = strdata[1]
            strdata = strdata[0]
            logging.info(strdata)
            # here the dvl message handing
            jsondata = json.loads(strdata) 
           
            # DVL velocity message
            if "time" in jsondata:
                logging.info("time")
                # 1 forward ?

                # 2 save local csv file
                try:
                    if save_locally == True:
                        if csv_writer:
                            csv_s = flatten(jsondata)
                            csv_rows = csv_s.split('\n')
                            if csv_rows[1]:
                                csv_writer.writerow(csv_s[1]+ '\n')
                except:
                    logging.info('fails to write csv')
                time_delta = time_delta + jsondata["time"]/1000.0
                # 3 target to average 60 s measurements  and forward
                if jsondata["velocity_valid"] == True:
                    # average 60 s distance -> if 0,05 m/s current -> 3 m 
                    # if 80 ms between messages -> 750 messages?
                    vx = vx + jsondata["vx"]
                    vy = vy + jsondata["vy"]
                    vz = vz + jsondata["vz"]
                    altitude = altitude + jsondata["altitude"]
                    measurement_cnt += 1
                    if time_delta >= 1.0:
                        message = {
                            "deviceid": deviceid,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "vx": vx / measurement_cnt,
                            "vy": vy / measurement_cnt,
                            "vz": vz / measurement_cnt,
                            "altitude" : altitude /measurement_cnt,
                            "measurements": measurement_cnt
                        }
                        time_delta = 0
                        measurement_cnt = 0
                        vx = 0
                        vy = 0
                        vz = 0
                        logging.info("message collected")
                        ##payload = Message(json.dumps(message), content_encoding="utf-8", content_type="application/json")
                        ##await module_client.send_message_to_output(payload, "DVLaverageoutput") 
            # IMU message with x,y,z
            if "ts" in jsondata:
                logging.info("ts as IMU message")
            # 
            # 
              

async def main():
    global TCP_IP, TCP_PORT
    logging.info("IoT Hub Client for Python: dvlmodule")
    try:
        if not sys.version >= "3.5.3":
            raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
        print ( "IoT Hub Client for Python" )

        # The client object is used to interact with your Azure IoT hub.
        module_client = None  #IoTHubModuleClient.create_from_edge_environment()

        # connect the client.
        #await module_client.connect()

        # define behavior for receiving an input message on input1
        async def input1_listener(module_client):
            while True:
                input_message = await module_client.on_message_received("input1")  # blocking call
                print("the data in the message received on input1 was ")
                print(input_message.data)
                print("custom properties are")
                print(input_message.custom_properties)
                print("forwarding mesage to output1")
                await module_client.send_message_to_output(input_message, "output1")

        # define behavior for halting the application
        def stdin_listener():
            while True:
                try:
                    selection = input("Q")
                    if selection == "Q" or selection == "q":
                        print("Quitting...")
                        break
                except:
                    time.sleep(10)
        
        listen = TCPConnection()
        listen.connect(TCP_IP, TCP_PORT)
        logging.info( "The dvlmodule socket is connected ")
            
        # Schedule task for C2D Listener
        listeners = asyncio.gather(input1_listener(module_client), listen.read_dvl())
        logging.info( "The dvlmodule is now waiting for messages. ")

        # Run the stdin listener in the event loop
        loop = asyncio.get_event_loop()
        user_finished = loop.run_in_executor(None, stdin_listener)

        # Wait for user to indicate they are done listening for messages
        await user_finished

        # Cancel listening
        listeners.cancel()

        # Finally, disconnect
        await module_client.disconnect()

    except Exception as e:
        print ( "Unexpected error %s " % e )
        raise

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(os.environ.get("LOGLEVEL", "INFO"))
    asyncio.run(main())