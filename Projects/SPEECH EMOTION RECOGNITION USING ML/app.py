import streamlit as st
import numpy as np
import librosa
from tensorflow.keras.models import load_model

# Load your trained CNN model
model = load_model('SER_model.h5')  

# Emotion labels (update if you trained differently)
emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

# Constants based on your CNN input
NUM_MFCC = 40  # based on your actual CNN code
INPUT_SHAPE = (40, 1)  # from model.add(Conv1D(..., input_shape=(40,1)))

# Preprocessing function
def preprocess_audio(audio_file):
    signal, sr = librosa.load(audio_file, sr=None)
    mfccs = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=NUM_MFCC)
    mfccs_mean = np.mean(mfccs.T, axis=0)  # get shape (40,)
    mfccs_mean = mfccs_mean.reshape(1, 40, 1)  # shape expected by CNN
    return mfccs_mean

# Prediction function
def classify_emotion(audio_file):
    features = preprocess_audio(audio_file)
    predictions = model.predict(features)
    predicted_label = emotion_labels[np.argmax(predictions)]
    return predicted_label

# Streamlit UI
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
