# General requirements

No knowledge of the Julia programming language is required. Simply download the complete repository and use the tool. Everything the user needs is:
- Julia installed (this tool was developed using Julia version 1.12.6). Refer to [Installing Julia](https://julialang.org/downloads/) if it is not already installed;
- **Optional**: It is strongly recommended to add an environment variable to avoid manually activating the project every time the user runs any Julia script.

## Optional

### Windows OS
1. Press the **Windows key** and type **"environment variables"**, then press Enter;
2. Click the **Environment Variables...** button at the bottom right;
3. In the **User variables** section (the top one), click **New...**;
4. Enter the following values:
    - **Variable name**: ``JULIA_PROJECT``;
    - **Variable value**: ``@.``;
5. Click **OK** on all windows to save and apply the changes.

### Linux OS
1. Locate the configuration file (``~/.bashrc`` or ``~/.zshrc``);
2. Add the following line at the end of the file: ``export JULIA_PROJECT="@."``;
3. Save the file and refresh the terminal.

This tells Julia to look for a project and automatically activate it when one is found while launching ``julia`` from the terminal.  
If you choose not to set **Optional**, remember to always type ``julia --project=@.`` instead of simply typing ``julia``.

## Performance tips (1. PRE: mesh_stats.jl)

The code has a relatively high **compilation overhead**, which is generally not an issue if the script is executed only a few times. This happens because Julia must be relaunched every time the script is executed. To avoid this overhead, the user can use Julia's *Daemon Mode*, which compiles the script only once (during the first execution) and then reuses the compiled version while allowing different input files.

To use this feature, open a terminal, navigate to the repository, and run the command:
````
julia --startup-file=no -e 'using DaemonMode; serve()'
````

This command starts the server on which the script is executed. Then open a second terminal, navigate again to the repository, and run --- :
````
julia --startup-file=no -e 'using DaemonMode; runargs()' src/mesh_stats.jl inputs/test_mesh.csv inputs/test_regions.txt BASEHPC png 
````

An even shorter command can be obtained by creating an alias. From the second terminal, run:
````
alias juliameshstats='julia --startup-file=no -e "using DaemonMode; runargs()" src/mesh_stats.jl'
````

Then the command becomes:
````
juliameshstats inputs/test_mesh.csv inputs/test_regions.txt BASEHPC png 