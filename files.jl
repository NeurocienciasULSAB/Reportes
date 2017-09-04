"""
`read_sig(path::String, n_channels::Int, [header::Array{String})], sep::Char='\t', rem_len::Int=5)`
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

"""
`read_setup([path::String, sep::Char='\t'])`
Reads a channel setup from a tsv file. Columns are x-position, y-position, and channel name. Defaults to nicolette 19 channel 10-20 setup
"""
function read_chsetup()
    setup = [0.3   1.0    "FP1";
             0.7   1.0    "FP2";
             0.25  0.775  "F3" ;
             0.75  0.775  "F4" ;
             0.5   0.725  "FZ" ;
             0.25  0.5    "C3" ;
             0.75  0.5    "C4" ;
             0.5   0.5    "CZ" ;
             0.25  0.225  "P3" ;
             0.75  0.225  "P4" ;
             0.5   0.275  "PZ" ;
             0.3   0.0    "O1" ;
             0.7   0.0    "O2" ;
             0.0   0.85   "F7" ;
             1.0   0.85   "F8" ;
             0.0   0.5    "T3" ;
             1.0   0.5    "T4" ;
             0.0   0.15   "T5" ;
             1.0   0.15   "T6" ]
end

function read_chsetup(path::String, sep::Char='\t')
    setup = []
    try
        setup = readdlm(path,sep,header=false)
    catch err
        error("Couldn't find setup, using fallback 19ch.")
        return read_chsetup()
    end
    return setup
end
