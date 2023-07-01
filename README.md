# Reliable data transfer through UDP

## Problem 
TCP is a reliable data transfer protocol, however it is not as fast as the UDP protocol due to the hand shake mechanism. Here we tend to achieve the best of both i.e, data reliabity over the UDP protocol.


## Outcome
• Extended UDP to provide reliable data transfer over realistic delays and packet loss conditions.  
• Throughput up to 6x compared to conventional TCP  
• Features -  
  1. packet loss detection,  
  2. delayed acknowledgment,  
  3. packet retransmission,   
  4. network congestion control

## Configuration
• Update the BUFFER_SIZE in ![client](src/rdt_udp_client_final.py) file to modify the size of each packet.  
• You can verify that the lower value of BUFFER_SIZE gives high transmission time as compared to higer values of BUFFER_SIZE    


## Running
```bash
<!-- navigate to the src folder -->

<!-- Star server in terminal 1 -->
python3 rdt_udp_server_final.py

<!-- Star client in terminal 2 -->
python3 rdt_udp_client_final.py

```
