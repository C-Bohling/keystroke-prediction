# keystroke-prediction
This tool can be used to create a model of your keystroke patterns, providing data to predict what keys are likely to be pressed next. The functionality is currently limmited to all keys that represent single characters and space. Keys it does not track include shift, enter, backspace, pagedown, etc.

## Usage

### KeypressProbabilityModel class

after importing the "Model" module to your project, initiate a `KeypressProbabilityModel` object to get started. 

#### `KeypressProbabiltiesModel(name, description="", maxDepth=2, modelDir="./models", acceptedKeyNames=default, minAcceptableDatapoints)`
- `name`: Defines the name of a new model, or is used to open an existing model. All other fields (except modelDir) are ignored if an existing model is found.
- `description`: Defines the desctiption of the model.
- `maxDepth`: Defines the maximum number of characters to be recorded in the sequence data. This number is recursive, so if it was set to 3, the model would also store all the data for sequences of 2 characters and sequences of 1 character.
- `modelDir`: Defines where the model data will be found/stored. If you are trying to use a stored model, make sure this is set to the directory that model is in.
- `acceptedKeyNames`: By default, it includes all letters, numbers, and characters on the keyboard. This determines what characters the models stores.
- `minAcceptableDatapoints`: This determines how many datapoints are required for the model to use a sequence. For instance, if someone wanted probabilities for the next letter after a sequence of 3 characters, but only had two recorded instances of what happened after that sequence and this value was set to 3, the model wouldn't return the data for all the sequence of 3, but would instead check for the sequence of 2.

#### `.train_with_text(text)`
Trains the model on all the sequences in `text`. That way you can get started without typing a bunch. (or you can skip it)

#### `.save_model()`
Saves the model as a JSON file in `.modelDir` with the name "{name}.json". This is the file the program will look for when you intitialize a `KeypressProbabilitiesModel` object.

#### `.get_sequence_data(prevSet)`
Returns a `Sequence` object for a given sequence. If I passed in "abc", and the model was trained with that sequence, it would return a `Sequence` object with all the recorded following keypresses.

#### `.send_sequence_data_on_keypress(callback)`
Passes `callback` a `Sequence` object representing the previous sequence and the posible next keypresses after every keypress.

There is not yet a stop function

#### `.start_training_on_keypress()`
After running this method, every keystroke you press (that is in the `.acceptedKeyNames`) will be recorded and added to the sequence data.

There is not yet a stop function

### Sequence Object

#### `Sequence(sequence, rawData)` 
Gets passed a sequence, like "abc", and then it gets passed the rawData of what keys were pushed next and how many times as a dictionary like {d:5, c:1}. This example means that out of 6 times that "abc" was typed, 5 times a d was pressed next, and once a c was pressed next.

#### `.addDataPoint(point)`
If you pass it a "d" it adds one to the "d" catagory of the rawData, updates the datapoints property and updates the probabilities property.

#### `.sequence`
The sequence this object represents

#### `.rawData`
The dictionary of raw keystroke data formated {a: 4, b:3} where a was pressed after `.sequence` 4 times and b was pressed 3 times after `.sequence`.

#### `.datapoints`
The number of points in the data. This can be used to determine the credability of the probabilities.

#### `.probabilities`
The dictionary of the probabilities of all the keypresses represented as decimal percentage. {a: 0.35, b: 0.65} would mean that b is the next letter 65% of the time and a is the next letter 35% of the time.

## Other stuff.
This was made for fun, so I didn't go super in-depth. I created this so I could have an RGB keyboard change colors predictively depending on my previous keystrokes. Feel free to fork and improve as you wish to make it work for your project!

\- *Caleb Bohling*