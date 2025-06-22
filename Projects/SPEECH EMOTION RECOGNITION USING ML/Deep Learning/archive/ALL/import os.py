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

# Evaluate SAVEE dataset
def evaluate_savee(savee_path):
    correct_predictions = []
    incorrect_predictions = []

    for file in os.listdir(savee_path):
        if file.endswith(".wav"):
            file_path = os.path.join(savee_path, file)
            features = preprocess_audio(file_path)
            predictions = model.predict(features)
            predicted_index = np.argmax(predictions)
            predicted_label = emotion_labels[predicted_index]

            # Extract the true label from the filename
            true_label_code = file[0]  # First character indicates emotion
            true_label = {
                'n': 'neutral',
                'a': 'angry',
                'h': 'happy',
                'sa': 'sad',
                'f': 'fearful',
                'd': 'disgust',
                'su': 'surprised'
            }.get(true_label_code, 'unknown')

            # Check if the prediction is correct
            if predicted_label == true_label:
                correct_predictions.append(file)
            else:
                incorrect_predictions.append((file, true_label, predicted_label))

    return correct_predictions, incorrect_predictions

# Path to SAVEE dataset
savee_path = r"C:\Users\ifaaz\Desktop\Lab MACHINE LEARNING\Speech-Emotion-Recognition-using-ML-and-DL-master\Speech Emotion Recognition Using Machine (22-cp-47,22-cp-03,22-cp-55)\Deep Learning\archive\ALL"

# Run evaluation
correct, incorrect = evaluate_savee(savee_path)

# Print results
print(f"Correct Predictions: {len(correct)}")
print(f"Incorrect Predictions: {len(incorrect)}")
print("\nCorrectly Predicted Files:")
for file in correct:
    print(file)

print("\nIncorrectly Predicted Files:")
for file, true_label, predicted_label in incorrect:
    print(f"File: {file}, True Label: {true_label}, Predicted Label: {predicted_label}")
