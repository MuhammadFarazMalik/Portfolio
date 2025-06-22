import streamlit as st
import numpy as np
import librosa
from tensorflow.keras.models import load_model

# Load your trained CNN model
model = load_model(r"C:\Users\ifaaz\Desktop\Lab MACHINE LEARNING\Speech-Emotion-Recognition-using-ML-and-DL-master\Speech Emotion Recognition Using Machine (22-cp-47,22-cp-03,22-cp-55)\Deep Learning\SER_model.h5")

# Updated emotion labels to match the notebook
emotion_labels = ['neutral', 'calm', 'happy', 'sad', 'angry', 'fearful', 'disgust', 'surprised']

# Constants used in training
NUM_MFCC = 40  # as in training
INPUT_SHAPE = (40, 1)

# === AUDIO PREPROCESSING FUNCTION ===
def preprocess_audio(audio_file):
    signal, sr = librosa.load(audio_file)  # Use default sampling rate to match notebook

    # Extract MFCC features (40) and compute mean
    mfccs = np.mean(librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=40).T, axis=0)

    # Reshape for CNN input: (1, 40, 1)
    mfccs = np.expand_dims(mfccs, axis=1)
    mfccs = np.expand_dims(mfccs, axis=0)
    return mfccs

# === PREDICTION FUNCTION ===
def classify_emotion(audio_file):
    features = preprocess_audio(audio_file)
    predictions = model.predict(features)
    predicted_index = np.argmax(predictions)
    predicted_label = emotion_labels[predicted_index]
    confidence = predictions[0][predicted_index] * 100
    return f"{predicted_label} ({confidence:.2f}%)"

# === STREAMLIT USER INTERFACE ===
st.markdown(
    """
    <style>
        .centered {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 7vh;
            flex-direction: column;
            text-align: center;
        }
        .heading {
            background-color: #f76c6c;
            color: white;
            padding: 20px;
            border-radius: 8px;
            font-size: 40px;
            font-weight: bold;
        }
        .prediction {
            font-size: 30px;
            color: #ff6347;
            text-align: center;
            justify-content: center;
            align-items: center;
            border: 3px solid #ff6347;
            padding: 10px;
            border-radius: 8px;
            margin-top: 20px;
        }
    </style>
    """, 
    unsafe_allow_html=True
)

# Centered layout
st.markdown('<div class="centered">', unsafe_allow_html=True)
st.markdown('<h1 class="heading">🎵 Audio Emotion Classifier 🎤</h1>', unsafe_allow_html=True)
st.write("Upload an audio file to classify its emotion. Supported formats: WAV, MP3.")

# File uploader
audio_file = st.file_uploader("Choose an audio file...", type=["wav", "mp3"])

if audio_file is not None:
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_file.getbuffer())

    st.audio(audio_file)
    emotion = classify_emotion("temp_audio.wav")
    st.markdown(f'<div class="prediction">The Predicted Emotion is: <strong>{emotion}</strong></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
