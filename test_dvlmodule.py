import socket
import time
import sys
import os
import logging
import json
import csv

from flatten_json import flatten
from datetime import datetime
from datetime import timezone

from six.moves import input
import threading
import asyncio
from functools import wraps, partial

from dvl_socket import TCPConnection

# for socket 
TCP_IP = "192.168.194.95"
TCP_PORT = 16171
deviceid = "SUB"

#
#   
#
async def main():
    global TCP_IP, TCP_PORT, csv_file_time, csv_writer_time, csv_file_ts, csv_writer_ts

    try:
        if not sys.version >= "3.5.3":
            raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
        logging.info("IoT Hub Client for Python: dvlmodule")

        # The client object is used to interact with your Azure IoT hub.
        #module_client = IoTHubModuleClient.create_from_edge_environment()

        # connect the client.
        #await module_client.connect()

        '''
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
        '''
        # define behavior for halting the application
        def stdin_listener():
            while True:
                try:
                    selection = input("Press Q to quit\n")
                    if selection == "Q" or selection == "q":
                        print("Quitting...")
                        break
                except:
                    time.sleep(10)
        
        listen = TCPConnection()
        await listen.connect(TCP_IP, TCP_PORT)
        logging.info( "The dvl module TCP socket is connected ")
            
        # Schedule task for C2D Listener
        listeners = asyncio.gather(listen.read_dvl())
        logging.info( "The dvlmodule is now waiting for messages from DVL A50. ")

        # Run the stdin listener in the event loop
        loop = asyncio.get_event_loop()
        user_finished = loop.run_in_executor(None, stdin_listener)

        # Wait for user to indicate they are done listening for messages
        await user_finished

        # Cancel listening
        listeners.cancel()

        # Finally, disconnect
        #await module_client.disconnect()

    except Exception as e:
        print ( "Unexpected error %s " % e )
        raise

if __name__ == '__main__' : 
    logging.basicConfig()
    logging.getLogger().setLevel(os.environ.get("LOGLEVEL", "INFO"))
    asyncio.run(main())
  
