import socket
import time
import os
import logging
import json
from datetime import datetime
from datetime import timezone


TCP_IP = "192.168.194.95"
TCP_PORT = 16171

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
        global dataJson
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

                # 2 save locally
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
                            "deviceid": os.environ["IOTEDGE_DEVICEID"],
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
                        ##payload = Message(json.dumps(message), content_encoding="utf-8", content_type="application/json")
                        ##await module_client.send_message_to_output(payload, "DVLaverageoutput") 
            # IMU message with x,y,z
            if "ts" in jsondata:
                logging.info("ts as IMU message")
            # 

if __name__ == '__main__' : 
    logging.basicConfig()
    logging.getLogger().setLevel(os.environ.get("LOGLEVEL", "INFO"))
    listen = TCPConnection()
    listen.connect('192.168.194.95',16171)
    while (1):
        listen.read_dvl()
