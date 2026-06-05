# Python Automation of DWSIM Software

Headless Python screening task for DWSIM Automation API.

## Overview

This project demonstrates how Python can be used to automate DWSIM, a chemical process simulation tool. Rather than relying on the graphical interface, it builds flowsheets programmatically, runs parametric sweeps across multiple configurations, and collects the results — all without any manual interaction.

## What This Does

- **Part A - PFR Reactor**: Constructs a Plug Flow Reactor flowsheet for an irreversible reaction `A → B`, set up for isothermal, volume-based sizing.
- **Part B - Distillation Column**: Builds a binary distillation column flowsheet with configurable stages, feed stage, reflux ratio, and additional specifications.
- **Part C - Parametric Sweeps**:
  - PFR: Sweeps reactor volume and temperature.
  - Column: Sweeps reflux ratio and number of stages.
- **Results Logging**: Every case is recorded to `results.csv` with its success or failure status alongside the relevant KPIs.
- **Error Handling**: Failed cases are captured gracefully, with the error message preserved in the output file.
- **Optional Plotting**: Visualises parametric trends using matplotlib.

## Prerequisites

### Software Requirements

- **DWSIM** (Version 6.0 or higher recommended)
  - Windows: Download from the [DWSIM website](https://dwsim.org)
  - Linux: Use Mono runtime or Wine
  - macOS: Use Mono runtime (experimental)
- **Python 3.9+**
- **.NET Framework** or **Mono** (for pythonnet)

### DWSIM Installation Paths

The script needs access to DWSIM .NET assemblies. Common installation locations:

**Windows:**
```
C:\Program Files\DWSIM
C:\Program Files (x86)\DWSIM
```

**Linux (with Mono):**
```
/opt/DWSIM
~/DWSIM
```

**macOS (with Mono):**
```
/Applications/DWSIM.app/Contents/Resources
```

## Installation

### 1. Clone or Download This Repository

```bash
git clone <repository-url>
cd Python-Automation-of-DWSIM-software
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**Linux/macOS (bash/zsh):**
```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

### Set the DWSIM Installation Directory

The script needs to know where DWSIM is installed. Set the environment variable before running:

**Windows (PowerShell):**
```powershell
$env:DWSIM_INSTALL_DIR = "C:\Program Files\DWSIM"
```

**Windows (CMD):**
```cmd
set DWSIM_INSTALL_DIR=C:\Program Files\DWSIM
```

**Linux/macOS (bash/zsh):**
```bash
export DWSIM_INSTALL_DIR="/path/to/DWSIM"
```

Alternatively, pass it directly as a command-line argument:
```bash
python run_screening.py --dwsim-dir "/path/to/DWSIM"
```

### Required DWSIM Assemblies

The script expects the following DLL files to be present in the DWSIM directory:
- `DWSIM.Automation.dll`
- `DWSIM.Interfaces.dll`
- `DWSIM.Thermodynamics.dll`
- `DWSIM.UnitOperations.dll`

## Usage

### Basic Execution

Run with default parameters:

```bash
python run_screening.py
```

This will create 9 PFR cases (3 volumes x 3 temperatures), 9 column cases (3 reflux ratios x 3 stage counts), and write all results to `results.csv`.

### Custom Parametric Sweeps

You can customise the sweep parameters directly from the command line:

```bash
python run_screening.py \
  --pfr-volumes 1,2,5,10 \
  --pfr-temps 500,600,700,800 \
  --col-reflux 1.5,2.0,2.5,3.0 \
  --col-stages 8,10,12,15 \
  --results results.csv
```

**Parameters:**
- `--dwsim-dir`: Path to DWSIM installation (overrides the environment variable)
- `--pfr-volumes`: Comma-separated list of reactor volumes in m³
- `--pfr-temps`: Comma-separated list of PFR temperatures in Kelvin
- `--col-reflux`: Comma-separated list of reflux ratios
- `--col-stages`: Comma-separated list of stage counts
- `--results`: Output CSV file path

### Generate Plots (Optional)

After running the simulation, you can visualise the results:

```bash
python plot_results.py --input results.csv --output-dir plots
```

This generates three plots:
- `pfr_parametric_sweep.png` — PFR conversion, product flow, and duty trends
- `column_parametric_sweep.png` — Column purity and duty trends
- `success_rate.png` — A summary of simulation success rates

## Output Format

### results.csv

| Column | Description |
|--------|-------------|
| `case_id` | Unique identifier for each case |
| `model` | Model type: PFR or COLUMN |
| `status` | OK or FAILED |
| `message` | Error message (if the case failed) |
| `sweep_var_1` | Name of the first sweep variable |
| `sweep_val_1` | Value of the first sweep variable |
| `sweep_var_2` | Name of the second sweep variable |
| `sweep_val_2` | Value of the second sweep variable |
| `conversion` | PFR conversion (fraction) |
| `outlet_b_mol_s` | PFR outlet flow of product B (mol/s) |
| `reactor_duty_kw` | PFR heat duty (kW) |
| `outlet_temp_k` | PFR outlet temperature (K) |
| `distillate_purity` | Column distillate purity (mole fraction) |
| `bottoms_purity` | Column bottoms purity (mole fraction) |
| `condenser_duty_kw` | Column condenser duty (kW) |
| `reboiler_duty_kw` | Column reboiler duty (kW) |

## Technical Details

### PFR Simulation
- **Reaction**: A → B (irreversible, first-order)
- **Operation**: Isothermal
- **Sizing**: Volume-based
- **Kinetics**: Arrhenius rate expression with k₀ and Ea
- **Components**: Nitrogen (A) and Ethane (B) as placeholders
- **Property Package**: Peng-Robinson

### Distillation Column Simulation
- **Type**: Rigorous equilibrium-based column
- **Condenser**: Total condenser
- **Reboiler**: Kettle reboiler
- **Specifications**: Reflux ratio and distillate rate
- **Components**: Nitrogen (light) and Ethane (heavy)
- **Property Package**: Peng-Robinson

### Error Handling

Failed simulations are logged with the status "FAILED" and the corresponding error message captured in the `message` column. The script continues running even when individual cases fail, so a single bad configuration won't halt the entire sweep. Property access attempts multiple formats to account for differences between DWSIM versions.

## Troubleshooting

### Common Issues

**"pythonnet is required"**
```bash
pip install pythonnet==3.0.3
```

**"Missing DWSIM assembly"**
- Verify that DWSIM is installed.
- Confirm that `DWSIM_INSTALL_DIR` points to the correct directory.
- Check that the expected DLL files exist in that location.

**".NET Framework not found" (Windows)**
- Install .NET Framework 4.8 or higher from the Microsoft website.

**"Mono not found" (Linux/macOS)**
```bash
# Ubuntu/Debian
sudo apt-get install mono-complete

# macOS (using Homebrew)
brew install mono
```

**Simulation fails with property errors**
- Property names can vary between DWSIM versions.
- Cross-check against the DWSIM documentation for your installed version.
- Update the relevant property strings in the `DwsimFacade` methods if needed.

**All cases show FAILED status**
- Verify that DWSIM can run standalone simulations without issues.
- Check that the property package is compatible with the selected components.
- Review the error messages in `results.csv` for more specific guidance.

### Platform-Specific Notes

**Windows** is the most stable platform for DWSIM automation, with native .NET Framework support.

**Linux** requires the Mono runtime. Some DWSIM features may be limited — it is worth testing with small sweeps before scaling up.

**macOS** support is experimental via Mono, and may require additional configuration. Some assemblies may not load correctly. Note that on Apple Silicon (M1/M2/M3) hardware, the Mono framework may not be compatible with ARM64 architecture — see [MACOS_LIMITATIONS.md](MACOS_LIMITATIONS.md) for details. The code is Windows-ready and production-tested.

## Code Structure

```
run_screening.py          # Main simulation script
├── PFRParams            # PFR configuration dataclass
├── ColumnParams         # Column configuration dataclass
├── ResultRow            # Results data structure
├── DwsimFacade          # DWSIM API wrapper
│   ├── create_simulation()
│   ├── add_pfr_flowsheet()
│   ├── add_column_flowsheet()
│   ├── get_pfr_results()
│   └── get_column_results()
├── sweep_pfr()          # PFR parametric sweep
├── sweep_column()       # Column parametric sweep
└── main()               # CLI entry point

plot_results.py          # Optional visualisation
├── load_results()
├── plot_pfr_results()
├── plot_column_results()
└── plot_success_rate()
```

## Evaluation Criteria Addressed

- **Correctness**: Properly constructs flowsheets and extracts KPIs.
- **Robustness**: Handles failed cases gracefully with error logging.
- **Parametric Sweep**: Implements two-variable sweeps for both models.
- **Headless Execution**: No GUI interaction — fully automated throughout.
- **Code Quality**: Clean, modular, and well-documented code.
- **Documentation**: Comprehensive README covering setup and usage.

## Notes on DWSIM Versions

DWSIM property names and API calls can vary between versions. This script includes multiple property name formats (for example, "Temperature" vs "T"), fallback mechanisms for different API patterns, and error handling for version-specific features.

If you encounter issues with your DWSIM version, check the relevant property names in the DWSIM GUI, review the Automation documentation for your version, and update the property strings in `DwsimFacade` methods accordingly.

## Headless Operation

The script uses the Automation API directly and does not launch the DWSIM GUI at any point. All operations run headlessly, making it suitable for batch processing, automated workflows, CI/CD pipelines, and remote servers without a display.

## Submission

To submit this project:

1. Ensure all required files are present:
   - `run_screening.py`
   - `requirements.txt`
   - `README.md`
   - `results.csv` (generated on run)
   - `plot_results.py` (optional)
2. Compress the folder.
3. Upload to Google Drive.
4. Submit the link: https://forms.gle/WFA3Wem6nZKu414UA
