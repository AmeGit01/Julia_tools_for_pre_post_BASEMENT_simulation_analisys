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

# Interactive plot of the CSV files of a given quantity ("discharge" or "wse")
function plot_quantity_custom(quantity)
    q = QUANTITIES[quantity]

    # Files are searched only now, after the user's choice
    InputFiles = find_input_files(quantity)
    isempty(InputFiles) && return nothing

	for File ∈ InputFiles
		# Read data
	    println("\n[$(q.name)] Reading ", File, "...")
	    df = CSV.read(File, DataFrame)

		# Print columns
		println("Columns: ")
		Cols = names(df)
		foreach(println, enumerate(Cols))

		# Select columns
		println("Select columns to be plotted (ex. 2 5 6):")
		input = readline()

		if isempty(input) 
			println("No column selected, all columns will be plotted!!")
			Nall = length(Cols)
			DatasetsToPlot = collect(2:1:Nall)
			@infiltrate false
		else
			DatasetsToPlot = parse.(Int64, split(input)) # [8, 9]
		end

		# transform seconds to hours
		xh = df[:, 1] ./ 3600

		# Reverse eventual wrong directioned nodestring (discharge only:
		# the sign of the water surface elevation must not be changed)
		reverse_list = [] # [23, 24]
		if quantity == "discharge"
			for n ∈ reverse_list
				df[:, n] .= -df[:, n]
			end
		end

		# Plot the data
		FirstPlot = true
		plt = plot()
		for n ∈ DatasetsToPlot
			if FirstPlot			
				println("Choose the plot title: ")
				title = readline()
				plot_df!(plt, xh, df[:, n], strip_unit(Cols[n]), title; ylabel=q.ylabel)
				FirstPlot = false
			else
				plot_df!(plt, xh, df[:, n], strip_unit(Cols[n]))
			end
		end
		plot!(plt, size=(800, 600), left_margin=3mm)
		display(plt)

		println("Do you want to save the plot? (y/n)")
		input = readline()

		if input == "y" || input == "Y"
			println("Digit the file name: ")
			input = readline()

			OutputPath = joinpath(OutputFolder, input)
			savefig(plt, OutputPath)
			isfile(OutputPath) && println("Plot saved: ", OutputPath)
		end

		@infiltrate false
	end

    return nothing
end

function main_custom()
    # Choose what to plot: 1) discharge, 2) WSE, 3) both
    for quantity ∈ choose_quantities()
        plot_quantity_custom(quantity)
    end

    return nothing
end

main_custom()

# Tutte (escluse BC monte)
# 13 14 15 16 17 18 20 21 22 23 24 7

# Divergenza
# 14 15 16 

# Andamento portata
# 13 21 22 14 18 7
