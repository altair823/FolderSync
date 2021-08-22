from json import dump, load
from history_schema import HistorySchema

historyFileName = 'history.json'


class History:
    # Save location history in Json file.
    @staticmethod
    def saveHistory(historyList):
        try:
            with open(historyFileName, 'w', encoding='utf-8') as historyJson:
                dump(historyList, historyJson, indent=4)
        except Exception as e:
            print(e)
            pass

    @staticmethod
    def loadHistory():
        history1 = HistorySchema()
        history2 = HistorySchema()
        try:
            with open(historyFileName, 'r', encoding='utf-8') as historyJson:
                tempFileData = load(historyJson)
                history1.Type = list(tempFileData.keys())[0]
                history1.LocationList = tempFileData[history1.Type]
                history2.Type = list(tempFileData.keys())[1]
                history2.LocationList = tempFileData[history2.Type]
        except FileNotFoundError:
            print('There is no history file. Try making a new one.')
            try:
                with open(historyFileName, 'w', encoding='utf-8') as historyJson:
                    tempDict = dict()
                    tempDict['original'] = history1.LocationList
                    tempDict['destination'] = history2.LocationList
                    dump(tempDict, historyJson, indent=4)
            except Exception as e:
                raise e
        finally:
            temp = {'original': history1.LocationList, 'destination': history2.LocationList}
            return temp
