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
    #TODO
    if not header:
        header = [i for i in sig.columns]
    if rem_len:
        header = [i[0:-rem_len] for i in header]
    return sig, header


def read_chsetup(path=None, sep='\t'):
    if path:
        setup = []
        try:
            return pd.read_csv(path,sep)
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
    return pd.DataFrame({"band_names": band_names,
                         "band_lows" : band_lows,
                         "band_highs": band_highs})


def pot_abs(df, bands, fs=500, window='hanning', nperseg=256):
    """
    Return a dataframe with the abolute power of the given bands for every channel in the dataframe

    :param df: data frame with signals as rows and channels as columns
    :param fs: sampling frequency
    :param window: Desired window to use. See [get_window](https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.signal.get_window.html#scipy.signal.get_window) for a list of windows and required parameters.
    :param nperseg: Length of each segment. Defaults to 256.
    :param bands: Dataframe with the desired bands and their cut frequencies

    Window types:
    boxcar, triang, blackman, hamming, hann, bartlett, flattop, parzen, bohman, blackmanharris, nuttall, barthann, kaiser (needs beta), gaussian (needs std), general_gaussian (needs power, width), slepian (needs width), chebwin (needs attenuation)
    """
    n_bands = bands.size
    abs_df  = pd.DataFrame(columns=list(df.columns.values))
    for band in bands:
            print(band)
    for channel in df:
        f, ps = signal.welch(df[channel], fs, window=window, nperseg=nperseg)
       

def pot_rel(absl):
    raise NotImplementedError
