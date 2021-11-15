
# how to reset IMU: http://192.168.194.95/api/positioning/reset

# problems with VS Code connection "remote-SSH: connect to Host"
#To find out which entry is for a known hostname in known_hosts:
# ssh-keygen -H  -F <hostname or IP address>
#To delete a single entry from known_hosts:

# ssh-keygen -R <hostname or IP address>


# dvl 


https://waterlinked.github.io/dvl/dvl-protocol/


Velocity report

A velocity report is outputted after each measurement has been completed. The expected update rate varies depending on the altitude, but will be in the range 2-26 Hz.

The report is in the following format: wrx,[time],[vx],[vy],[vz],[fom],[altitude],[valid],[status]

wrx,112.83,0.007,0.017,0.006,0.000,0.93,y,0*d2
wrx,140.43,0.008,0.021,0.012,0.000,0.92,y,0*b7
wrx,118.47,0.009,0.020,0.013,0.000,0.92,y,0*54

Example where velocities and altitude are not valid and a high temperature warning occurs:

wrx,1075.51,0.000,0.000,0.000,2.707,-1.00,n,1*04
wrx,1249.29,0.000,0.000,0.000,2.707,-1.00,n,1*6a
wrx,1164.94,0.000,0.000,0.000,2.707,-1.00,n,1*39


# basics

uart/usb converter

Bus 001 Device 004: ID 0403:6011 Future Technology Devices International, Ltd FT4232H Quad HS USB-UART/FIFO IC


# ubuntu

https://askubuntu.com/questions/22835/how-to-network-two-ubuntu-computers-using-ethernet-without-a-router



{"time":76.7872314453125,"vx":-0.00032196289976127446,"vy":0.000003616247568061226,"vz":0.000027176462026545778,"fom":0.0006300417589955032,"altitude":0.18486595153808594,"transducers":[{"id":0,"velocity":-0.00007525738328695297,"distance":0.22420001029968262,"rssi":-41.31503677368164,"nsd":-96.30579376220703,"beam_valid":true},{"id":1,"velocity":0.00043700519017875195,"distance":0.2832000255584717,"rssi":-35.15789794921875,"nsd":-95.66007995605469,"beam_valid":true},{"id":2,"velocity":-0.00039610499516129494,"distance":0.11800000071525574,"rssi":-49.564998626708984,"nsd":-96.72905731201172,"beam_valid":true},{"id":3,"velocity":0.0002194414846599102,"distance":0.14160001277923584,"rssi":-37.52872848510742,"nsd":-90.13951873779297,"beam_valid":true}],"velocity_valid":true,"status":0,"format":"json_v2","type":"velocity"}