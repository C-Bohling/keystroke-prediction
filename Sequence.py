class Sequence:
    def __init__(self, sequence, rawData):
        self.sequence = sequence
        self.rawData = rawData
        self.datapoints = sum(rawData.values())
        self.probabilities = self.calculate_next_probabilities()
    
    def calculate_next_probabilities(self):
        return { key: (rawValue / self.datapoints) for key, rawValue in self.rawData.items()}
    
    def addDataPoint(self, point):
        if not point in self.rawData.keys():
            self.rawData.update({point: 1})
        else:
            self.rawData[point] += 1
        self.datapoints += 1
        self.probabilities = self.calculate_next_probabilities()
    
    def __str__(self):
        return f'''
        Sequence for '{self.sequence}'
        Datapoints: {self.datapoints}
        Probabilities: {self.probabilities}
        '''
    
# s = Sequence("ab", {"a": 2, "b": 1})
# print(s.probabilities)