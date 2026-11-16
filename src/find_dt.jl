#!/usr/bin/env julia

using Plots, Plots.Measures, CSV, DataFrames, Infiltrator, Glob

const InputFolder = joinpath("inputs")
const OutputFolder = joinpath("outputs", "reports")

function main()
	println("Input the .csv mesh file name without file format: ")
    InputName = readline() # "mesh_results_tend"
	InputFormat = ".csv"
	InputFile = InputName * InputFormat
    InputPath = joinpath(InputFolder, InputFile)
    data = CSV.read(InputPath, DataFrame)

	# safety check: unphysical negative water depths (checked cell by cell,
	# before the square root, which would fail on a negative value)
	negative_depth = data[!, "water_dept"] .< 0.0
	@assert !any(negative_depth) "error: negative water depth in cells $(data[negative_depth, "id"])!!"

	# compute max eigenvalue for each cell: λ = u + sqrt(g h)
	# (flow_veloc is already the velocity magnitude from BASEMENT results)
	gravity = 9.81
    λi = data[!, "flow_veloc"] .+ sqrt.(gravity .* data[!, "water_dept"])

	# filter non-zero eigenvalues
	mask = λi .!= 0.0
	data_nonzero = data[mask, :]

	# Compute dt and assign it to a new column of data_nonzero
	data_nonzero[!, :λi] = λi[mask]
	CFL = 1.0
	dt = CFL * data_nonzero[!, "ins_rad"] ./ data_nonzero[!, "λi"]
	data_nonzero[!, :Δt] = dt

	# find the minimum time step and return the correspondig cell id
	idx_min = argmin(data_nonzero.Δt)
	println("the cell that controls the time step is: ", data_nonzero[idx_min, "id"])

	idxs_min20 = partialsortperm(data_nonzero.Δt, 1:20)

	OutputPath = joinpath(OutputFolder, InputName*"_min20.txt")
	open(OutputPath, "w") do f
		println(f, "The 20 cells with smaller Δt are: ")
		for i ∈ 1:20
			println(f, "- ", data_nonzero[idxs_min20[i], "id"])
		end
	end
	return nothing
end

main()