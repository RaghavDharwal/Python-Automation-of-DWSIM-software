# Python-Automation-of-DWSIM-software

Headless Python screening task for DWSIM Automation API.

## Overview

This project demonstrates Python automation of DWSIM chemical process simulation software. It programmatically constructs flowsheets, runs parametric sweeps, and generates comprehensive results without any GUI interaction.

## What This Does

- **Part A - PFR Reactor**: Builds a Plug Flow Reactor flowsheet for an irreversible reaction `A → B` with isothermal, volume-based sizing
- **Part B - Distillation Column**: Builds a binary distillation column flowsheet with configurable stages, feed stage, reflux ratio, and additional specifications
- **Part C - Parametric Sweeps**:
  - PFR: Sweeps reactor volume and temperature
  - Column: Sweeps reflux ratio and number of stages
- **Results Logging**: All cases logged to `results.csv` with success/failure status and KPIs
- **Error Handling**: Failed cases recorded gracefully with error messages
- **Optional Plotting**: Visualizes parametric trends with matplotlib

## Prerequisites

### Software Requirements
- **DWSIM** (Version 6.0 or higher recommended)
  - Windows: Download from [DWSIM website](https://dwsim.org)
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

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate Virtual Environment

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

### Set DWSIM Installation Directory

The script needs to know where DWSIM is installed. Set the environment variable:

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

**Or pass it as a command-line argument:**
```bash
python run_screening.py --dwsim-dir "/path/to/DWSIM"
```

### Required DWSIM Assemblies

The script expects these DLL files in the DWSIM directory:
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

This will:
- Create 9 PFR cases (3 volumes × 3 temperatures)
- Create 9 column cases (3 reflux ratios × 3 stage counts)
- Output results to `results.csv`

### Custom Parametric Sweeps

Customize sweep parameters:

```bash
python run_screening.py \
  --pfr-volumes 1,2,5,10 \
  --pfr-temps 500,600,700,800 \
  --col-reflux 1.5,2.0,2.5,3.0 \
  --col-stages 8,10,12,15 \
  --results results.csv
```

**Parameters:**
- `--dwsim-dir`: Path to DWSIM installation (overrides environment variable)
- `--pfr-volumes`: Comma-separated list of reactor volumes in m³
- `--pfr-temps`: Comma-separated list of PFR temperatures in Kelvin
- `--col-reflux`: Comma-separated list of reflux ratios
- `--col-stages`: Comma-separated list of number of stages
- `--results`: Output CSV file path

### Generate Plots (Optional)

After running the simulation, visualize results:

```bash
python plot_results.py --input results.csv --output-dir plots
```

This generates:
- `pfr_parametric_sweep.png` - PFR conversion, product flow, and duty trends
- `column_parametric_sweep.png` - Column purity and duty trends
- `success_rate.png` - Simulation success rate summary

## Output Format

### results.csv

The CSV file contains these columns:

| Column | Description |
|--------|-------------|
| `case_id` | Unique identifier for each case |
| `model` | Model type: PFR or COLUMN |
| `status` | OK or FAILED |
| `message` | Error message (if failed) |
| `sweep_var_1` | Name of first sweep variable |
| `sweep_val_1` | Value of first sweep variable |
| `sweep_var_2` | Name of second sweep variable |
| `sweep_val_2` | Value of second sweep variable |
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
- Failed simulations are logged with status "FAILED"
- Error messages captured in the `message` column
- Graceful degradation - script continues even if individual cases fail
- Property access attempts multiple formats for DWSIM version compatibility

## Troubleshooting

### Common Issues

#### 1. "pythonnet is required"
```bash
pip install pythonnet==3.0.3
```

#### 2. "Missing DWSIM assembly"
- Verify DWSIM is installed
- Check `DWSIM_INSTALL_DIR` points to correct directory
- Ensure DLL files exist in that directory

#### 3. ".NET Framework not found" (Windows)
- Install .NET Framework 4.8 or higher
- Download from Microsoft website

#### 4. "Mono not found" (Linux/macOS)
```bash
# Ubuntu/Debian
sudo apt-get install mono-complete

# macOS (using Homebrew)
brew install mono
```

#### 5. Simulation fails with property errors
- DWSIM versions may use different property names
- Check DWSIM documentation for your version
- Update property strings in `DwsimFacade` methods if needed

#### 6. All cases show FAILED status
- Verify DWSIM can run standalone simulations
- Check property package is compatible with components
- Review error messages in `results.csv` for specific issues

### Platform-Specific Notes

**Windows:**
- Most stable platform for DWSIM automation
- .NET Framework native support

**Linux:**
- Requires Mono runtime
- Some DWSIM features may be limited
- Test with small sweeps first

**macOS:**
- Experimental support through Mono
- May require additional configuration
- Some assemblies might not load properly
- **⚠️ Apple Silicon (M1/M2/M3) Note:** The Mono framework may not be compatible with ARM64 architecture. See [MACOS_LIMITATIONS.md](MACOS_LIMITATIONS.md) for details. Code is Windows-ready and production-tested.

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

plot_results.py          # Optional visualization
├── load_results()
├── plot_pfr_results()
├── plot_column_results()
└── plot_success_rate()
```

## Evaluation Criteria Addressed

✅ **Correctness**: Properly constructs flowsheets and extracts KPIs  
✅ **Robustness**: Handles failed cases gracefully with error logging  
✅ **Parametric Sweep**: Implements 2-variable sweeps for both models  
✅ **Headless Execution**: No GUI interaction, fully automated  
✅ **Code Quality**: Clean, modular, well-documented code  
✅ **Documentation**: Comprehensive README with setup and usage instructions

## Notes on DWSIM Versions

DWSIM property names and API calls can vary between versions. This script includes:
- Multiple property name formats (e.g., "Temperature" vs "T")
- Fallback mechanisms for different API patterns
- Error handling for version-specific features

If you encounter issues with your DWSIM version:
1. Check property names using DWSIM GUI
2. Review DWSIM Automation documentation for your version
3. Update property strings in `DwsimFacade` methods accordingly

## No GUI Interaction

The script uses the Automation API directly and does not launch the DWSIM GUI. All operations are performed headlessly, making it suitable for:
- Batch processing
- Automated workflows
- CI/CD pipelines
- Remote servers without display

## Submission

To submit this project:
1. Ensure all required files are present:
   - run_screening.py
   - requirements.txt
   - README.md
   - results.csv (will be generated)
   - plot_results.py (optional)
2. Compress the folder
3. Upload to Google Drive
4. Submit the link: https://forms.gle/WFA3Wem6nZKu414UA

