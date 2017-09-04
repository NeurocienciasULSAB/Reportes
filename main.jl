module Reporte
export read_sig,
    read_chsetup,
    pot_abs,
    pot_rel,
    coh,
    headplot

include("files.jl")
include("pot.jl")
include("coh.jl")
include("plots.jl")
end

using Reporte

setup = read_chsetup()
band_names = ["delta","theta","alpha1","alpha2","beta1","beta2","gamma"]

# Sample_Frequency = 500
# n_channels = 19


# sig, channels = read_sig(joinpath(pwd(),"example/eeg.txt"), n_channels)
# absl = pot_abs(sig, Sample_Frequency)
# rel = pot_rel(absl)
# println(sum(absl,2))
# println(sum(rel,2))
# cor_mat  = cor(sig)
# coh_mats = coh(sig,n_channels)

