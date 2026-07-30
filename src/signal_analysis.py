import numpy as np
from scipy.signal import find_peaks
from scipy.signal import savgol_filter

def get_time_axis(intensity, fps):  
    frame_nbr = np.arange(0,len(intensity),1)
    time_axis = frame_nbr/fps
    return time_axis

def analyze_frequency(intensity, fps, distance=1/6, prominence=None):
    #intensity = np.nan_to_num(intensity, nan=0.0, posinf=0.0, neginf=0.0)
    if len(intensity) < 11:
        return [], 0.0, 0.0, intensity
    smoothed_intensity = savgol_filter(intensity, 11, 3) #smoothing the curve
    #smoothed_intensity = (smoothed_intensity-np.min(smoothed_intensity))/(np.max(smoothed_intensity)-np.min(smoothed_intensity)) #normalizing the curve
    peaks, _ = find_peaks(smoothed_intensity, distance=int(fps*distance), prominence=prominence) 
    if len(peaks) < 2: #impossible to calculate period with less than 2 peaks
        return peaks, 0.0, 0.0, smoothed_intensity  
    period = np.diff(peaks)                          
    T = np.mean(period)/fps
    f = 1/T
    return peaks, T, f, smoothed_intensity

def calculate_wave_properties(peaks1, peaks2, fps, distance_px, pixel_size, period):
    if len(peaks1) == 0 or len(peaks2) == 0:
        return 0.0, 0.0, 0.0
    distance_um = distance_px * pixel_size
    min_len = min(len(peaks1), len(peaks2))
    time_peaks1 = peaks1[:min_len] / fps
    time_peaks2 = peaks2[:min_len] / fps
    dt = np.mean(np.abs(time_peaks2 - time_peaks1))
    if dt == 0:
        return 0.0, 0.0, distance_um
    speed = distance_um / dt
    wavelength = speed * period
    return speed, wavelength, distance_um