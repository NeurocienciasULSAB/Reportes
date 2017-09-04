"""
`cut_frequencies(spectrum::Array{Float64}, freqs::StepRangeLen, lowFreq::Int, highFreq::Int)`
Selects a section of a power spectrum array from the lower frequency (`lowFreq`) up to but without including the higher frequency (`highFreq`) according to the frequency range `freqs`.

Arguments:
- `spectrum`: signal or array of `Float64` signals.
- `freqs`: step range representing the frequencies to be handled.
- `lowFreq`: Int with a low-cut frequency.
- `highFreq`: Int with a high-cut frequency.

Output:
- `res`: matrix with cut powerspectrum.
"""
function cut_frequencies(ps::Array{Float64}, freqs::StepRangeLen, lowFreq::Int, highFreq::Int)
    assert(lowFreq < highFreq)
    m = sum(lowFreq .<= freqs .< highFreq)
    filter_freq = repmat(freqs,1,size(ps,2))
    res = ps[lowFreq .<= filter_freq .< highFreq]
    res = reshape(res,m,size(ps,2))
end

"""
"""
function power_spectrum(sig::Array{Float64}, sampFreq::Int=500)
    n = size(sig)[1]
    p = fft(sig,1)
    n_unique = ceil(Int, (n+1)/2)
    p = p[1:n_unique,:]
    p = abs.(p)
    p = p ./ n #scale
    p = p.^2  # square it
    # odd nfft excludes Nyquist point
    if n % 2 > 0
        p[2:length(p)] = p[2:length(p)]*2 # we've got odd number of   points fft
    else 
        p[2:(length(p)-1)] = p[2: (length(p) -1)]*2 # we've got even number of points fft
    end
    freqArray = (0:(n_unique-1)) * (sampFreq / n)
    return p, freqArray
end

"""
`pot_abs(sig::Array{Float64,2}, sampFreq::Int=500)::Array{Float64}`
Return the absolute spectral potence of 7 different frequency bands:
delta  = [1,4)
theta  = [4,8)
alpha1 = [8,11)
alpha2 = [11,14)
beta1  = [14,20)
beta2  = [20,31)
gamma  = [31,50)

Arguments:
- `sig`: array with a signal or signals to be analyzed.
- `sampFreq`: Sampling frequency in herz, defaults to Nicolet's 500 hz.

Output:
    Array of 7 rows and the same number of columns as the number of channels with the summed power of every band, for every channel
"""
function pot_abs(sig::Array{Float64}, sampFreq::Int=500)::Array{Float64}

    p, freqArray = power_spectrum(sig, sampFreq)

    delta  = sum(cut_frequencies(p,freqArray,1,4),1)
    theta  = sum(cut_frequencies(p,freqArray,4,8),1)
    alpha1 = sum(cut_frequencies(p,freqArray,8,11),1)
    alpha2 = sum(cut_frequencies(p,freqArray,11,14),1)
    beta1  = sum(cut_frequencies(p,freqArray,14,20),1)
    beta2  = sum(cut_frequencies(p,freqArray,20,31),1)
    gamma  = sum(cut_frequencies(p,freqArray,31,50),1)
    return [delta; theta; alpha1; alpha2; beta1; beta2; gamma]
end

"""
`pot_rel(abs::Array{Float64})::Array{Float64}`
Return the absolute spectral potence of 7 different frequency bands:
delta  = [1,4)
theta  = [4,8)
alpha1 = [8,11)
alpha2 = [11,14)
beta1  = [14,20)
beta2  = [20,31)
gamma  = [31,50)

Arguments:
- `absl`: array with the absolute powers of every band

Output:
    Array of 7 rows and the same number of columns as the number of channels with the summed power of every band, for every channel
"""
function pot_rel(absl::Array{Float64})::Array{Float64}
    total = sum(absl,1)

    delta  = (absl[1,:]' ./total)
    theta  = (absl[2,:]' ./total)
    alpha1 = (absl[3,:]' ./total)
    alpha2 = (absl[4,:]' ./total)
    beta1  = (absl[5,:]' ./total)
    beta2  = (absl[6,:]' ./total)
    gamma  = (absl[7,:]' ./total)
    return [delta; theta; alpha1; alpha2; beta1; beta2; gamma]
end

"""

"""
function plot_pot(ps::Array{Float64},freqs::StepRangeLen,n_channels::Int,low::Int=0,high::Int=30,args...)
    freqz = repmat(freqs,1,size(ps,2))
    plot(freqz,ps,
    layout=(n_channels,1),
    label=header,
    xlims=(low,high),
    args...)
end
