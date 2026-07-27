import streamlit as st
import tempfile
import cv2
import plotly.graph_objects as go
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
    with tempfile.NamedTemporaryFile(delete=False, suffix='.avi') as tfile: #create a temporary file named tfile
        tfile.write(uploaded_file.read()) #store the uploaded video in tfile
        temp_video_path = tfile.name
    cap = cv2.VideoCapture(temp_video_path) #open the video file
    ret, frame = cap.read() #read the first frame and store it in 'frame'
    cap.release() #close the video
    if ret:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cv2.rectangle(frame_rgb, (x, y), (x + w, y + h), (0, 255, 0), 2) 
        st.image(frame_rgb, caption="Preview of the calculating zone (red zone)") #dispay the image 'frame'
        intensity, fps = extract_signal(temp_video_path, x, y, w, h)
        time_axis = get_time_axis(intensity, fps)
        peaks, period, freq, smoothed_intensity = analyze_frequency(intensity, fps)
        col1, col2  = st.columns(2)
        col1.metric("Frequency (Hz)", f"{freq:.5f}") #display metric
        col2.metric("Period (s)", f"{period:.5f}")
        fig = go.Figure() #initialize a figure
        fig.add_trace(go.Scatter(x=time_axis, y=intensity, mode="lines", name="Initial signal", line=dict(color="gray", dash="dot")))
        fig.add_trace(go.Scatter(x=time_axis, y=smoothed_intensity, mode="lines", name="Smoothed signal", line=dict(color="blue")))
        if len(peaks) > 0:
            fig.add_trace(go.Scatter(x=time_axis[peaks], y=smoothed_intensity[peaks], mode="markers", name="Detected peaks", marker=dict(color="red", size=7, symbol="cross")))
        fig.update_layout(title="Hydrogel pulse signal",xaxis_title="Time (s)", yaxis_title="Mean intensity", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True) #displays the plot

st.success("Success")

