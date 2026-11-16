#!/usr/bin/env julia

using Plots, Plots.Measures, CSV, DataFrames, Infiltrator, Glob

function plot_df!(plt, x, y, label::AbstractString, title::AbstractString;
                  ylabel::AbstractString="Discharge [m³/s]")
	# xh = x ./ 3600

    plt = plot!(x, y;
        # legend=false, 
        xlabel="Time [h]", 
        # xticks=(ticks, ticklabels),
        # xrotation=30,
        ylabel=ylabel,
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

function plot_df(x, y, title::AbstractString; ylabel::AbstractString="Discharge [m³/s]")
    plt = plot(x, y;
        # legend=false, 
        xlabel="Time [h]", 
        # xticks=(ticks, ticklabels),
        # xrotation=30,
        ylabel=ylabel,
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

# ---------------------------------------------------------
# Quantities that can be plotted
#   pattern: files searched in InputFolder (only after the choice)
#   ylabel:  label of the vertical axis
# ---------------------------------------------------------
const QUANTITIES = Dict(
    "discharge" => (name="Discharge", pattern="*discharge.csv", ylabel="Discharge [m³/s]"),
    "wse"       => (name="Water surface elevation", pattern="*wse.csv", ylabel="WSE [m a.s.l.]"),
)

# Ask the user which quantity to plot and return the list of keys of QUANTITIES
function choose_quantities()
    while true
        println("What do you want to plot?")
        println("  1) Discharge")
        println("  2) Water surface elevation (WSE)")
        println("  3) Both discharge and WSE (consecutively)")
        print("Type 1, 2 or 3 and press Enter: ")
        choice = strip(readline())
        choice == "1" && return ["discharge"]
        choice == "2" && return ["wse"]
        choice == "3" && return ["discharge", "wse"]
        println("Invalid choice '$(choice)', please type 1, 2 or 3.\n")
    end
end

# Find the CSV files of a given quantity (empty list if none is present)
function find_input_files(quantity)
    q = QUANTITIES[quantity]
    InputFiles = glob(q.pattern, InputFolder)
    if isempty(InputFiles)
        println("\nNo '$(q.pattern)' file found in '$(InputFolder)/': skipping $(q.name).")
    else
        println("\n$(q.name): found $(length(InputFiles)) CSV files: ", InputFiles)
    end
    return InputFiles
end

# Remove the unit from a column name, e.g. "Q_name [m3/s]" -> "Q_name"
strip_unit(col::AbstractString) = replace(col, r"\s*\[[^\]]*\]\s*$" => "")

# Plot all the CSV files of a given quantity ("discharge" or "wse")
function plot_quantity(quantity)
    q = QUANTITIES[quantity]

    # Files are searched only now, after the user's choice
    InputFiles = find_input_files(quantity)
    isempty(InputFiles) && return nothing

    for file ∈ InputFiles
		# Read the file
		df = CSV.read(file, DataFrame)

		# Find its columns
		Cols = names(df)
		
		# transform seconds to hours
		xh = df[:, 1] ./ 3600

		# extract the name of the file
		FileName = splitext(basename(file))[1]

        println("\n[$(q.name)] $(file)")
        println("Do you want to save a single file? [y/n]")
        input = readline()

        if input == "y" || input == "Y"
		    # Plot the data single file
		    FirstPlot = true
		    plt = plot()
		    @infiltrate false
		    for n ∈ eachindex(Cols[2:end])
		    	if FirstPlot		
		    		plot_df!(plt, xh, df[:, n+1], strip_unit(Cols[n+1]), FileName; ylabel=q.ylabel)
		    		FirstPlot = false
		    	else
		    		plot_df!(plt, xh, df[:, n+1], strip_unit(Cols[n+1]))
		    	end
		    end
		    plot!(plt, size=(800, 600), left_margin=3mm)
            display(plt)

            OutputPath = joinpath(OutputFolder, "$(FileName).pdf")
		    savefig(plt, OutputPath) 
            isfile(OutputPath) && println("Saved $(OutputPath)")
        else
            # plot data multiple files
		    for n ∈ eachindex(Cols[2:end])
	    		plt = plot_df(xh, df[:, n+1], strip_unit(Cols[n+1]); ylabel=q.ylabel)
    		    OutputPath = joinpath(OutputFolder, "$(strip_unit(Cols[n+1])).png")
    		    savefig(plt, OutputPath)
                isfile(OutputPath) && println("Saved $(OutputPath)")
            end

        end
    end

    return nothing
end

function main()
    # Choose what to plot: 1) discharge, 2) WSE, 3) both
    for quantity ∈ choose_quantities()
        plot_quantity(quantity)
    end

    return nothing
end

main()
