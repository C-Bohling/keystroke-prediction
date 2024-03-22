import keyboard
import os
import json
import time

# Data Formatting
#
# {
#   name: 'name',
#   description: 'description',
#   depth: 2,
#   sequences: {
#       aa: {
#           r: 10
#       }
#   }
#   shortSequence: {
#       a: {
#           b: 3
#       }
#   }
# }
letterFrequencies = {
    "e": 0.12702,
    "t": 0.09056,
    "a": 0.08167,
    "o": 0.07507,
    "i": 0.06966,
    "n": 0.06749,
    "s": 0.06327,
    "h": 0.06094,
    "r": 0.05987,
    "d": 0.04253,
    "l": 0.04025,
    "c": 0.02782,
    "u": 0.02758,
    "m": 0.02406,
    "w": 0.0236,
    "f": 0.02228,
    "g": 0.02015,
    "y": 0.01974,
    "p": 0.01929,
    "b": 0.01492,
    "v": 0.00978,
    "k": 0.00772,
    "j": 0.00153,
    "x": 0.0015,
    "q": 0.00095,
    "z": 0.00074,
}

acceptedKeyNames = [
    "space",
    "q",
    "w",
    "e",
    "r",
    "t",
    "y",
    "u",
    "i",
    "o",
    "p",
    "[",
    "]",
    "\\",
    "a",
    "s",
    "d",
    "f",
    "g",
    "h",
    "j",
    "k",
    "l",
    ";",
    "'",
    "z",
    "x",
    "c",
    "v",
    "b",
    "n",
    "m",
    ",",
    ".",
    "/",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "0",
    "-",
    "=",
    "`",
    "~",
    "!",
    "@",
    "#",
    "$",
    "%",
    "^",
    "&",
    "*",
    "(",
    ")",
    "_",
    "+",
    "{",
    "}",
    "|",
    ":",
    "\"",
    "<",
    ">",
    "?",
]

class KeypressProbabilitiesModel:
    def __init__(self, name, description='', depth=2, modelDir='./models'):
        '''
        Fetches model data from it's model file if present. Otherwise, 
        it creates a new model. If a model is stored away from './models',
        modelDir must be provided in order to load the model.
        '''
        self.name = name
        self.modelDir = modelDir

        self.trainingWithKeyboard = False
        self.listening = False
        self.sendingProbabilities = False
        self.callbackFunctions = []
        self.acceptedKeyNames = acceptedKeyNames
        self.prevSet = ""
        self.letterFrequencies = letterFrequencies
        self.minAcceptableDatapointCount = 10

        if not os.path.isdir(modelDir):
            print("Models folder not found.")
            print("Creating Models folder")
            os.mkdir(modelDir)

        files = os.listdir(modelDir)
                    
        if f'{name}.json' in files:
            with open(f'{self.modelDir}/{name}.json') as file:
                data = json.load(file)

            self.description = data["description"]
            self.depth = data["depth"]
            self.rawSequenceData = data["sequences"]
            self.reducedSequenceData = self.reduce_sequence_data(self.rawSequenceData)
            self.rawShortSequenceData = data["shortSequences"]
            self.reducedShortSequenceData = self.reduce_sequence_data(self.rawShortSequenceData)
        else:
            self.description = description
            self.depth = depth
            self.rawSequenceData = {}
            self.reducedSequenceData = {}
            self.rawShortSequenceData = {}
            self.reducedShortSequenceData = {}
    
    def reduce_sequence_data(self, rawSequenceData):
        reducedSequenceData = {}
        for previousSet, letterProbabilities in rawSequenceData.items():
            totalInstancesRecorded = sum(letterProbabilities.values())
            potentialLettersReduced = {posibility: (instancesRecorded / totalInstancesRecorded) for posibility, instancesRecorded in letterProbabilities.items()}
            reducedSequenceData[previousSet] = potentialLettersReduced
        return reducedSequenceData

    def train_with_text(self, text):
        '''
        Uses a passed string to train the model
        '''
        text = text.lower()
        print("training model on text")

        for i in range(self.depth, len(text)):
            letter = text[i]
            prevSet = text[i-self.depth:i]
            # print("i:", i)
            # print("self.depth:", self.depth)
            # print("letter:", letter)
            # print("prevSet:", prevSet)
            self.add_to_sequence_data(letter, prevSet)

        self.reducedSequenceData = self.reduce_sequence_data(self.rawSequenceData)
        self.reducedShortSequenceData = self.reduce_sequence_data(self.rawShortSequenceData)
    
    def add_to_sequence_data(self, letter, prevSet):
        prevLetter = prevSet[-1]
        
        if not prevSet in self.rawSequenceData.keys():
            self.rawSequenceData[prevSet] = {letter: 1}
        elif not letter in self.rawSequenceData[prevSet].keys():
            self.rawSequenceData[prevSet].update({letter: 1})
        else:
            self.rawSequenceData[prevSet][letter] += 1
            
        if not prevLetter in self.rawShortSequenceData.keys():
            self.rawShortSequenceData[prevLetter] = {letter: 1}
        elif not letter in self.rawShortSequenceData[prevLetter].keys():
            self.rawShortSequenceData[prevLetter].update({letter: 1})
        else:
            self.rawShortSequenceData[prevLetter][letter] += 1
    
    def save_model(self):
        '''
        Saves the model to a json file in the modelDir path
        '''
        print("saving model")
        modelObject = {
            "name": self.name,
            "description": self.description,
            "depth": self.depth,
            "sequences": self.rawSequenceData,
            "shortSequences": self.rawShortSequenceData
        }

        with open(f'{self.modelDir}/{self.name}.json', 'w') as file:
            json.dump(modelObject, file, indent=2)

    def get_next_keypress_probabilities(self, prevSet):
        
        if prevSet in self.rawSequenceData.keys() and \
            sum(self.rawSequenceData[prevSet].values()) >= self.minAcceptableDatapointCount:
            return self.reducedSequenceData[prevSet]
        
        lastLetter = prevSet[-1]
        if lastLetter in self.rawShortSequenceData.keys() and \
            sum(self.rawShortSequenceData[lastLetter].values()) >= self.minAcceptableDatapointCount:
            # print(self.reducedShortSequenceData)
            return self.reducedShortSequenceData[lastLetter]
        return self.letterFrequencies
    
    def handle_key_press(self, event):
        print("\033c", end='')
        currentCharName = event.name.lower()
        print(currentCharName)

        if currentCharName in self.acceptedKeyNames:
            print("in acceptedKeyNames")
            char = " " if currentCharName == "space" else currentCharName

            if self.trainingWithKeyboard:
                if len(self.prevSet) == self.depth:
                    self.add_to_sequence_data(char, self.prevSet)
                    self.reducedSequenceData = self.reduce_sequence_data(self.rawSequenceData)
                    self.reducedShortSequenceData = self.reduce_sequence_data(self.rawShortSequenceData)

            if len(self.prevSet) < self.depth:
                print("prevSet < depth")
                self.prevSet += char
            else:
                print("prevSet == or > depth")
                self.prevSet = self.prevSet[1:] + char
            
            if self.sendingProbabilities:
                print(self.prevSet)
                probabilities = self.get_next_keypress_probabilities(self.prevSet)
                
                for callback in self.callbackFunctions:
                    callback(probabilities)
    
    def start_listening(self):
        '''
        Don't call this: call send_probabilities_on_keypress() or start_training_by_keypress()

        Starts listening to key presses and recording previous sets.
        At every keypress, uses "callback" if self.trainingWithKeyboard == True
        to send probability data on keypress.
        '''

        self.listening = True
        keyboard.on_press(self.handle_key_press)

        print("listening")
    
    def send_probabilities_on_keypress(self, callback):
        '''
        Passes the callback function a function with next letter probabilities
        '''
        if not self.listening:
            self.start_listening()
        
        self.callbackFunctions.append(callback)
        self.sendingProbabilities = True
    
    def start_training_on_keypress(self):
        if not self.listening:
            self.start_listening()
        
        self.trainingWithKeyboard = True


a = KeypressProbabilitiesModel('v2-3.20.24', 'version trained on key inputs on 3.20.24 depth of 3', 3)
print("name:", a.name)
# with open('./trainingData/parsedNet.txt') as f:
#     text = f.readline()
#     a.train_with_text(text)
# a.save_model()

a.send_probabilities_on_keypress(lambda prob: print(str(prob).replace(", '", ",\n'")))
a.start_training_on_keypress()

end = False
def stop(x):
    global end
    end = True

keyboard.on_press_key('f6', lambda x: a.save_model())
keyboard.on_press_key('f7', stop)

while not end:
    time.sleep(0.5)