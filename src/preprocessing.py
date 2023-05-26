from scipy.signal import filtfilt, butter, resample
from sklearn.preprocessing import StandardScaler


def remove_basline_wander(data, sampling_rate=360, cutoff_freq=0.05):
    """
    Remove baseline wander from ECG data using a high-pass filter. The high-pass filter will remove all frequencies
    below the cutoff frequency. The cutoff frequency should be set to the lowest frequency that is still considered
    baseline wander and not part of the ECG signal. For example, baseline wander is typically between 0.05 Hz and
    0.5 Hz. Therefore, a cutoff frequency of 0.05 Hz is a good starting point. However, if the ECG signal contains
    low-frequency components of interest, such as the T wave or P wave, then a higher cutoff frequency may be necessary
    to avoid over-filtering and loss of important ECG signal components.
    See https://en.wikipedia.org/wiki/High-pass_filter for more information on high-pass filters.

    :param data: ECG data as a 1-dimensional numpy array.
    :type data: numpy array
    :param sampling_rate: Sampling rate of ECG data (Hz), defaults to 360.
    :type sampling_rate: int, optional
    :param cutoff_freq: cutoff frequency of high-pass filter (Hz), defaults to 0.05.
    :type cutoff_freq: float, optional

    :return: ECG data with baseline wander removed.
    :rtype: numpy array
    """
    # Define filter parameters Nyquist frequency - The highest frequency that can be represented given the sampling
    # frequency. Nyquist Frequency is half the sampling rate (in Hz).
    nyquist_freq = 0.5 * sampling_rate
    # Filter order - The higher the order, the steeper the filter roll-off (i.e. the more aggressive the filter is at
    # removing frequencies outside the passband).
    filter_order = 3
    # Apply high-pass filter
    b, a = butter(filter_order, cutoff_freq / nyquist_freq, 'highpass')
    filtered_data = filtfilt(b, a, data)

    return filtered_data


def remove_noise(data, sampling_rate=360, lowcut=0.5, highcut=45):
    """
    Remove noise from ECG data using a band-pass filter. The band-pass filter will remove all frequencies below the
    lowcut frequency and above the highcut frequency. The lowcut frequency should be set to the lowest frequency that
    is still considered noise and not part of the ECG signal. For example, noise is typically between 0.5 Hz and 45
    Hz. Therefore, a lowcut frequency of 0.5 Hz is a good starting point. However, if the ECG signal contains
    low-frequency components of interest, such as the T wave or P wave, then a higher lowcut frequency may be
    necessary to avoid over-filtering and loss of important ECG signal components. For this reason,
    a lowcut frequency of 5 Hz is also a good starting point. The lowcut frequency can be adjusted as needed. The
    highcut frequency should be set to the highest frequency that is still considered noise and not part of the ECG
    signal. For example, noise is typically between 0.5 Hz and 45 Hz. Therefore, a highcut frequency of 45 Hz is a
    good starting point. However, if the ECG signal contains high-frequency components of interest, such as the QRS
    complex, then a lower highcut frequency may be necessary to avoid over-filtering and loss of important ECG signal
    components. For this reason, a highcut frequency of 15 Hz is also a good starting point. The highcut frequency
    can be adjusted as needed. See https://en.wikipedia.org/wiki/Band-pass_filter for more information on band-pass
    filters.

    :param data: ECG data as a 1-dimensional numpy array.
    :type data: numpy array
    :param sampling_rate: The sampling rate of ECG data (Hz), defaults to 360.
    :type sampling_rate: int, optional
    :param lowcut: The lowcut frequency of band-pass filter (Hz), defaults to 0.5.
    :type lowcut: float, optional
    :param highcut: The highcut frequency of band-pass filter (Hz), defaults to 45.
    :type highcut: float, optional

    :return: ECG data with noise removed
    :rtype: numpy array
    """
    # Define filter parameters
    nyquist_freq = 0.5 * sampling_rate
    # Define cutoff frequencies (remove all frequencies below lowcut and above highcut)
    low = lowcut / nyquist_freq
    high = highcut / nyquist_freq
    # Initialize filter
    b, a = butter(4, [low, high], btype='band')
    # Apply filter twice (combined filter) to remove forward and reverse phase shift. See
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.filtfilt.html for more information on filtfilt.
    filtered_data = filtfilt(b, a, data)

    return filtered_data


def preprocess_ecg(data, sampling_rate=1000, new_sampling_rate=360):
    # Remove basline wander using highpass filter
    filtered_data = remove_basline_wander(data=data, sampling_rate=sampling_rate)
    # Remove noise from ECG data using bandpass filter
    filtered_data = remove_noise(data=filtered_data, sampling_rate=sampling_rate)
    # Resample ECG data to a new sampling rate
    if new_sampling_rate is not None and new_sampling_rate != sampling_rate:
        filtered_data = resample(filtered_data, int(len(filtered_data) * new_sampling_rate / sampling_rate))
    # Normalize ECG data to have zero mean and unit variance
    scaler = StandardScaler()
    normalized_data = scaler.fit_transform(filtered_data.reshape(-1, 1)).reshape(-1)

    return normalized_data
