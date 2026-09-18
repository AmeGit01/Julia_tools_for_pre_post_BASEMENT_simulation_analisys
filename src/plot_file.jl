#!/usr/bin/env julia

using Plots, Plots.Measures, CSV, DataFrames, Infiltrator, Glob

function plot_df(df::DataFrame, filename::AbstractString)
    # Vaiaini = DateTime("2018-10-28 00:00:00", dateformat"yyyy-mm-dd HH:MM:SS")
    # Vaiaend = DateTime("2018-11-02 19:00:00", dateformat"yyyy-mm-dd HH:MM:SS")
    # ticks = collect(Vaiaini:Day(1):Vaiaend)
    # ticks = push!(ticks, Vaiaend)
    # ticklabels = Dates.format.(ticks, "dd-mm HH:MM")

    j = findlast(==('.'), filename)
    name = filename[1:j-1]

    # BMv41
    time = collect(0.0:1200.0:64800.0)
    plt = plot(time, df[!, "Discharge [m3/s]"];
        legend=false, 
        xlabel="Time [s]", 
        # xticks=(ticks, ticklabels),
        # xrotation=30,
        ylabel="Discharge [m³/s]", 
        title=name,
        # bottom_margin=5mm
    ) # =#


    #= MBv42
    plt = plot(df[!, "t [s]"], df[!, "Discharge [m3/s]"];
        legend=false, 
        xlabel="Time [s]", 
        # xticks=(ticks, ticklabels),
        # xrotation=30,
        ylabel="Discharge [m³/s]", 
        title=name,
        # bottom_margin=5mm
    ) # =#
    @infiltrate false
    display(plt)
    return plt, name
end

function main()
    files = glob("csv_files/*.csv")
    println("Found $(length(files)) CSV files:", files)

    for file ∈ files
        index = collect(findlast("/", file))
        filename = file[index[end]+1:end]
        df = CSV.read(file, DataFrame)
        plt, name = plot_df(df, filename)
        outpath = joinpath("images", "$(name).png")
        savefig(plt, outpath)
    end

    return nothing
end

main()