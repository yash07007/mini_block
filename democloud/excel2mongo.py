import pymongo
import pandas as pd
import pprint

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

database = myclient['cloudData']

database.drop_collection('constituencyDetails')

constituencyDetails = database['constituencyDetails']

df = pd.read_csv('./raw-data/card-cons.csv')
df = df.values

documents = []
for entry in df:
    candidatesData = []
    candidates = pd.read_excel('./raw-data/' + entry[1] + '.xlsx')
    candidates = candidates.values
    for candidate in candidates:
        candidateData = {}
        candidateData["CandidateId"] = candidate[0]
        candidateData["CandidateName"] = candidate[1]
        candidateData["PartyId"] = candidate[2]
        candidateData["PartyName"] = candidate[3]
        candidateData["PartySymbol"] = candidate[4]
        candidateData["PartyColor"] = candidate[5]
        candidateData["CandidatePicture"] = candidate[6]
        candidatesData.append(candidateData)

    document = {}

    document["SecretCode"]  = entry[0] 
    document["ConstId"] = entry[1]
    document["ConstName"] = entry[2]
    document["ConstState"] = entry[3]
    document["NumberOfEligibleVoters"] = entry[4]
    document["NumberOfContestingCandidates"] = entry[5]
    document["Candidates"] = candidatesData

    documents.append(document)

X = constituencyDetails.insert_many(documents)

print(X.inserted_ids)
