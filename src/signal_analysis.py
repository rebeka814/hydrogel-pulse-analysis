import numpy as np
from scipy.signal import find_peaks
from scipy.signal import savgol_filter

def get_time_axis(intensity, fps):  
    frame_nbr = np.arange(0,len(intensity),1)
    time_axis = frame_nbr/fps
    return time_axis

def analyze_frequency(intensity, fps, distance=1/6, prominence=None):
    smoothed_intensity = savgol_filter(intensity, 11, 3) #smoothing the curve
    smoothed_intensity = (smoothed_intensity-np.min(smoothed_intensity))/(np.max(smoothed_intensity)-np.min(smoothed_intensity)) #normalizing the curve
    peaks, _ = find_peaks(smoothed_intensity, distance=int(fps*distance), prominence=prominence) 
    if len(peaks) < 2: 
        return peaks, 0.0, 0.0, smoothed_intensity    # impossible to calculate period with less than 2 peaks
    period = np.diff(peaks)                          
    T = np.mean(period)/fps
    f = 1/T
    return peaks, T, f, smoothed_intensity
