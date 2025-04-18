import shutil
import subprocess
import sys
from pathlib import Path
from typing import Literal

import click
import yaml
from pydantic import BaseModel

import autochem


class Input(BaseModel):
    formula: str
    Hf: float
    Tf: Literal[0, 298] = 298
    energy_unit: str = "kJ"
    mess_input: str = "pf.inp"
    nasa_output: str = "therm.nasa"


@click.command()
@click.argument("input_file", type=click.Path(exists=True), default="input.yaml")
def main(input_file: str) -> None:
    # 1. Read input
    input_data = yaml.safe_load(Path(input_file).read_text())
    input = Input.model_validate(input_data)
    formula = input.formula
    Hf = input.Hf
    Tf = input.Tf
    units = {"energy": input.energy_unit}
    mess_inp_name = Path(input.mess_input)
    nasa_out_name = Path(input.nasa_output)

    # 2. Create run directory
    run_path = run_directory()

    # 3. Run MESS-PF and read output
    mess_inp_path = shutil.copyfile(mess_inp_name, run_path / mess_inp_name)
    subprocess.run(["messpf", mess_inp_name], cwd=run_path)
    pf_str = mess_inp_path.with_suffix(".dat").read_text()
    pf_spc = autochem.therm.from_messpf_output_string(
        pf_str, formula=formula, Hf=Hf, Tf=Tf, units=units
    )

    # 4. Run PAC99 and read output (requires copying data files from share/ directory)
    pac_inp_path = run_path / nasa_out_name.with_suffix(".i97")
    pac_inp_path.write_text(autochem.therm.pac99_input_string(pf_spc))
    pac_share_path = Path(sys.prefix) / "share" / "pac99"
    for pac_share_file in pac_share_path.iterdir():
        shutil.copyfile(pac_share_file, run_path / pac_share_file.name)
    subprocess.run(
        ["pac99"],
        input=pac_inp_path.stem.encode(),
        stdout=pac_inp_path.with_suffix(".log").open("w"),
        stderr=pac_inp_path.with_suffix(".err").open("w"),
        cwd=run_path,
    )
    pac_out_str = pac_inp_path.with_suffix(".c97").read_text()
    fit_spc = autochem.therm.from_pac99_output_string(pac_out_str)

    # 5. Write NASA fit in Chemkin format
    nasa_str = autochem.therm.chemkin_string(fit_spc)
    nasa_out_name.write_text(nasa_str)
    print(nasa_str)


def run_directory(path: str = ".", base_name: str = "run") -> Path:
    """Create a new run directory."""
    base_path = Path(path) / base_name
    run_paths = [base_path.with_name(f"{base_name}_{i:02d}") for i in range(100)]
    run_path = next(p for p in run_paths if not p.exists())
    run_path.mkdir()
    return run_path


if __name__ == "__main__":
    main()
