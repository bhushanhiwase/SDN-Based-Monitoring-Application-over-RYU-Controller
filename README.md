# SDN-Based-Monitoring-Application-over-RYU-Controller

This SDN application displays various stats of an OpenFlow switch using control-plane programming over RYU controller. 

Steps:
1. Launch a topology in mininet VM using the command: "-	sudo mn --topo tree,3 --mac --controller=remote,
   ip= (Ip of the controller VM) --switch ovsk"
2. In the VM running controller, start the application (Monnitor_application.py file) using the ryu-manager:
   "ryu-manager Monitor_Application.py"
3. The step 2 will start the Monitoring application Now ping all the clients using "pingall" command.
4. The monitor application send query to the controller and with the help of RYU controller send the following info:
'datapath,'in-port','eth-dst,'out-port', 'packets', 'bytes', 'duration', 'datapath','port','rx-pkts','rx-bytes'
,'rx-error','tx-pkts', 'tx-bytes','tx-error', % Packet Loss', 'Datapath', 'port', 'MAC address','Bit rate(kbps)'
