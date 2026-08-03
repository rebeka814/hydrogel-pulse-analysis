import streamlit as st
import tempfile
import cv2
import plotly.graph_objects as go
import numpy as np
from src.processing import extract_signal 
from src.signal_analysis import get_time_axis, analyze_frequency, calculate_wave_properties

st.title("Hydrogel pulse analysis")
st.markdown("In this app you can analyse the pulse of an hydrogel by video.")

pixel_size = st.sidebar.number_input("Pixel size (micrometer)", value=0.05, format="%.4f")

st.sidebar.markdown("Zone 1: pulse measure (green)")
x = st.sidebar.number_input("x", value=530)
y = st.sidebar.number_input("y", value=260)
w = st.sidebar.number_input("width", value=20)
h = st.sidebar.number_input("height", value=20)

st.sidebar.markdown("Zone 2: speed measure (blue)")
x2 = st.sidebar.number_input("x\'", value=x + 100)
y2 = st.sidebar.number_input("y\'", value=y)

distance_val = st.sidebar.slider("Peak distance (s)", min_value=0.01, max_value=2.00, value=0.17, step=0.01)
prominence_val = st.sidebar.slider("Peak prominence", min_value=0.0, max_value=5.0, value=0.0, step=0.05)

uploaded_file = st.sidebar.file_uploader("Hydrogel video", type=["avi", "mp4"])
if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.avi') as tfile: #create a temporary file named tfile
        tfile.write(uploaded_file.read()) #store the uploaded video in tfile
        temp_video_path = tfile.name
    cap = cv2.VideoCapture(temp_video_path) #open the video file
    video_width, video_height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_shape = (video_width, video_height)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_idx = st.slider("Preview frame index", 0, total_frames - 1, 0)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    ret, frame = cap.read() #read the first frame and store it in 'frame'
    cap.release() #close the video
    if ret:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cv2.rectangle(frame_rgb, (x, y), (x + w, y + h), (0, 255, 0), 2) 
        st.image(frame_rgb, caption=f"Preview of the calculating zone (green zone) - Frame {frame_idx}/{total_frames} - Picture size: {video_shape}") #dispay the image 'frame'

        intensity, fps = extract_signal(temp_video_path, x, y, w, h)
        time_axis = get_time_axis(intensity, fps)
        t_min_val = float(time_axis[0])
        t_max_val = float(time_axis[-1])
        selected_range = st.sidebar.slider("Time window to keep (s)", min_value=t_min_val, max_value=t_max_val, value=(t_min_val, t_max_val), step=0.1)
        mask = (time_axis >= selected_range[0]) & (time_axis <= selected_range[1])
        time_axis_filtered = time_axis[mask]
        intensity_filtered = intensity[mask]
        prom_param = prominence_val if prominence_val > 0 else None #avoiding bugs with prominence
        peaks, period, freq, smoothed_intensity = analyze_frequency(intensity_filtered, fps, distance=distance_val, prominence=prom_param)

        col1, col2  = st.columns(2)
        col1.metric("Frequency (Hz)", f"{freq:.5f}") #display metric
        col2.metric("Period (s)", f"{period:.5f}")
        fig = go.Figure() #initialize a figure
        fig.add_trace(go.Scatter(x=time_axis_filtered, y=intensity_filtered, mode="lines", name="Initial signal", line=dict(color="#D3D3D3")))
        fig.add_trace(go.Scatter(x=time_axis_filtered, y=smoothed_intensity, mode="lines", name="Smoothed signal", line=dict(color="blue")))
        if len(peaks) > 0:
            fig.add_trace(go.Scatter(x=time_axis_filtered[peaks], y=smoothed_intensity[peaks], mode="markers", name="Detected peaks", marker=dict(color="red", size=7, symbol="cross")))
        fig.update_layout(title="Hydrogel pulse signal",xaxis_title="Time (s)", yaxis_title="Mean intensity", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True) #displays the plot

        intensity2, _ = extract_signal(temp_video_path, x2, y2, w, h)
        intensity2_filtered = intensity2[mask]
        peaks2, _, _, smoothed2 = analyze_frequency(intensity2_filtered, fps, distance=distance_val, prominence=prom_param)
        distance_px = np.sqrt((x2 - x)**2 + (y2 - y)**2)
        speed, wavelength, distance_um = calculate_wave_properties(peaks, peaks2, fps, distance_px, pixel_size, period)
        col1, col2 = st.columns(4)
        #col1.metric("Frequency", f"{freq:.3f} Hz")
        #col2.metric("Period", f"{period:.3f} s")
        col1.metric("Speed", f"{speed:.2f} um/s")
        col2.metric("Wavelength", f"{wavelength:.2f} um")

st.success("Success")

