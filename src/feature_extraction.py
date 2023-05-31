import numpy as np
from biosppy.signals import ecg
from scipy.signal import welch
import pandas as pd


def create_windows(df, time_column, window_size=5.0, window_slicing_method='time_related'):
    """
    Slices a dataframe into windows of a given size. The windows can be sliced in different ways. The windows are returned as a generator of dataframes. The dataframe must have a column containing timestamps and be indexed by it.

    :param df: The dataframe to slice.
    :type df: pandas.DataFrame
    :param time_column: The name of the column containing the timestamps.
    :type time_column: str
    :param window_size: The size of the windows in seconds.
    :type window_size: int
    :param window_slicing_method: The method used to slice the windows.
    :type window_slicing_method: str

    :return: A generator of dataframes containing the windows.
    :rtype: generator
    """
    # Convert the timestamp column to datetime if it's not already
    if not pd.api.types.is_datetime64_ns_dtype(df[time_column]):
        df[time_column] = pd.to_datetime(df[time_column])

    # Slice the dataframe into windows
    if window_slicing_method == 'time_related':
        # Resample the dataframe every x seconds
        result_dfs = [group for _, group in df.groupby(pd.Grouper(key=time_column, freq=f'{window_size}S'))]
        return result_dfs
    elif window_slicing_method == 'label_related_before':
        pass
    elif window_slicing_method == 'label_related_after':
        pass
    elif window_slicing_method == 'label_related_centered':
        pass
    else:
        raise ValueError(f'window_slicing_method {window_slicing_method} not supported')


def hrv_features(ecg_signal, fs):
    # Compute RR intervals from ECG data
    rpeaks, = ecg.hamilton_segmenter(signal=ecg_signal, sampling_rate=fs)
    rr_intervals = np.diff(rpeaks) / fs

    # Compute time domain features from RR intervals
    mean_rr = np.mean(rr_intervals)
    sdnn = np.std(rr_intervals)
    rmssd = np.sqrt(np.mean(np.square(np.diff(rr_intervals))))
    nn50 = np.sum(np.abs(np.diff(rr_intervals)) > 0.05)
    pnn50 = nn50 / len(rr_intervals)

    # Compute frequency domain features from RR intervals
    freq, power = welch(rr_intervals, fs=fs)
    lf_band = np.sum(power[(freq >= 0.04) & (freq <= 0.15)])
    hf_band = np.sum(power[(freq >= 0.15) & (freq <= 0.4)])
    lf_hf_ratio = lf_band / hf_band

    # Return HRV features as a dictionary
    features = {
        'mean_rr': mean_rr,
        'sdnn': sdnn,
        'rmssd': rmssd,
        'nn50': nn50,
        'pnn50': pnn50,
        'lf_band': lf_band,
        'hf_band': hf_band,
        'lf_hf_ratio': lf_hf_ratio,
    }
    return features
