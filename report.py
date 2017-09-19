import pandas as pd
import numpy as np
from scipy import signal
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib
import scipy.interpolate



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
    psd_df = freq_df.apply(lambda x: (np.abs(x) / len(sig.index))**2,
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
    N = len(sig.index)
    time_step = 1/fs
    freqs = np.fft.fftfreq(N,time_step)
    idx = np.argsort(freqs)
    if f:
        return freqs[idx]
    else:
        ps = np.fft.fft(sig)
        return ps[idx]


def band_peaks(psd_df, bands):
    """
    Return a dataframe with the peak frequency for every band in every channel

    :param psd_df: DataFrame with power spectrum density as rows and channels as columns
    :param bands: DataFrame with the desired bands and their cut frequencies
    """
    A = np.array([i for i in psd_df.columns.values for _ in (0,1)])
    B = np.array(['Freq', 'Pot']*len(psd_df.columns.values))
    W = [i for i in zip(A,B)]

    max_df = pd.DataFrame(columns=pd.MultiIndex.from_tuples(W))
    for channel in psd_df:
        pots  = []
        freqs = []
        for index, row in bands.iterrows():
            freq = float(psd_df[row["low"]:row["high"]][channel].idxmax())
            pot  = float(psd_df[row["low"]:row["high"]][channel].max())
            pots.append(pot)
            freqs.append(freq)
        max_df[channel, "Freq"] = freqs
        max_df[channel, "Pot"]  = pots
        max_df.index = bands["name"]
    return max_df

def pot_abs(psd_df, bands):
    """
    Return a dataframe with the abolute power of the given bands for every channel in the dataframe

    :param psd_df: DataFrame with power spectrum density as rows and channels as columns
    :param bands: DataFrame with the desired bands and their cut frequencies
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
    Return a dataframe with the phase difference for every band in every channel
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


def headmap(data, setup, rel=False, N=300):
    x = setup['x'].tolist()
    y = setup['y'].tolist()
    plots = []
    pos = {}
    for i,row in setup.iterrows():
        pos[row["name"]] = (row['x'],row['y'])
    radius = .5         # radius
    xy_center = [.5,.5]   # center of the plot
    for ix, row in data.iterrows():
        z = row.tolist()

        xi = np.linspace(-.1, 1.1, N)
        yi = np.linspace(-.1, 1.1, N)
        zi = scipy.interpolate.griddata((x, y), z, (xi[None,:], yi[:,None]), method='cubic')

        # set points > radius to not-a-number. They will not be plotted.
        # the dr/2 makes the edges a bit smoother
        dr = xi[1] - xi[0]
        for i in range(N):
            for j in range(N):
                r = np.sqrt((xi[i] - xy_center[0])**2 + (yi[j] - xy_center[1])**2)
                if (r - dr/2) > radius:
                    zi[j,i] = "nan"


        G = nx.Graph()
        G.add_nodes_from(pos)
        nx.set_node_attributes(G,'pos',pos)
        fig, ax = plt.subplots(1,1,figsize=(7,7))
        ax.set_aspect('equal')

        # nodes
        nx.draw_networkx_nodes(G,pos,node_size=70, ax=ax, node_color='cyan')
        # labels
    #     nx.draw_networkx_labels(G,pos,font_size=20,font_family='sans-serif')

        # use different number of levels for the fill and the lines
        im = ax.contourf(xi, yi, zi, 60, cmap = plt.cm.viridis, zorder = 1)
        ax.contour(xi, yi, zi, 15, colors = "grey", zorder = 2)

        ax.axis("off")
        ax.set_title("Absolute Power band: "+ix)
        if rel:
            ax.set_title("Relative Power band: "+ix)

        # HEAD
        circle = matplotlib.patches.Circle(xy = xy_center, radius = radius, edgecolor = "k", facecolor = "none")
        ax.add_patch(circle)
        # add two ears
        circle = matplotlib.patches.Ellipse(xy = [0,.5], width = 0.125, height = .25, angle = 0, edgecolor = "k", facecolor = "w", zorder = 0)
        ax.add_patch(circle)
        circle = matplotlib.patches.Ellipse(xy = [1,.5], width = 0.125, height = .25, angle = 0, edgecolor = "k", facecolor = "w", zorder = 0)
        ax.add_patch(circle)
        # add a nose
        xy = [[.4,.8], [.5,1.075],[.6,.8]]
        polygon = matplotlib.patches.Polygon(xy = xy, edgecolor = "k", facecolor = "w", zorder = 0)
        ax.add_patch(polygon) 


        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        fig.colorbar(im, cax=cax)

        # plt.show()

        plots.append((fig,ax))
    return plots

def cor_headnet(cor_df, pos, tresholds=[-0.8,0.8]):
    """
    Return correlation network from dataframe and positions
    """
    G = nx.Graph()
    for index, row in  cor_df.iterrows():
        for channel, dat in row.iteritems():
            G.add_edge(index,
                    channel,
                    weight=dat)

    # print(G.edges(data=True))
    nx.set_node_attributes(G,'pos',pos)
    fig, ax = plt.subplots(1,1,figsize=(7,7))
    # nodes
    nx.draw_networkx_nodes(G,pos,node_size=70, ax=ax)
    # edges
    elarge   = [(u,v,d) for (u,v,d) in G.edges(data=True) if d['weight'] > tresholds[1]]
    weights1 = [i[2]["weight"] for i in elarge]

    emedium  = [(u,v,d) for (u,v,d) in G.edges(data=True) if tresholds[0] < d['weight'] <= tresholds[1]]
    weights2 = [i[2]["weight"] for i in emedium]

    esmall   = [(u,v,d) for (u,v,d) in G.edges(data=True) if d['weight'] <= tresholds[0]]
    weights3 = [i[2]["weight"] for i in esmall]

    im = nx.draw_networkx_edges(G,pos,
                                edgelist=elarge,
                                alpha=1,
                                width=5,
                                edge_color=weights1,
                                edge_cmap=plt.cm.RdBu,
                                edge_vmin=0,
                                edge_vmax=1,
                                ax=ax)
    nx.draw_networkx_edges(G,pos,
                        edgelist=emedium,
                        alpha=0.05,
                        width=5,
                        edge_color=weights2,
                        edge_cmap=plt.cm.RdBu,
                        edge_vmin=0,
                        edge_vmax=1,
                        ax=ax)
    nx.draw_networkx_edges(G,pos,
                        edgelist=esmall,
                        alpha=1,
                        width=5,
                        edge_color=weights2,
                        edge_cmap=plt.cm.RdBu,
                        edge_vmin=0,
                        edge_vmax=1,
                        ax=ax)
    # labels
    nx.draw_networkx_labels(G,pos,font_size=20,font_family='sans-serif')
    ax.axis("off")
    # plt.savefig("weighted_graph.png") # save as png
    ax.set_title("Average correlation")

    # HEAD
    xy_center = [.5,.5]   # center of the plot
    radius = .6         # radius
    circle = matplotlib.patches.Circle(xy = xy_center, radius = radius, edgecolor = "k", facecolor = "none")
    ax.add_patch(circle)


    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    fig.colorbar(im, cax=cax, ticks=[0, .5, 1])

    # plt.show() # display
    return fig, ax


def coh_headnet(coh_df, pos, treshold=0.8):
    """
    Return coherence network from dataframe and positions
    """
    plots = []
    for index, band in  coh_df.iterrows():
        G = nx.Graph()
        for channel_pair, dat in band.iteritems():
            G.add_edge(channel_pair.split('-')[0],
                    channel_pair.split('-')[1],
                    weight=dat)
    #     print(G.edges(data=True))
    #     print(weights)
        nx.set_node_attributes(G,'pos',pos)
        fig, ax = plt.subplots(1,1,figsize=(7,7))
        # nodes
        nx.draw_networkx_nodes(G,pos,node_size=70, ax=ax)
        # edges
        elarge=[(u,v,d) for (u,v,d) in G.edges(data=True) if d['weight'] > treshold]
        weights1 = [i[2]["weight"] for i in elarge]
        esmall=[(u,v,d) for (u,v,d) in G.edges(data=True) if d['weight'] <= treshold]
        weights2 = [i[2]["weight"] for i in esmall]

        im = nx.draw_networkx_edges(G,pos,
                                    edgelist=elarge,
                                    alpha=1,
                                    width=5,
                                    edge_color=weights1,
                                    edge_cmap=plt.cm.viridis,
                                    edge_vmin=0,
                                    edge_vmax=1,
                                    ax=ax)
        nx.draw_networkx_edges(G,pos,
                            edgelist=esmall,
                            alpha=0.05,
                            width=5,
                            edge_color=weights2,
                            edge_cmap=plt.cm.viridis,
                            edge_vmin=0,
                            edge_vmax=1,
                            ax=ax)
        # labels
        nx.draw_networkx_labels(G,pos,font_size=20,font_family='sans-serif')
        ax.axis("off")
        # plt.savefig("weighted_graph.png") # save as png
        ax.set_title("Coherence "+index)

        # Head
        xy_center = [.5,.5]   # center of the plot
        radius = .6         # radius
        circle = matplotlib.patches.Circle(xy = xy_center, radius = radius, edgecolor = "k", facecolor = "none")
        ax.add_patch(circle)
    

        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        fig.colorbar(im, cax=cax, ticks=[0, .5, 1])

        # plt.show() # display
        plots.append((fig, ax))
    return plots

def phs_headnet(pdif_df, pos):
    plots = []
    for index, band in  pdif_df.iterrows():
        G = nx.Graph()
        for channel_pair, dat in band.iteritems():
            G.add_edge(channel_pair.split('-')[0],
                    channel_pair.split('-')[1],
                    weight=dat)
    #     print(G.edges(data=True))
    #     print(weights)
        nx.set_node_attributes(G,'pos',pos)
        fig, ax = plt.subplots(1,1,figsize=(7,7))
        # nodes
        nx.draw_networkx_nodes(G,pos,node_size=70, ax=ax)
        # edges
        weights = [i[2]["weight"] for i in G.edges(data=True)]

        im = nx.draw_networkx_edges(G,pos,
                            alpha=1,
                            width=5,
                            edge_color=weights,
                            edge_cmap=plt.cm.RdBu,
                            edge_vmin=-np.pi,
                            edge_vmax=np.pi,
                            ax=ax)

        # labels
        nx.draw_networkx_labels(G,pos,font_size=20,font_family='sans-serif')
        ax.axis("off")
        # plt.savefig("weighted_graph.png") # save as png
        ax.set_title("Phase difference "+index)

        # HEAD
        xy_center = [.5,.5]   # center of the plot
        radius = .6         # radius
        circle = matplotlib.patches.Circle(xy = xy_center, radius = radius, edgecolor = "k", facecolor = "none")
        ax.add_patch(circle)

        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        fig.colorbar(im, cax=cax, ticks=[-np.pi, 0, np.pi]) #  ,ticklabels=["-π","0","π"])

        # plt.show() # display
        plots.append((fig,ax))
    return plots
