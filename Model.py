import keyboard
import os
import json

from Sequence import Sequence

'''  Data Formatting v3

{
  name: "name",
  description: "description",
  maxDepth: 2,
  minAcceptableDatapoints = 2
  acceptedKeyNames: {}
  sequences: {
    a: {b: 2, c: 4},
    aa: {a: 4, c: 1}
  },
}

'''

letterFrequencies = Sequence("Standard letter frequencies", {
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
})

singleCharKeyNames = [
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
    def __init__(self, name, description="", maxDepth=2, modelDir="./models", acceptedKeyNames=singleCharKeyNames, minAcceptableDatapoints=2):
        '''
        Fetches model data from it's model file if present. Otherwise, 
        it creates a new model. If a model is stored away from "./models",
        modelDir must be provided in order to load the model. All arguments
        but the name will be overwriten by the saved file if such exists.
        '''
        self.name = name
        self.modelDir = modelDir

        self.trainingWithKeyboard = False
        self.listening = False
        self.sendingSequenceData = False
        self.callbackFunctions = []
        self.prevSet = ""
        self.letterFrequencies = letterFrequencies

        if not os.path.isdir(modelDir):
            print("Models folder not found.")
            print("Creating Models folder")
            os.mkdir(modelDir)

        files = os.listdir(modelDir)
                    
        if f"{name}.json" in files:
            with open(f"{self.modelDir}/{name}.json") as file:
                data = json.load(file)

            self.description = data["description"]
            self.maxDepth = data["maxDepth"]
            self.sequenceData = {sequence: Sequence(sequence, result) for sequence, result in data["sequences"].items()}
            self.minAcceptableDatapoints = data["minAcceptableDatapoints"]
            self.acceptedKeyNames = data["acceptedKeyNames"]
        else:
            self.description = description
            self.maxDepth = maxDepth
            self.sequenceData = {}
            self.minAcceptableDatapoints = minAcceptableDatapoints
            self.acceptedKeyNames = acceptedKeyNames

    def train_with_text(self, text):
        '''
        Uses a passed string to train the model
        '''

        text = text.lower()
        print("training model on text")

        for i in range(self.maxDepth, len(text)):
            letter = text[i]
            prevSet = text[i-self.maxDepth:i]
            self.add_to_sequence_data(letter, prevSet)
    
    def add_to_sequence_data(self, letter, prevSet):
        for depth in range(1, self.maxDepth+1):
            prevSetAtDepth = prevSet[(self.maxDepth - depth) - 1:]
            if not prevSetAtDepth in self.sequenceData.keys():
                self.sequenceData[prevSetAtDepth] = Sequence(prevSetAtDepth, {letter: 1})
            else:
                self.sequenceData[prevSetAtDepth].addDataPoint(letter)
    
    def save_model(self):
        '''
        Saves the model to a json file in the modelDir path
        '''
        print("saving model")
        modelObject = {
            "name": self.name,
            "description": self.description,
            "maxDepth": self.maxDepth,
            "minAcceptableDatapoints": self.minAcceptableDatapoints,
            "acceptedKeyNames": self.acceptedKeyNames,
            "sequences": {sequence: data.rawData for sequence, data in self.sequenceData.items()}
        }

        with open(f"{self.modelDir}/{self.name}.json", "w") as file:
            json.dump(modelObject, file, indent=2)

    def get_sequence_data(self, prevSet):
        for nDepth in range(-len(prevSet), 0):
            prevSetAtDepth = prevSet[nDepth:]
            if prevSetAtDepth in self.sequenceData.keys() and \
                self.sequenceData[prevSetAtDepth].datapoints >= self.minAcceptableDatapoints:
                return self.sequenceData[prevSetAtDepth]
        
        return self.letterFrequencies
    
    def handle_key_press(self, event):
        print("\033c", end="")
        currentCharName = event.name.lower()
        print(currentCharName)

        if currentCharName in self.acceptedKeyNames:
            print("in acceptedKeyNames")
            char = " " if currentCharName == "space" else currentCharName

            if self.trainingWithKeyboard and \
                len(self.prevSet) == self.maxDepth:
                self.add_to_sequence_data(char, self.prevSet)

            if len(self.prevSet) < self.maxDepth:
                print("prevSet < maxDepth")
                self.prevSet += char
            else:
                print("prevSet == or > maxDepth")
                self.prevSet = self.prevSet[1:] + char
            
            if self.sendingSequenceData:
                print(self.prevSet)
                sequence = self.get_sequence_data(self.prevSet)
                
                for callback in self.callbackFunctions:
                    callback(sequence)
    
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
    
    def send_sequence_data_on_keypress(self, callback):
        '''
        Passes the callback function a dictionary with next letter probabilities
        '''
        if not self.listening:
            self.start_listening()
        
        self.callbackFunctions.append(callback)
        self.sendingSequenceData = True
    
    def start_training_on_keypress(self):
        if not self.listening:
            self.start_listening()
        
        self.trainingWithKeyboard = True