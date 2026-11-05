import pandas as pd
import numpy as np
import biosppy
import scipy

def get_respiratory_rate(
    signal: pd.Series,
    srate: float = 1000.0,
    apply_smooth: bool = False,
    mode: str = "biosppy",
):
    """
    Estimate respiratory rate from a respiratory waveform.

    Parameters
    ----------
    signal : pandas.Series
        Respiratory signal. The Series index is assumed to contain the
        original sample indices and is used to map detected events back
        to the source signal.
    srate : float, default=1000.0
        Sampling frequency in Hz.
    apply_smooth : bool, default=False
        If True, apply a moving-average smoothing window of 3 seconds
        before respiratory rate estimation.
    mode : {"biosppy", "scipy"}, default="biosppy"
        Method used for respiratory cycle detection:

        - "biosppy": Uses biosppy.signals.resp.resp(), which detects
          respiratory cycles from zero-crossings of the filtered signal.
        - "scipy": Uses scipy.signal.find_peaks() with a prominence
          threshold derived from the signal IQR.

    Returns
    -------
    br_idx : numpy.ndarray
        Sample indices of detected breaths.
    br_bpm : numpy.ndarray
        Instantaneous respiratory rate (breaths/minute) associated with
        each detected breath. The first value is NaN for the SciPy method
        because no preceding interval exists.
    """

    if not isinstance(signal, pd.Series):
        raise TypeError("signal must be a pandas.Series with sample indices.")

    values = signal

    if apply_smooth:
        values = smooth(values, box_pts=int(3 * srate))

    if mode == "biosppy":
        ts, filtval, zeroval_i, br_time, br_val = biosppy.signals.resp.resp(
            signal=values,
            sampling_rate=srate,
            units=None,
            path=None,
            show=False,
        )

        br_idx = (
            (np.asarray(br_time, dtype=np.float64) * srate).astype(int)
            + int(values.index[0])
        )
        br_bpm = 60.0 * br_val

    elif mode == "scipy":
        med_IQR_CW = 2.09

        q75, q25 = np.percentile(values, [75, 25])
        iqr = q75 - q25

        if iqr / med_IQR_CW < 0.25 or iqr / med_IQR_CW > 3:
            br_idx = np.array(int(values.index[0]))
            br_bpm = np.array([-1.0])
        else:
            br_idx = scipy.signal.find_peaks(
                values,
                prominence=iqr / 4,
                distance=int(srate * 1.5),
            )[0]

            br_bpm = np.concatenate(
                ([np.nan], 60.0 * srate / np.diff(br_idx))
            )

    else:
        raise ValueError("mode must be 'biosppy' or 'scipy'.")

    return br_idx, br_bpm

def smooth(y, box_pts):
    box = np.ones(box_pts) / box_pts
    y_smooth = np.convolve(y.to_numpy(), box, mode="same")

    if isinstance(y, pd.Series):
        return pd.Series(y_smooth, index=y.index, name=y.name)

    return y_smooth

