import numpy as np
import matplotlib.pyplot as plt
from src.processing import extract_signal
from src.signal_analysis import get_time_axis
from src.signal_analysis import analyze_frequency

if __name__ == "__main__":
    # defining test parameters
    video_path = "PEGDA 8000.avi"
    x, y, w, h = 530, 260, 20, 20

    # extracting data from modules
    intensity, fps = extract_signal(video_path, x, y, w, h)
    time_axis = get_time_axis(intensity, fps)
    peaks, T, f, smoothed_intensity = analyze_frequency(intensity, fps)

    # drawing plots
    plt.figure('Intensity')
    plt.plot(time_axis, intensity)
    #plt.plot(time_axis, smoothed_intensity)
    #plt.plot(time_axis[peaks], intensity[peaks], marker='o', linestyle='None', color='red', label='Peaks')
    plt.savefig('intensity_pulsation.png')
    plt.close('Intensity')

    plt.figure('Smoothed')
    plt.plot(time_axis, smoothed_intensity)
    plt.plot(time_axis[peaks], smoothed_intensity[peaks], marker='+', linestyle='None', color='red', label='Peaks')
    plt.savefig('smoothed_intensity.png')
    plt.close('Smoothed')

    # verifying results
    #print(T)