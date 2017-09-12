import GR.gridit
function headplot(vec::Array{Float64};
                  colorbar_title="",
                  title="",
                  aspect_ratio=1,
                  ticks=nothing,
                  grid=nothing,
                  seriescolor=:viridis,
                  border=false
                  )
    setup =[0.3   1.0    "Fp1";
            0.7   1.0    "Fp2";
            0.5   0.725  "Fz" ;
            0.25  0.775  "F3" ;
            0.75  0.775  "F4" ;
            0.0   0.85   "F7" ;
            1.0   0.85   "F8" ;
            0.5   0.5    "Cz" ;
            0.25  0.5    "C3" ;
            0.75  0.5    "C4" ;
            0.0   0.5    "T3" ;
            1.0   0.5    "T4" ;
            0.5   0.275  "Pz" ;
            0.25  0.225  "P3" ;
            0.75  0.225  "P4" ;
            0.0   0.15   "T5" ;
            1.0   0.15   "T6" ;
            0.3   0.0    "O1" ;
            0.7   0.0    "O2" ]

    headplot(vec,setup,
             aspect_ratio=aspect_ratio,
             title=title,
             colorbar_title=colorbar_title,
             ticks=ticks,
             grid=grid,
             seriescolor=seriescolor,
             border=border
             )
end
function headplot(vec::Array{Float64},ch_setup::Array;
                  title="",
                  colorbar_title="",
                  aspect_ratio=1,
                  ticks=nothing,
                  grid=nothing,
                  seriescolor=:viridis,
                  border=false
                  )
    info(size(ch_setup))
    info(size(vec))
    info(size(ch_setup,1),size(vec,1))
    assert(size(ch_setup,1)==size(vec,1))
    x = ch_setup[:,1]
    y = ch_setup[:,2]
    z = vec

    ncols = 50 # number of columns to interpolate
    nrows = 50 # number of rows to interpolate

    frame = .1 # 10% frame
    xlims = (minimum(x)-frame,
        maximum(x)+frame)
    ylims = (minimum(y)-frame,
        maximum(y)+frame)

    xi, yi, zi = gridit(x, y, z, ncols, nrows) # interpolate values
    Z = reshape(zi,nrows,ncols)
    p1 = contour(xi,yi,Z,fill=true,
                 aspect_ratio=aspect_ratio,
                 title=title,
                 colorbar_title=colorbar_title,
                 ticks=ticks,
                 grid=grid,
                 seriescolor=seriescolor,
                 border=border,
                 xlims=xlims,
                 ylims=ylims
                 )
end
