"""
`read_sig(path::String, n_channels::Int, [header::Array{String})], sep::Char='\t', rem_len::Int=5`
Reads numeric signals from a text file and returns them and their header.
"""
function read_sig(path::String, n_channels::Int, sep::Char='\t', rem_len::Int=5)
    signals = sig = []
    try
        signals = readdlm(path,sep,header=true);
        sig = convert.(Float64,signals[1][:,1:n_channels]);
    catch err
        throw(err)
    end
    header = signals[2][:,1:n_channels]
    header = Array{String}([i[1:end-(rem_len)] for i in header]) # Remove reference name ex 'A1A2'
    header = header[1,:]
    return sig, header
end

function read_sig(path::String, n_channels::Int, header::Array{String}, sep::Char='\t', rem_len::Int=0)
    signals = sig = []
    try
        signals = readdlm(path,sep,header=true)
        sig = convert.(Float64,signals[1][:,1:n_channels]);
    catch err
        error("Couldn't open file")
        throw(error(err))
        return(-1)
    end
    header = Array{String}([i[1:end-(rem_len)] for i in header]) # Remove reference name ex 'A1A2'
    header = header[1,:]
    return sig, header
end
