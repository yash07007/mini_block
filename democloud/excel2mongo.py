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
    candidates = pd.read_excel('./raw-data/candidates/' + entry[1] + '.xlsx')
    candidates = candidates.values
    for candidate in candidates:
        candidateData = {}
        candidateData["CandidateId"] = candidate[0]
        candidateData["CandidateName"] = candidate[1]
        candidateData["PartyId"] = candidate[2]
        candidateData["PartyName"] = candidate[3]
        candidateData["PartySymbol"] = candidate[4]
        candidateData["PartyColor"] = candidate[5]
        candidatesData.append(candidateData)

    votersData = []
    voters = pd.read_csv('./raw-data/roll/' + entry[1] + '.csv')
    voters = voters.values
    for voter in voters:
        voterData = {}
        voterData["VoterId"] = voter[0]
        voterData["VoterName"] = voter[1]
        voterData["VoterGender"] = voter[2]
        voterData["VoterBiometric"] = voter[3]
        votersData.append(voterData)

    document = {}

    document["SecretCode"]  = entry[0] 
    document["ConstId"] = entry[1]
    document["ConstName"] = entry[2]
    document["ConstState"] = entry[3]
    document["NumberOfEligibleVoters"] = entry[4]
    document["NumberOfContestingCandidates"] = entry[5]
    document["Candidates"] = candidatesData
    document["Voters"] = votersData

    documents.append(document)

X = constituencyDetails.insert_many(documents)

print(X.inserted_ids)
