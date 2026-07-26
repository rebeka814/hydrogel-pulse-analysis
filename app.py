import streamlit as st
import tempfile
import cv2
import matplotlib.pyplot as plt
from src.processing import extract_signal 
from src.signal_analysis import get_time_axis, analyze_frequency 

st.title("Hydrogel pulse analysis")
st.markdown("In this app you can analyse the pulse of an hydrogel by video.")

x = st.sidebar.number_input("x", value=530)
y = st.sidebar.number_input("y", value=260)
w = st.sidebar.number_input("width", value=20)
h = st.sidebar.number_input("height", value=20) 

uploaded_file = st.sidebar.file_uploader("Hydrogel video", type=["avi", "mp4"])
if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.avi') as tfile:
        tfile.write(uploaded_file.read())
        temp_video_path = tfile.name
    cap = cv2.VideoCapture(temp_video_path)
    ret, frame = cap.read()
    cap.release()
    if ret:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cv2.rectangle(frame_rgb, (x, y), (x + w, y + h), (255, 0, 0), 2)
        st.image(frame_rgb, caption="Preview of the calculating zon (Red zone)")
        intensity, fps = extract_signal(temp_video_path, x, y, w, h)
        time_axis = get_time_axis(intensity, fps)
        peaks, period, freq, smoothed_intensity = analyze_frequency(intensity, fps)
        col1, col2  = st.columns(2)
        col1.metric("Frequency (Hz)", f"{freq:.2f}")
        col2.metric("Period (s)", f"{period:.2f}")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(time_axis, intensity, label="Intensity", color="blue")
        if len(peaks) > 0:
            ax.plot(time_axis[peaks], intensity[peaks], "ro", label="Detected peaks")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Mean intensity")
        ax.set_title("Hydrogel pulse signal")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)



st.success("Success message")

