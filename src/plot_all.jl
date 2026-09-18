#!/usr/bin/env julia

using Plots, Plots.Measures, CSV, DataFrames, Infiltrator, Glob

function plot_df!(plt, x, y, label::AbstractString, title::AbstractString)
	# xh = x ./ 3600

    plt = plot!(x, y;
        # legend=false, 
        xlabel="Time [s]", 
        # xticks=(ticks, ticklabels),
        # xrotation=30,
        ylabel="Discharge [m³/s]", 
        title=title,
		label=label,
    )
    # display(plt)
    return
end

function plot_df!(plt, x, y, label::AbstractString)
    plt = plot!(x, y;
        # legend=false, 
        # xlabel="Time [s]", 
        # xticks=(ticks, ticklabels),
        # xrotation=30,
        # ylabel="Discharge [m³/s]", 
        # title=title,
		label=label,
    )
    # display(plt)
    return
end

function plot_df(x, y, title::AbstractString)
    plt = plot(x, y;
        # legend=false, 
        xlabel="Time [s]", 
        # xticks=(ticks, ticklabels),
        # xrotation=30,
        ylabel="Discharge [m³/s]", 
        title=title,
		# label=label,
        size=(800, 600), 
        left_margin=3mm
    )

    display(plt)
    return plt
end

const InputFolder = "outputs"
const OutputFolder = joinpath("outputs", "figures")

function main()
    InputPath = joinpath(InputFolder, "*discharge.csv")
    InputFiles = glob(InputPath)
    println("Found $(length(InputFiles)) CSV files:", InputFiles)

    for file ∈ InputFiles
		# Read the file
		df = CSV.read(file, DataFrame)

		# Find its columns
		Cols = names(df)
		
		# transform seconds to hours
		xh = df[:, 1] ./ 3600

		# extract the mane of the file
		index = collect(findlast("/", file))
		FileName = file[index[end]+1:end-4]

        println("Do you want to save a single file? [y/n]")
        input = readline()

        if input == "y" || input == "Y"
		    # Plot the data single file
		    FirstPlot = true
		    plt = plot()
		    @infiltrate false
		    for n ∈ eachindex(Cols[2:end])
		    	if FirstPlot		
		    		plot_df!(plt, xh, df[:, n+1], Cols[n+1][begin:end-7], FileName)
		    		FirstPlot = false
		    	else
		    		plot_df!(plt, xh, df[:, n+1], Cols[n+1][begin:end-7])
		    	end
		    end
		    plot!(plt, size=(800, 600), left_margin=3mm); # display(plt)

            OutputPath = joinpath(OutputFolder, "$(FileName).pdf")
		    savefig(plt, OutputPath) 
            isfile(OutputPath) && println("Saved $(OutputPath)")
        else
            # plot data multiple files
            # plt = plot()
		    for n ∈ eachindex(Cols[2:end])
	    		plt = plot_df(xh, df[:, n+1], Cols[n+1][begin:end-7])
    		    OutputPath = joinpath(OutputFolder, "$(Cols[n+1][begin:end-7]).pdf")
    		    savefig(plt, OutputPath)
                isfile(OutputPath) && println("Saved $(OutputPath)")
            end

        end
    end

    return nothing
end

main()