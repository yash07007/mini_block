import socket
import pymongo
import pickle as pk

# Creating a Socket
try: 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    print("Socket successfully created")
except socket.error as err: 
    print("socket creation failed with error %s" %(err))

# Connecting to Database
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
database = myclient['cloudData']
constituencyDetails = database['constituencyDetails']
print('Data Loaded...')

# Binding to a Socket and Listning
s.bind(('localhost', 12345))           

s.listen(5) 
print('Server is listening...')      

while True: 
   c, addr = s.accept()      
   print('Got connection from', addr) 
   SecretCode = pk.loads(c.recv(1024))  
   obj = constituencyDetails.find({'SecretCode':123004})
   obj = [e for e in obj] 
   c.send(pk.dumps(obj))
   c.close() 