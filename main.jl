module Reporte
export read_sig, pot_abs, pot_rel, coh
include("files.jl")
include("pot.jl")
include("coh.jl")
end

using Reporte

Sample_Frequency = 500
bands = ["delta","theta","alpha1","alpha2","beta1","beta2","gamma"]
n_channels = 19


# sig, channels = read_sig(joinpath(pwd(),"example/eeg.txt"), n_channels)
# absl = pot_abs(sig, Sample_Frequency)
# rel = pot_rel(absl)
# println(sum(absl,2))
# println(sum(rel,2))
# cor_mat  = cor(sig)
# coh_mats = coh(sig,n_channels)


