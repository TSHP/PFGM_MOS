"""An example of showing geographic data."""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk
import os
import random
import uuid
from functools import partial

def load_audio_samples():
    audio_files = []
    for path, subdirs, files in os.walk(AUDIO_DIR):
        for name in files:
            audio_files.append(os.path.join(path, name))

    return audio_files

AUDIO_DIR = "data"   
NUM_ROUNDS = 3

def initialize_app():
    st.session_state.uuid = str(uuid.uuid4())
    st.session_state.audio_files = load_audio_samples()
    random.shuffle(st.session_state.audio_files)
    st.session_state.run = 0
    st.session_state.round = 0
    st.session_state.disabled = False
    st.session_state.results = pd.DataFrame(columns=['round','file','score'])
    st.session_state.choices = []
    st.session_state.last_value_set = False

if st.session_state.get("run") is None:
    initialize_app()

def disable_survey_button():
    st.session_state.disabled = True

def increment_run():
    st.session_state.results.loc[st.session_state.round * len(st.session_state.get("audio_files")) + st.session_state.run, ] = [st.session_state.round, st.session_state.choices[st.session_state.round * len(st.session_state.get("audio_files")) + st.session_state.run], -1]
    st.session_state.run += 1
    if st.session_state.run == len(st.session_state.get("audio_files")):
        st.session_state.run = 0
        st.session_state.round += 1
        random.shuffle(st.session_state.audio_files)

def run():
    st.title("Audio Generation Opinion Survey")
    placeholder_description = st.empty()
    placeholder_description.markdown(
        """
    For our deep learning project, we explored the capabilities of the Poisson Flow Generative Model (PFGM) for audio generation. 
    To evaluate the model, we aim to compute the Mean Opinion Score (MOS) in order to compare it with current audio generation models.


    To achieve this, we've prepared this survey consisting of audio samples generated by various audio generation models including the PFGM.


    The survey is split into three rounds with 40 audio samples (1 second long) per round. Each round consists of the same 40 samples but in randomized order.
    In each audio sample, a number from 0-9 is spoken and a dropdown field is provided to score the audio sample from 1 (Worst Score) to 5 (Best Score).


    The score given to a sample should reflect the audio quality, how easily the speaker is understood and how natural the spoken digit sounds.


    If the audio is not loaded properly, please select the "Unable to Assign a Score" value from the dropdown field.


    The survey takes no more than 15 minutes and we would gladly appreciate your feedback.


    Thank you very much in advance!
    """
    )
    
    placeholder = st.empty()
    btn = placeholder.button('Start Survey', disabled=st.session_state.get("disabled", False), on_click=disable_survey_button, key='1')
        
    if (st.session_state.get("disabled", False) and st.session_state.round < NUM_ROUNDS) or (st.session_state.get("disabled", False) and not st.session_state.last_value_set):
        st.subheader(f"Round {st.session_state.round + 1}")
        st.text(f"Sample {st.session_state.run + 1} / {len(st.session_state.get('audio_files'))}")
        with st.form("audio_form", clear_on_submit=True):
            placeholder.empty()
            audio_file_path = st.session_state.get("audio_files")[st.session_state.run]
            st.session_state.choices.append(audio_file_path)
            audio_file = open(st.session_state.choices[st.session_state.round * len(st.session_state.get("audio_files")) + st.session_state.run], 'rb')
            audio_bytes = audio_file.read()

            st.audio(audio_bytes, format='audio/wav')
            score = st.selectbox("Opinion Score (1: Lowest, 5: Highest)", ["Unable to Assign a Score", 1, 2, 3, 4, 5], index=1)
            next_button = st.form_submit_button('Next', disabled=False, on_click=increment_run)
            
            if next_button:
                st.session_state.results.loc[len(st.session_state.results) - 1, "score"] = score
                st.session_state.results.to_csv(f"results/{st.session_state.uuid}.csv")
                if st.session_state.round == NUM_ROUNDS:
                    st.session_state.last_value_set = True


    elif st.session_state.last_value_set:
        placeholder.empty()
        placeholder_description.empty()
        st.markdown(
        """
        Thank you for your feedback!
        """
        )
        st.session_state.results.to_csv(f"results/{st.session_state.uuid}.csv")


if __name__ == "__main__":
    run()