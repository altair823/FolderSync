class HistorySchema:
    def __init__(self):
        self.Type = None
        self.LocationList = []


def VerifyHistory(history, hisType):
    if type(history) is not HistorySchema:
        raise Exception('Wrong schema class')
    if history.Type is None or history.Type != hisType:
        tempHistory = HistorySchema
        tempHistory.Type = hisType
        return tempHistory
