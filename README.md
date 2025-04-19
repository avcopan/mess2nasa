# mess2nasa

Generates thermochemical NASA polynomial fits in Chemkin format, using MESS-PF and
PAC99.

## Install

This code can be installed by running `pixi install` in this directory.
If you haven't installed pixi before, you will first need to install it by running
`curl -fsSL https://pixi.sh/install.sh | sh`.

## Activate

To run, you will need to first activate the Pixi environment as follows.
```
pixi shell --manifest-path /path/to/mess2nasa
```
If you are in a subfolder of this directory, you can simply use `pixi shell`.

## Quick Start

### Prepare Input Files

Electronic structure data is provided through an input file for the `MESS-PF` program,
which is part of the `MESS` master equation code and accepts the same keywords.
```
!===================================================
!  GLOBAL KEYWORDS
!===================================================
TemperatureList[K]       200.0  300.0 <...temperatures...> 3000.0
RelativeTemperatureIncrement           0.001
AtomDistanceMin[angstrom]              0.32
Species NH2NO
  RRHO
    Geometry[angstrom]			5
N         -0.0188331238        0.1790351320       -1.0728609547
N          0.0025820100       -0.4917280515        0.0756162504
O          0.0015612045        0.2219836321        1.0589297274
H          0.0852906695        1.1854045799       -1.0448633445
H          0.1157591360       -0.3637376222       -1.9058409446
    Core	RigidRotor
      SymmetryFactor 			0.5
    End  ! Core
    Frequencies[1/cm]			9
187	627	580	1023	1255	1522	1614	3298	3465
    ZeroEnergy[kcal/mol]			-45.79
End
```
With such a file in place, running the code is very simple.
The input for `mess2nasa` is a simple YAML file that looks as follows.
```
formula: NH2NO
Hf: 76.95
Tf: 298
energy_unit: kJ
mess_input: pf.inp
nasa_output: fit.nasa
```
Here, `Hf` is the heat of formation in units of `energy_unit` per mol at reference
temperature `Tf`, which an be either `0` or `298` (alias for $298.15~\text{K}$).
The formula `NH2NO` in this example will be correctly interpreted as 
$\text{N}_2 \text{H}_2 \text{O}_1$.
The `mess_input` field is the name of your `MESS-PF` input file, which should have a `.inp` extension.

### Run

If the YAML input file is given the default name of `input.yaml`, one can simply run
`mess2nasa`.
If another name is used, it must be passed as an argument.
```
mess2nasa <input file name>.yaml
```
Under the hood, this does the following:
1. Run `MESS-PF` to calculate the partition function.
2. Generate thermodynamic function values needed for input to `PAC99`.
3. Run `PAC99` to fit the thermodynamic data to a 7-coefficient NASA polynomial.
4. Put the fitted NASA polynomial in Chemkin format.

The `MESS-PF` and `PAC99` runs will be performed in a subdirectory `run_01` which will increment with successive runs.
The final Chemkin-formatted NASA polynomial is written to the `nasa_output` file specified in the input YAML.
