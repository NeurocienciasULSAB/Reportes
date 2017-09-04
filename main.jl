module Reporte
using Plots
export read_sig,
    read_chsetup,
    pot_abs,
    pot_rel,
    coh,
    headplot

include("src/files.jl")
include("src/pot.jl")
include("src/coh.jl")
end

using Reporte
using ArgParse

function parse_commandline()
    s = ArgParseSettings(prog = "Reportes",
                         description = "Report creation utility for EEG signals.",
                         add_help = true,
                         commands_are_required = false)

    @add_arg_table s begin
        "--channels", "-c"
            help = "Indicate file with channel setup"
        "--bands", "-b"
            help = "Indicate file with band setup"
        "--template", "-t"
            help = "Indicate template to use"
        "--gui", "-g"
            help = "Start gtk window"
            action = :store_true
        "input"
            help = "Input file or folder to analyze"
        "output"
            help = "Folder or file name to save the report"

        # "arg1"
        #     help = "a positional argument"
        #     required = true
        #     action = :store_true
        #     arg_type = Int
        #     default = 0
    end

    return parse_args(s)
end

function main()
    parsed_args = parse_commandline()
    println("Parsed args:")
    for (arg,val) in parsed_args
        println("  $arg  =>  $val")
    end

    # setup = read_chsetup()
    # band_names = ["delta","theta","alpha1","alpha2","beta1","beta2","gamma"]
    # n_channels = size(setup,1)

    # sig, channels = read_sig(joinpath(pwd(),"example/eeg.txt"), n_channels)
    # absl = pot_abs(sig)
    # info(typeof(absl))
    # rel = pot_rel(absl)
    # println(sum(absl,2))
    # println(sum(rel,2))
    # cor_mat  = cor(sig)
    # coh_mats = coh(sig,n_channels)
end

main()



