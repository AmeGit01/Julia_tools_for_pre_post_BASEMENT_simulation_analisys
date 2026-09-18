#!/usr/bin/env julia

using Plots, Plots.Measures, CSV, DataFrames, Infiltrator, Glob

const InputFolder = joinpath("csv_files", "csv_mesh")
const OutputFolder = "reports"

function main()
    InputName = "mesh_results_tend"
	InputFormat = ".csv"
	InputFile = InputName * InputFormat
    InputPath = joinpath(InputFolder, InputFile)
    data = CSV.read(InputPath, DataFrame)

	# compute max eigenvalue for each cell
	gravity = 9.81
    λi = data[!, "water_dept"]*gravity + data[!, "flow_veloc"]

	@assert any(λi .≥ 0.0) "error: some eigenvalues are negative!!"
	
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

	OutputPath = joinpath(OutputFolder, InputName*"min20.txt")
	open(OutputPath, "w") do f
		println(f, "The 20 cells with smaller Δt are: ")
		for i ∈ 1:20
			println(f, "- ", data_nonzero[idxs_min20[i], "id"])
		end
	end
	return nothing
end

main()