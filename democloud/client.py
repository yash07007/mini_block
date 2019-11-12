import socket                
import pickle as pk
import pprint

s = socket.socket()                  

s.connect(('localhost', 12345)) 
print(s.recv(1024).decode())
s.send(pk.dumps(123004))

details = pk.loads(s.recv(10000))

pprint.pprint(details)

s.close()    