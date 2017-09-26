import argparse
import report as rp
import pandas as pd
import numpy as np
import pweave
import os
import shutil


class Handler:
    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)

    def onButtonPressed(self, button):
        print("Hello World!")


def create_parser(dir_path=os.path.dirname(os.path.realpath(__file__))):
    parser = argparse.ArgumentParser(prog="Reportes",
                                     description="Report creation utility for EEG signals.",
                                     add_help=True)
    parser.add_argument("--setup", "-s",
                        help="File with the channel setup")
    parser.add_argument("--bands", "-b",
                        help="File with the band setup")
    parser.add_argument("--frequency", "-f",
                        help='Samling frequency of the signals',
                        dest='fs',
                        type=int,
                        default=500)
    parser.add_argument("--template", "-t",
                        help="Markdown template to use",
                        default=os.path.join(dir_path, "templates", "main.pmd"))
    parser.add_argument("--gui", "-g",
                        help="Start with gui.",
                        action="store_true",
                        default=False)
    parser.add_argument("--input", "-i",
                        help="Input file or folder to analyze",
                        default=os.path.join(dir_path,
                                             "example",
                                             "eeg.txt"))
    parser.add_argument("--output", "-o",
                        help="Folder name to save the reports",
                        default=os.path.join(dir_path, "Reports"))
    return parser


def main():
    dir_path  = os.path.dirname(os.path.realpath(__file__))
    parser    = create_parser(dir_path)
    args      = parser.parse_args()
    fs        = args.fs  
    cache_dir = os.path.join(dir_path, "cache")
    MULTIPLE  = False

    if args.setup:
        setup = rp.read_chsetup(args.setup)
    else:
        setup = rp.read_chsetup() # TODO variable to dump
    setup = pd.DataFrame(setup)
    setup.columns = ["x","y","name"]

    if args.bands:
        # TODO: implement
        raise NotImplementedError("ERROR: Not yet implemented")
    else:
        band_names = ["delta",
                      "theta",
                      "alpha1",
                      "alpha2",
                      "beta1",
                      "beta2",
                      "gamma"]
        band_lows  = [1, 4, 8, 11, 14, 20, 31]
        band_highs = [4, 8, 11, 14, 20, 31, 50]
        bands = rp.create_bands(band_names, band_lows, band_highs)  # TODO variable to dump
    template = args.template
    files = []
    if os.path.isdir(args.input):
        files = [os.path.join(args.input, i) for i in os.listdir(args.input)]
        if len(files) > 1:
            MULTIPLE = True
    elif os.path.isfile(args.input):
        files = [args.input]
    else:
        raise IOError("ERROR: file or folder not found")

    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)

    os.makedirs(cache_dir)
    bands.to_csv(os.path.join(cache_dir, "bands"),index=False)
    setup.to_csv(os.path.join(cache_dir, "setup"),index=False)
    pd.DataFrame({"freq":[fs],
                  "output":[args.output]}).to_csv(os.path.join(cache_dir, "other"),index=False)
    n_channels = len(setup.index) # TODO: not true.

    n = 0
    for f in files:
        print("INFO: Processing file ", f)
        shutil.copyfile(f, os.path.join(cache_dir,"temp"))
        pd.DataFrame({"name":[f]}).to_csv(os.path.join(cache_dir, "name"),index=False)
        sig    = rp.read_sig(os.path.join(dir_path, "cache", "temp"), n_channels)
        psd_df, phase_df = rp.sig_to_frequency(sig, fs=fs)
        peaks_df = rp.band_peaks(psd_df, bands)
        abs_df = rp.pot_abs(psd_df, bands)
        rel_df = rp.pot_rel(abs_df)
        cor_df = sig.corr()
        coh_df = rp.coh(sig, bands, fs=fs)
        pdif_df = rp.phase_dif(phase_df, bands)

        if MULTIPLE: 
            if n==0:
                avg_psd   = np.array([psd_df.as_matrix()], np.float64)
                avg_peaks = np.array([peaks_df.as_matrix()], np.float64)
                avg_abs   = np.array([abs_df.as_matrix()], np.float64)
                avg_rel   = np.array([rel_df.as_matrix()], np.float64)
                avg_cor   = np.array([cor_df.as_matrix()], np.float64)
                avg_coh   = np.array([coh_df.as_matrix()], np.float64)
                avg_pdif  = np.array([pdif_df.as_matrix()], np.float64)
                n+=1
            avg_psd   = np.concatenate((avg_psd, [psd_df.as_matrix()]), axis=0)
            avg_peaks = np.concatenate((avg_peaks, [peaks_df.as_matrix()]), axis=0)
            avg_abs   = np.concatenate((avg_abs, [abs_df.as_matrix()]), axis=0)
            avg_rel   = np.concatenate((avg_rel, [rel_df.as_matrix()]), axis=0)
            avg_cor   = np.concatenate((avg_cor, [cor_df.as_matrix()]), axis=0)
            avg_coh   = np.concatenate((avg_coh, [coh_df.as_matrix()]), axis=0)
            avg_pdif  = np.concatenate((avg_pdif, [pdif_df.as_matrix()]), axis=0)
            n += 1
        
        psd_df.to_csv(os.path.join(cache_dir, "psd_df"))
        peaks_df.to_csv(os.path.join(cache_dir, "peaks_df"))
        abs_df.to_csv(os.path.join(cache_dir, "abs_df"))
        rel_df.to_csv(os.path.join(cache_dir, "rel_df"))
        cor_df.to_csv(os.path.join(cache_dir, "cor_df"))
        coh_df.to_csv(os.path.join(cache_dir, "coh_df"))
        pdif_df.to_csv(os.path.join(cache_dir, "pdif_df"))

        w = pweave.Pweb(template,
                        doctype="md2html",
                        output="./Reports/"+os.path.basename(f).split('.')[0]+".html") # TODO: output folder and path.join
        w.weave()
    
    if MULTIPLE:
        print(avg_psd)
        print(avg_psd.shape)
        # avg_psd.to_csv(os.path.join(cache_dir, "psd_df"))
        # avg_peaks.to_csv(os.path.join(cache_dir, "peaks_df"))
        # avg_abs.to_csv(os.path.join(cache_dir, "abs_df"))
        # avg_rel.to_csv(os.path.join(cache_dir, "rel_df"))
        # avg_cor.to_csv(os.path.join(cache_dir, "cor_df"))
        # avg_coh.to_csv(os.path.join(cache_dir, "coh_df"))
        # avg_pdif.to_csv(os.path.join(cache_dir, "pdif_df"))
        
        w = pweave.Pweb(template,
                        doctype="md2html",
                        output="./Reports/"+os.path.basename(f).split('.')[0]+".html") # TODO: output folder and path.join
        # w.weave()
    # shutil.rmtree(cache_dir)


if __name__ == "__main__":
    # execute only if run as a script
    main()

