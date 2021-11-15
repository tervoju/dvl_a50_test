import socket
import time
import os
import logging
import json
from flatten_json import flatten
from datetime import datetime
from datetime import timezone


TCP_IP = "192.168.194.95"
TCP_PORT = 16171
deviceid = "SUB"
csv_header = "time,vx,vy,vz,fom,altitude,transducers_0_id,transducers_0_velocity,transducers_0_distance,transducers_0_rssi,transducers_0_nsd,transducers_0_beam_valid,transducers_1_id,transducers_1_velocity,transducers_1_distance,transducers_1_rssi,transducers_1_nsd,transducers_1_beam_valid,transducers_2_id,transducers_2_velocity,transducers_2_distance,transducers_2_rssi,transducers_2_nsd,transducers_2_beam_valid,transducers_3_id,transducers_3_velocity,transducers_3_distance,transducers_3_rssi,transducers_3_nsd,transducers_3_beam_valid,velocity_valid,status,format,type\n"
save_locally = True
csv_writer = ""
# how to reset IMU: http://192.168.194.95/api/positioning/reset

### GENERIC 
# problems with VS Code connection "remote-SSH: connect to Host"
#To find out which entry is for a known hostname in known_hosts:
# ssh-keygen -H  -F <hostname or IP address>
#To delete a single entry from known_hosts:

# ssh-keygen -R <hostname or IP address>

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
                                csv_writer.writerow(csv_s[1])
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

def create_csv_file():
    global csv_writer
    csv_file = open('dvl_data.csv', 'w')
    csv_writer = csv.writer(csv_file)    

if __name__ == '__main__' : 
    logging.basicConfig()
    logging.getLogger().setLevel(os.environ.get("LOGLEVEL", "INFO"))
    listen = TCPConnection()
    listen.connect('192.168.194.95',16171)
    while (1):
        listen.read_dvl()
