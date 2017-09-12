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
using Weave

function parse_commandline()
    s = ArgParseSettings(prog = "Reportes",
                         description = "Report creation utility for EEG signals.",
                         add_help = true,
                         commands_are_required = false)

    @add_arg_table s begin
        "--setup", "-s"
            help = "Indicate file with channel setup"
            arg_type = String
        "--bands", "-b"
            help = "Indicate file with band setup"
            arg_type = String
        "--template", "-t"
            help = "Indicate template to use"
            arg_type = String
            default = joinpath(pwd(),"templates/main.jmd")
        "--html"
            help = "Indicate a html template to use"
            arg_type = String
            default = joinpath(pwd(),"templates/main_html.tpl")
        "--css"
            help = "Indicate a css template to use"
            arg_type = String
            default = joinpath(pwd(),"css/style.css")
        "--gui", "-g"
            help = "Start gtk window"
            action = :store_true
        "input"
            help = "Input file or folder to analyze"
            arg_type = String
            default = joinpath(pwd(),"example/eeg.txt")
        "--output", "-o"
            help = "Folder or file name to save the report"
            default = joinpath(pwd(),"Reports/last.html")
    end

    return parse_args(s)
end

function main()
    args = parse_commandline()

    if args["setup"] != nothing
        setup = read_chsetup(args["setup"])
    else
        setup = read_chsetup()
    end

    if args["bands"] != nothing
        # TODO: Implement reading bands
        error("Not yet implemented: band setup")
    else
        band_names = band_names = ["delta","theta","alpha1","alpha2","beta1","beta2","gamma"]
    end

    n_channels = size(setup,1)
    template = args["template"] # TODO: verify template
    files = []

    if isdir(args["input"])
        files = readdir(args["input"])
        MULTIPLE = true
    elseif isfile(args["input"])
        files = [args["input"]]
    else
        error("Input is neither a file nor a directory")
    end

    for file in files
        info("Processing ",file)
        sig, channels = read_sig(file, n_channels)
        absl = pot_abs(sig)
        rel  = pot_rel(absl)

        weave(template, 
        out_path = args["output"], # TODO: saving name should change to avoid override Date(now())
        template = args["html"],
              args = Dict( "date" => Dates.format(now(), "dd/mm/yyyy HH:MM"),
                           "subject" => basename(file), 
                           "chls" => channels,
                           "bnds" => band_names,
                           "abs"  => absl,
                           "rel"  => rel,
                           "cor"  => cor(sig),
                           "coh"  => coh(sig,n_channels)
                           ),
        doctype = "md2html")

        # sig, channels = read_sig(joinpath(pwd(),"example/eeg.txt"), n_channels)
        # absl = pot_abs(sig)
        # info(typeof(absl))
        # rel = pot_rel(absl)
        # println(sum(absl,2))
        # println(sum(rel,2))
        # cor_mat  = cor(sig)
        # coh_mats = coh(sig,n_channels)
    end


end

main()
