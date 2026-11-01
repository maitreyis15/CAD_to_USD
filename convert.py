from pathlib import Path
import subprocess

# -----------------------------------
# 1. Define project directories
# -----------------------------------

project_dir = Path(__file__).resolve().parent

input_folder = project_dir / "SolidWorks_Pushbuttons"
output_folder = project_dir / "USD_Pushbuttons"

# Use Python environment containing NVIDIA converter
converter_python = (
    project_dir / ".venv" / "Scripts" / "python.exe"
)

output_folder.mkdir(parents=True, exist_ok=True)

# -----------------------------------
# 2. Find all SolidWorks assemblies
# -----------------------------------

assemblies = sorted(
    file for file in input_folder.iterdir()
    if file.is_file()
    and file.suffix.lower() in {".sldasm", ".sldprt", ".step", ".stp"}
)

print(f"\nFound {len(assemblies)} SolidWorks assemblies.")

# -----------------------------------
# 3. Convert every assembly
# -----------------------------------

successful = 0
failed = 0

for index, assembly in enumerate(assemblies, start=1):

    output_file = output_folder / f"{assembly.stem}.usda"

    print(f"\n[{index}/{len(assemblies)}]")
    print(f"Converting: {assembly.name}")

    try:

        result = subprocess.run(
            [
                str(converter_python),
                "-m",
                "usd_convert_cad",
                "-i",
                str(assembly),
                "-o",
                str(output_file)
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0 and output_file.exists():

            print(f"SUCCESS: {output_file.name}")
            successful += 1

        else:

            print(f"FAILED: {assembly.name}")
            print(result.stderr or result.stdout)
            failed += 1

    except Exception as error:

        print(f"ERROR: {error}")
        failed += 1

# -----------------------------------
# 4. Print conversion summary
# -----------------------------------

print("\n==============================")
print("BATCH CONVERSION COMPLETE")
print("==============================")

print(f"Total assemblies: {len(assemblies)}")
print(f"Successful: {successful}")
print(f"Failed: {failed}")

print("==============================")