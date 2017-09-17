
import argparse
import report as rp
import pweave
import os
from time import gmtime, strftime

def create_parser(dir_path=os.path.dirname(os.path.realpath(__file__))):
    parser = argparse.ArgumentParser(prog="Reportes",
                                     description="Report creation utility for EEG signals.",
                                     add_help=True)
    parser.add_argument("--setup", "-s",
                        help="File with the channel setup")
    parser.add_argument("--bands", "-b",
                        help="File with the band setup")
    parser.add_argument("--template", "-t",
                        help="Markdown template to use",
                        default=os.path.join(dir_path, "templates", "main.pmd"))
    parser.add_argument("--html",
                        help="HTML template to use",
                        default=os.path.join(dir_path,
                                             "templates",
                                             "main_html.html"))
    parser.add_argument("--css",
                        help="CSS style file to use",
                        default=os.path.join(dir_path,
                                             "css",
                                             "style.css"))
    parser.add_argument("--gui", "-g",
                        help="Start with gui.",
                        action="store_true",
                        default=False)
    parser.add_argument("--input",
                        help="Input file or folder to analyze",
                        default=os.path.join(dir_path,
                                             "example",
                                             "eeg.txt"))
    parser.add_argument("--output", "-o",
                        help="Folder or file name to save the report",
                        default=os.path.join(dir_path, "Reports", "last.html"))
    return parser


def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    parser   = create_parser(dir_path)
    args     = parser.parse_args()

    fs = 500  # TODO: input frequency

    if args.setup:
        setup = rp.read_chsetup(args.setup)
    else:
        setup = rp.read_chsetup()

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
        bands = rp.create_bands(band_names, band_lows, band_highs)

    n_channels = setup.shape[0]
    template = args.template
    files = []
    if os.path.isdir(args.input):
        raise NotImplementedError
        files = readdir(args.input)  # TODO: readdir
        MULTIPLE = True
    elif os.path.isfile(args.input):
        files = [args.input]
    else:
        raise IOError("ERROR: file or folder not found")

    for f in files:
        print("INFO: Processing file ", f)
        # sig    = rp.read_sig(f, n_channels)
        # psd_df, phase_df = rp.sig_to_frequency(sig, fs=fs)
        # abs_df = rp.pot_abs(psd_df, bands)
        # rel_df = rp.pot_rel(abs_df)
        # cor_df = sig.corr()
        # coh_df = rp.coh(sig, bands, fs=fs)
        # pdif_df = rp.phase_dif(phase_df, bands)


        # Pweb.globals = { "foo" : "bar" } # This creates a global var `foo` with value 'bar'
        # w = Pweb("inputfile.tex")        # Generate a Pweb class. We can't just call `pweave()`
        # w.weave()                        # Equivalent of `pweave()`
        pweave.Pweb.globals = {"date":strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                               "author":"Alberto Barradas"
                               }
        In = [0,0]
        w = pweave.Pweb(template,
                        doctype="md2html",
                        output=args.output
                        )
        w.weave() 


if __name__ == "__main__":
    # execute only if run as a script
    main()
