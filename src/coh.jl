using PyCall
@pyimport scipy.signal as pysig


"""
"""
function coh(sig, n_channels, fs::Int=500)
    n_bands = 7
    coh = repmat([0],1,n_bands) # number of bands
    for i in 1:n_channels, j in 1:n_channels
        freq,coher = pysig.coherence(sig[:,i],sig[:,j],fs=fs)
        # TODO: mean or sum?
        coh_delta  =  mean(coher[1 .<= freq .< 4])
        coh_theta  =  mean(coher[4 .<= freq .< 8])
        coh_alpha1 =  mean(coher[8 .<= freq .< 11])
        coh_alpha2 =  mean(coher[11 .<= freq .< 14])
        coh_beta1  =  mean(coher[14 .<= freq .< 20])
        coh_beta2  =  mean(coher[20 .<= freq .< 31])
        coh_gamma  =  mean(coher[31 .<= freq .< 50])
        coh = vcat(coh,[coh_delta coh_theta coh_alpha1 coh_alpha2 coh_beta1 coh_beta2 coh_gamma])
    end
    coh_bands = coh[2:end,:]

    delta  = reshape(coh_bands[:,1],n_channels,n_channels) 
    theta  = reshape(coh_bands[:,2],n_channels,n_channels) 
    alpha1 = reshape(coh_bands[:,3],n_channels,n_channels) 
    alpha2 = reshape(coh_bands[:,4],n_channels,n_channels) 
    beta1  = reshape(coh_bands[:,5],n_channels,n_channels) 
    beta2  = reshape(coh_bands[:,6],n_channels,n_channels) 
    gamma  = reshape(coh_bands[:,7],n_channels,n_channels)
    return [[delta] [theta] [alpha1] [alpha2] [beta1] [beta2] [gamma]]
end

