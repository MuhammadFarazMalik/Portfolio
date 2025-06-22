import os
import numpy as np
import librosa
from tensorflow.keras.models import load_model

# Load your trained model
model_path = r"C:\Users\ifaaz\Desktop\Lab MACHINE LEARNING\Speech-Emotion-Recognition-using-ML-and-DL-master\Speech Emotion Recognition Using Machine (22-cp-47,22-cp-03,22-cp-55)\Deep Learning\SER_model.h5"
model = load_model(model_path)

# Emotion labels (must match the model's training order)
emotion_labels = ['neutral', 'calm', 'happy', 'sad', 'angry', 'fearful', 'disgust', 'surprised']

# Preprocessing function
def preprocess_audio(audio_file):
    signal, sr = librosa.load(audio_file)  # Default sampling rate
    mfccs = np.mean(librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=40).T, axis=0)
    mfccs = np.expand_dims(mfccs, axis=1)
    mfccs = np.expand_dims(mfccs, axis=0)
    return mfccs

# Evaluate SAVEE dataset for "happy" emotion
def evaluate_happy(savee_path):
    correct_happy_predictions = []

    for file in os.listdir(savee_path):
        if file.endswith(".wav"):
            file_path = os.path.join(savee_path, file)
            features = preprocess_audio(file_path)
            predictions = model.predict(features)
            predicted_index = np.argmax(predictions)
            predicted_label = emotion_labels[predicted_index]

            # Extract the true label from the filename
            # Adjusted to handle filenames like 'DC_a01.wav'
            true_label_code = file.split('_')[1][0]  # Extract the first character after 'DC_'
            true_label = {
                'n': 'neutral',
                'a': 'angry',
                'h': 'happy',
                'sa': 'sad',
                'f': 'fearful',
                'd': 'disgust',
                'su': 'surprised'
            }.get(true_label_code, 'unknown')

            # Check if the prediction is correct and the emotion is "happy"
            if predicted_label == true_label == 'neutral':
                correct_happy_predictions.append(file)

    return correct_happy_predictions

# Path to SAVEE dataset
savee_path = r"C:\Users\ifaaz\Desktop\Lab MACHINE LEARNING\Speech-Emotion-Recognition-using-ML-and-DL-master\Speech Emotion Recognition Using Machine (22-cp-47,22-cp-03,22-cp-55)\Deep Learning\archive\ALL"

# Run evaluation for "happy" emotion
correct_happy = evaluate_happy(savee_path)

# Print results
print(f"Correctly Predicted 'Happy' Files: {len(correct_happy)}")
for file in correct_happy:
    print(file)
