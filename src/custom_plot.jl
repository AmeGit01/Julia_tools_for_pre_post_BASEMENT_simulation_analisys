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

function main_custom()
    InputFile = "Discharge_IC_results.csv"
    InputPath = joinpath("csv_files", InputFile)

	# Read data
    println("Reading ", InputPath, "...")
    df = CSV.read(InputPath, DataFrame)

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

	# Reverce eventual wrong directioned nodestring
	reverse_list = [24, 25] # [23, 24]
	for n ∈ reverse_list
		df[:, n] .= -df[:, n]
	end

	# Plot the data
	FirstPlot = true
	plt = plot()
	for n ∈ DatasetsToPlot
		if FirstPlot			
			println("Choose the plot title: ")
			title = readline()
			plot_df!(plt, xh, df[:, n], Cols[n][begin:end-7], title)
			FirstPlot = false
		else
			plot_df!(plt, xh, df[:, n], Cols[n][begin:end-7])
		end
	end
	plot!(plt, size=(800, 600), left_margin=3mm)
	display(plt)

	println("Do you want to save the plot? (y/n)")
	input = readline()

	if input == "y" || input == "Y"
		println("Digit the file name: ")
		input = readline()

		OutputPath = joinpath("images", input)
		savefig(plt, OutputPath)

		println("Plot saved: ", OutputPath)
	end

	@infiltrate false

    return nothing
end

main_custom()

# Tutte (escluse BC monte)
# 13 14 15 16 17 18 20 21 22 23 24 7

# Divergenza
# 14 15 16 

# Andamento portata
# 20 21 13 17 7
