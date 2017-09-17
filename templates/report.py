import pandas as pd
import numpy as np
from scipy import signal


def read_sig(path, n_channels, header=None, sep='\t', rem_len=5):
    """
    Read signal in tabular format (csv, tsv)
    :param path: path of the tabular data file
    :param n_channels: number of channels to be handled. Extra channels will be ignored
    :param sep: tabular data separator. Default `tab`
    :param rem_len: Length of removed characters from column names. Used to remove A1A2 reference.
    """
    signals = sig = []
    try:
        signals = pd.read_csv(path, sep=sep)
        sig = signals.iloc[:, 0:n_channels]
    except:
        raise IOError(str("Error: could not read file " + path))
    # TODO
    if not header:
        header = [i for i in sig.columns]
    if rem_len:
        header = [i[0:-rem_len] for i in header]
    sig.columns = header
    return sig


def read_chsetup(path=None, sep='\t'):
    if path:
        setup = []
        try:
            return pd.read_csv(path, sep)
        except:
            raise IOError()
    setup = np.array(np.mat('''0.3   1.0    "Fp1";
                               0.7   1.0    "Fp2";
                               0.5   0.725  "Fz" ;
                               0.25  0.775  "F3" ;
                               0.75  0.775  "F4" ;
                               0.0   0.85   "F7" ;
                               1.0   0.85   "F8" ;
                               0.5   0.5    "Cz" ;
                               0.25  0.5    "C3" ;
                               0.75  0.5    "C4" ;
                               0.0   0.5    "T3" ;
                               1.0   0.5    "T4" ;
                               0.5   0.275  "Pz" ;
                               0.25  0.225  "P3" ;
                               0.75  0.225  "P4" ;
                               0.0   0.15   "T5" ;
                               1.0   0.15   "T6" ;
                               0.3   0.0    "O1" ;
                               0.7   0.0    "O2"'''))
    return setup


def create_bands(band_names, band_lows, band_highs):
    df = pd.DataFrame({"name": band_names,
                       "low" : band_lows,
                       "high": band_highs})
    return df[["name", "low", "high"]]


def psd(sig, fs=500, window='hanning', nperseg=1):
    """
    :param fs: sampling frequency
    :param window: Desired window to use. See [get_window](https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.signal.get_window.html#scipy.signal.get_window) for a list of windows and required parameters.
    :param nperseg: Segments per second. Defaults to 1.

    Window types:
    boxcar, triang, blackman, hamming, hann, bartlett, flattop, parzen, bohman, blackmanharris, nuttall, barthann, kaiser (needs beta), gaussian (needs std), general_gaussian (needs power, width), slepian (needs width), chebwin (needs attenuation)
    """
    if nperseg > fs:
        raise AssertionError("Sampling frequency cannot be bigger than window size")
    psds = sig.copy().apply(signal.welch,
                            axis=0,
                            args=(fs,
                                  window,
                                  nperseg * fs)
                            )
    psd_df = pd.DataFrame(columns=list(sig.columns.values),
                          index=psds[0][0])
    for column, i in zip(psd_df, psds):
        psd_df[column] = i[1]
    return psd_df


def sig_to_frequency(sig, fs=500):
    """
    Return the power spectrum and phase of a given signal as data frames
    :param sig: Dataframe containing one signal per column
    :param fs: Sampling frequency
    """
    freq_df = sig.copy().apply(simple_fft,
                               axis=0,
                               args=(fs,
                                     False)
                               )
    freq_df.index = simple_fft(freq_df[[0]], fs=fs,f=True)
    phase_df = freq_df.copy().apply(np.angle, axis=0)
    psd_df = freq_df.apply(lambda x: (np.abs(x) / sig.size)**2,
                           axis=0)
    return psd_df, phase_df


def simple_fft(sig, fs=500, f=False):
    """
    receive single signal and return either fourier transform, or frequencies
    :param sig: real signal to be converted
    :param fs: sampling frequency in hertz, defaults to 500
    :param f: frequency flag. If True, returns only the frequencies array
    """
    # s = sig.tolist()
    N = sig.size
    time_step = 1/fs
    freqs = np.fft.fftfreq(N,time_step)
    idx = np.argsort(freqs)
    if f:
        return freqs[idx]
    else:
        ps = np.fft.fft(sig)
        return ps[idx]


def pot_abs(psd_df, bands):
    """
    Return a dataframe with the abolute power of the given bands for every channel in the dataframe

    :param df: data frame with power spectrum as rows and channels as columns
    :param bands: Dataframe with the desired bands and their cut frequencies
    """
    abs_df  = pd.DataFrame(columns=list(psd_df.columns.values),
                           index=bands["name"])
    for channel in psd_df:
        v = []
        for index, row in bands.iterrows():
            pot = float(psd_df[row["low"]:row["high"]][channel].sum())
            v.append(pot)
        abs_df[channel] = v
        abs_df.index = bands["name"]
    return abs_df


def pot_rel(abs_df):
    """
    Return relative power per band, based on absolute power.
    :param abs_df: Dataframe with absolute power where rows are bands and columns are channels
    """
    rel_df = abs_df.copy()
    for col in abs_df:
        rel_df[col] = abs_df[col] / sum(abs_df[col])
    return rel_df


def coh(sig, bands, fs=500):
    """
    Return the coherence between signals of a dataframe averaged over a frequency band.
    :param sig: dataframe with a signal for every column
    :param bands: dataframe with a column for name, lower inclusive frequency and higher non-inclusive frequency.
    :param fs: sampling frequency
    """
    cols = [i + "-" + j for i in sig for j in sig]
    coh_df = pd.DataFrame(columns=cols)
    coh_temp = pd.DataFrame()
    for col1 in sig:
        for col2 in sig:
            freq, coh = signal.coherence(sig[col1],
                                         sig[col2],
                                         fs)
            coh_temp["temp"] = coh
            coh_temp.index = freq
            v = []
            for index, row in bands.iterrows():
                band_coh = float(coh_temp[row["low"]:row["high"]].mean())  # TODO: check if average is correct
                v.append(band_coh)

            coh_df[col1 + "-" + col2] = v

    coh_df.index = bands["name"]
    return coh_df


def phase_dif(phase_df, bands):
    """
    """
    cols = [i + "-" + j for i in phase_df for j in phase_df]
    pdif_df = pd.DataFrame(columns=cols)
    ph_temp = pd.DataFrame()
    for col1 in phase_df:
        for col2 in phase_df:
            ph_temp = phase_df[col1]-phase_df[col2]
            ph_temp.index = phase_df.index
            v = []
            for index, row in bands.iterrows():
                v.append(float(ph_temp[row["low"]:row["high"]].mean()))
            pdif_df[col1 + "-" + col2] = v
    pdif_df.index = bands["name"]
    return pdif_df
