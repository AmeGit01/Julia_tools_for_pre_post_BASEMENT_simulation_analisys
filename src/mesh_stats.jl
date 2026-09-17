#!/usr/bin/env julia

using Printf, Plots, Plots.Measures, DelimitedFiles
using StatsPlots, Statistics, StatsBase
using OrderedCollections, Colors, Dates
using Infiltrator, DaemonMode

function plot_histogram(data, materials, title, xlabel, quantile_intervals, i, matIDs, color, ylogScale, RegionNames; quantiles_flag = false)

	quantiles1 = 0
	qlabel1 = string(quantile_intervals[1]*100); qlabel1 = qlabel1 * "%"
	qlabel2 = string(quantile_intervals[2]*100); qlabel2 = qlabel2 * "%"
	# qlabel3 = string(quantile_intervals[3]*100); qlabel3 = qlabel3 * "%"
	# qlabel4 = string(quantile_intervals[4]*100); qlabel4 = qlabel4 * "%"

	# 1
	xmin = minimum(data[materials[matIDs[i]]])
	xmax = maximum(data[materials[matIDs[i]]])
	xticks = round.(collect(range(xmin, xmax, length=10)), digits=4)
	splt11 = histogram(
	    data[materials[matIDs[i]]],
	    bins=50,
	    xlabel=xlabel,
	    ylabel="Numero di celle",
	    # title=title,
		color=color,
		# label="matID $(matIDs[i])",
		label="$(RegionNames[i])",		
		xticks=xticks,
		yscale = ylogScale[i] ? :log10 : :identity
	)
	@printf("    minimum data at matID %d (%s) is %.4f \n", matIDs[i], RegionNames[i], minimum(data[materials[matIDs[i]]]))
	if i == 1
		splt11 = plot!(splt11; title=title)
	end

	if quantiles_flag
		quantiles1 = quantile(data[materials[matIDs[i]]], quantile_intervals)
		splt11 = vline!([quantiles1[1], quantiles1[1]], label=qlabel1)
		splt11 = vline!([quantiles1[2], quantiles1[2]], label=qlabel2)
		# splt11 = vline!([quantiles1[3], quantiles1[2]], label=qlabel3)
		# splt11 = vline!([quantiles1[4], quantiles1[4]], label=qlabel4)
	end

	return splt11, quantiles1
end

function write_report(ReportFileName, FileName, BASEflow, quantiles, quantiles_intervals, materials, matIDs, area, chrsize, RegionNames)
	@infiltrate false
	open(ReportFileName, "w") do io
		println(io, "QUANTILE REPORT for $(FileName)")
	    timestamp = Dates.format(now(), "yyyy-mm-dd HH:MM:SS")
		println(io, "Producion date: ", timestamp)
		println(io, "BASEMENT type: $(BASEflow) \n")
		println(io, "="^40)
		# in this case quantiles contains all the quantiles for all the data, 
		# its length is not known a priori, so I need to ckeck it first 
		# quantiles = Array[4, nID, 2] (Array[nquantiles, nregions, ndata])

		nID = length(matIDs)
		nq = length(quantiles_intervals[:, 1])
		Names = BASEflow == "BASEMD" ? ["Area", "Minimum length"] : ["Area", "Inscribed circle's radius"]
		variables = Array{Float64}(undef, length(area), 2)
		variables[:, 1] = area
		variables[:, 2] = chrsize
		

		for j ∈ 1:2		# loop over the variables' name
			for n ∈ 1:nID		# loop over the matIDs

				println(io, "\n$(Names[j]), matID $(matIDs[n]) ($(RegionNames[n]))")
				
				# quantiles[:, n, j]:  quantiles_intervals[:, j], matIDs[n], Names[j]
				# q_percentage = quantiles_intervals[:, j] * 100		# ex. [0.1, 1.0, 5.0, 10.0]
				
				for i ∈ 1:nq		# loop over the quantiles
					q_percentage = quantiles_intervals[i, j] * 100

					# quantiles[i, n, j]:  quantiles_intervals[i, j], matIDs[n], Names[j]
					q = quantiles[i, n, j]

					println(io, "	\nQuantile: $(q_percentage) % ($(round(q, digits=4)) m^2)")
					local_idx = findall( variables[materials[matIDs[n]], j] .< q ) # area[materials[idmat]]
					idx = materials[matIDs[n]][local_idx]
					println(io, "	Cells below quantile: $(length(idx))")
					println(io, "	Indices: $(idx)")
				end		# loop over the quantiles
			end		# loop over the matIDs
		end		# loop over the variables' name
	end # closing file

	@printf("\nReport printed to file %s\n", ReportFileName)

	return nothing
end

const InputFolder = "inputs"
const OutputFolder = "outputs"

function plot_stats(args)

	# Read inputs
	InputFileName = args[1] 
	RegionsFile = args[2]
	BASEflow = args[3]
	OutputFormat = args[4]	
	dosave = true
	dodisplay = false
	# =#

	#= testing
	InputFile = "inputs/test_mesh.csv"
	RegionsFile = "inputs/test_regions.txt"
	BASEflow = "BASEHPC"
	OutputFormat = "pdf"
	dosave = false
	dodisplay = true
	# =#

	# read files and set-up outputs names
	InputPath = joinpath(InputFolder, InputFileName)
	@printf("Reading input file: %s \n", InputPath)
	data, fields = readdlm(InputPath, ',', header=true) # '\t'

	last = collect(findlast(".", InputFileName))
	FileNameNoFormat = InputFileName[begin:last[begin]-1]	

	RegionsPath = joinpath("inputs", RegionsFile)
	UseRegionsFile, fields_RegionsFile = readdlm(RegionsPath, ',', header=true)
	UseRegions = Int64.(UseRegionsFile[:, 1])
	ylogScale = Bool.(UseRegionsFile[:, 2])
	RegionNames = String.(UseRegionsFile[:, 3])
	RegionNames = chop.(RegionNames, head=1, tail=0)

	ReportFilePath = joinpath(OutputFolder, "reports", "Report_$(FileNameNoFormat).txt")
	# ReportFilePath = "reports/Report_$(FileNameNoFormat).txt"
	
	# Find all the position of the colums to be used
	positions = zeros(Int64, 5)
	idx = findfirst(==( "fid" ), fields)
	!isnothing(idx) && (positions[1] = idx[2])
	idx = findfirst(==( "matid" ), fields)
	!isnothing(idx) && (positions[2] = idx[2])
	idx = findfirst(==( "area" ), fields)
	!isnothing(idx) && (positions[3] = idx[2])
	idx = findfirst(==( "min_len" ), fields)
	!isnothing(idx) && (positions[4] = idx[2])
	idx = findfirst(==( "ins_rad" ), fields)
	!isnothing(idx) && (positions[5] = idx[2])

	if any(iszero, positions) 
		@printf("\nSome of the required fields are missing in the input file %s. Please check the column names. \n", InputFile)
		@printf("The correct names that are required are: fid, matid, area, min_len, ins_rad \nAny additional (support) column can be present without any issue. \n")
		return
	end
	@infiltrate false

	# create filters by region type
	ndata = length(data[:,positions[1]])
	material_id = Array{Int64}(undef, ndata)
	material_id .= data[:,positions[2]]

	materials_all = Dict( i => findall(==(i), material_id) for i ∈ unique(material_id) )

	# Check the selected regions are actually stored in the csv file
	flag = false
	MissingRegions = Int64[]
	for i ∈ UseRegions
		if !haskey(materials_all, i)
			@printf("matid %d is selected but not found in the input file.\n", i)
			flag = true
			push!(MissingRegions, i)
		end
	end
	if flag
		# @printf("The regions with matid %s are missing in the input file.\nThe only available matids are: %s\n", join(MissingRegions, ", "), join(unique(material_id), ", "))
		@printf("The only available matids are: %s\n", join(sort(unique(material_id)), ", "))
		return
	end

	# Select the desired regions
	materials = OrderedDict(i => materials_all[i] for i in UseRegions)


	# Preallocate vectors
	nID = length(UseRegions)
	plts = Array{Plots.Plot}(undef, nID, 2)

	nquantiles = 2 															# USER DEFINED
	quantiles = Array{Float64}(undef, nquantiles, nID, 2)
	quantiles_intervals = Array{Float64}(undef, nquantiles, 2)
	
	# Define plot colors
	colors = [RGB(
		0.5 + 0.5*sin(2π*i/nID),
    	0.5 + 0.5*sin(2π*(i/nID + 1/3)),
    	0.5 + 0.5*sin(2π*(i/nID + 2/3))
	) for i ∈ 1:nID]

	## Plot area distributions
	@printf("\nBuilding area distribution plots... \n")
	area = data[:,positions[3]]
	title = "Distribuzione Aree - $(InputFileName)"
	xlabel = "Area cella [m^2]"
	OutputName = joinpath("outputs", "figures", "Area_$(FileNameNoFormat).$(OutputFormat)")
	# OutputName = "figures/Area_$(FileNameNoFormat).$(OutputFormat)"

	quantiles_intervals[:, 1] .= [0.001, 0.01]								# USED DEFINED, ACCORDIG TO nquantiles

	for i ∈ 1:nID
		plt_tmp, q1 = plot_histogram(area, materials, title, xlabel, quantiles_intervals[:, 1], i, UseRegions, colors[i], ylogScale, RegionNames; quantiles_flag = true)
		plts[i, 1] = plt_tmp
		quantiles[:, i, 1] = q1
	end

	ydimension = Int64(300*nID+100)
	plt1 = plot(plts[:, 1]..., layout=(nID, 1), 
		left_margin=5mm, bottom_margin=5mm,
		size=(1000, ydimension)
	)
	dodisplay && display(plt1)

	dosave && savefig(plt1, OutputName)
	dosave && @printf("Area plot saved to file %s\n", OutputName)

	# "figures/prova.png"

	# Plot controlling dimension 
	@printf("\nBuilding characteristic length distribution plots... \n")
	if BASEflow == "BASEMD"
		chrsize = data[:,positions[4]]
		title = "Minimum cell size - $(InputFileName)"
		xlabel = "edge length [m]"
	elseif BASEflow == "BASEHPC"
		chrsize = data[:, positions[5]]
		title = "Inscribed circle's radius - $(InputFileName)"
		xlabel = "radius [m]"
	else
		error("BASEflow not defined, select BASEMD or BASEHPC")
	end
	OutputName = joinpath("outputs", "figures", "Char_length_$(FileNameNoFormat).$(OutputFormat)")
	# OutputName = "figures/Char_length_$(FileNameNoFormat).$(OutputFormat)"

	quantiles_intervals[:, 2] = [0.001, 0.01]								# USED DEFINED, ACCORDIG TO nquantiles	

	for i ∈ 1:nID
		plt_tmp, q2 = plot_histogram(chrsize, materials, title, xlabel, quantiles_intervals[:, 2], i, UseRegions, colors[i], ylogScale, RegionNames; quantiles_flag = true)
		plts[i, 2] = plt_tmp
		quantiles[:, i, 2] = q2
		# @show q1
	end
	ydimension = Int64(300*nID+100)
	plt2 = plot(plts[:, 2]..., layout=(nID, 1), 
		left_margin=5mm, bottom_margin=5mm,
		size=(1000, ydimension)
	)
	dodisplay && display(plt2)

	dosave && savefig(plt2, OutputName) # =#
	dosave && @printf("Characteristic length plot saved to file %s\n", OutputName)

	# build the report
	dosave && write_report(ReportFilePath, InputFileName, BASEflow, quantiles, quantiles_intervals, materials, UseRegions, area, chrsize, RegionNames)

	return nothing
end

function compute_stats(args)
	ElementFile = args[1]
	NodeFile = args[2]
	BASEflow = args[3] 
	Outputformat = ".csv"
	dosave = true
	dodisplay = false

	# read files and set-up outputs names
	@printf("Reading element file: %s \n", ElementFile)
	ele, fields = readdlm(ElementFile, header=true) # , '\t')
	# elememnts contains: fid, node1, node2, node3, matid
	eleID = ele[:, 1]
	Nele = length(eleID)-1


	# Extract FileName
	last = collect(findlast("/", ElementFile))
	FileName = ElementFile[last[begin]+1:end]
	last = collect(findlast(".", FileName))
	FileNameNoFormat = FileName[begin:last[begin]-1]	

	@printf("Reading element file: %s \n", NodeFile)
	nod, fields = readdlm(NodeFile, header=true) # , '\t')
	nodID = nod[:, 1]
	Nnod = length(nodID)-1

	open("inputs/ID.sol", "w") do io

		write(io, "DATASET\n")
        write(io, "OBJTYPE \"mesh2d\"\n")
		write(io, "RT_JU8LIAN 2433282.500000\n")
		write(io, "BEGSCL\n")
        write(io, "ND $Nnod\n")
        write(io, "NC $Nele\n")
        write(io, "NAME \"ID\"\n")
		write(io, "TIMEUNITS seconds\n")
        write(io, "TS 0 0.0\n")
        # write(io, "CC\n") # Dati legati alle facce

		for n ∈ 1:Nele
			write(io, Float64(eleID[n]))
		end
	end

	return 
end

# use:
# empty!(Base.ARGS); push!(Base.ARGS, "test_mesh.csv", "test_regions.txt", "BASEHPC", "png")
if length(Base.ARGS) < 4
	error("Select an input file typing: julia src/mesh_stats.jl InputFile.csv RegionsFile.txt BASEMD/BASEHPC FigureFormat \n")
end # =#

#= use:
# push!(ARGS, "inputs/test_mesh.csv", "inputs/test_regions.txt", "BASEHPC", "png")
if length(Base.ARGS) < 2
	error("Missing argumens \n")
end # =#


# compute_stats(Base.ARGS)

plot_stats(Base.ARGS)