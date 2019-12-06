import socket
import pymongo
import pickle as pk
import json
import glob
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
    query = c.recv(1024).decode()
    if(query == 'download'):
        c.send('ok download'.encode())
        SecretCode = pk.loads(c.recv(1024))  
        obj = constituencyDetails.find({'SecretCode':SecretCode})
        obj = [e for e in obj] 
        c.send(pk.dumps(obj))
        c.close()
    elif(query == 'upload-attendence'):
        c.send('ok upload'.encode())
        ConstId,attendedVoters = pk.loads(c.recv(100000)) 
        with open('result-data/voter-attendence/' + ConstId + '.csv', 'w') as csvFile:
            fields = ['VoterId', 'VoterName', 'VoterGender', 'VoterBiometric', 'VoterAttendence']
            csvFile.write(','.join(fields))
            csvFile.write('\n')
            for voter in attendedVoters: 
                csvFile.write(','.join([voter['VoterId'], voter['VoterName'], voter['VoterGender'], voter['VoterBiometric'], voter['VoterAttendence']]))
                csvFile.write('\n')
        c.send('Attendence Uploaded'.encode())
        c.close()
    elif(query == 'upload-chain'):
        c.send('ok upload'.encode())
        constId,chain = pk.loads(c.recv(100000))
        with open('result-data/constituency-chains/' + ConstId + '.txt', 'w') as csvFile:
            csvFile.write(json.dumps(chain))
        c.send('Chain Uploaded'.encode())
        c.close()
    elif(query == 'download-results'):
            allData = constituencyDetails.find({})
            allData = [e for e in allData]
            relevantData = [
                (
                    constituency['ConstId'],
                    constituency['ConstName'],
                    constituency['ConstState'], 
                    [
                        (
                            candidate['CandidateId'], 
                            candidate['CandidateName'], 
                            candidate['PartyId'], 
                            candidate['PartyName']
                        ) for candidate in constituency['Candidates']
                    ] 
                )   for constituency in allData
            ]
            tableData = []
            for constituency in relevantData:
                for candidate in constituency[3]:
                    tableData.append(
                        (
                            constituency[0], 
                            constituency[1], 
                            constituency[2], 
                            candidate[0], 
                            candidate[1], 
                            candidate[2], 
                            candidate[3]
                        )
                    )
            maxlen = 0
            maxuri = ''
            for uri in glob.glob('result-data/constituency-chains/*.txt'):
                with open(uri, 'r') as f:
                    chain = json.loads(f.read())
                    if(len(chain) > maxlen):
                        maxuri = uri
                        maxlen = len(chain)
            with open(maxuri, 'r') as f:
                chain = f.read()
            responseData = (tableData, chain)
            c.send(pk.dumps(responseData))
            c.close()

