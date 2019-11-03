from collections import OrderedDict

class Transaction:
    def __init__(self, nodeId, candidateId, partyId, signature):
        self.nodeId = nodeId
        self.candidateId = candidateId
        self.partyId = partyId
        self.signature = signature


    def __repr__(self):
        return str(self.__dict__)

    def to_ordered_dict(self):
        return OrderedDict([('nodeId', self.nodeId), ('candidateId', self.candidateId), ('partyId', self.partyId)])