# QUICK START GUIDE

## For Windows Users

### Step 1: Install Prerequisites
1. Install DWSIM from https://dwsim.org (if not already installed)
2. Install Python 3.9+ from https://python.org (if not already installed)

### Step 2: Setup
Open PowerShell in this directory and run:

```powershell
# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Set DWSIM path (adjust if your installation is different)
$env:DWSIM_INSTALL_DIR = "C:\Program Files\DWSIM"
```

### Step 3: Run
```powershell
# Run the main screening script
python run_screening.py

# Generate plots (optional)
python plot_results.py
```

### Step 4: View Results
- Open `results.csv` in Excel or any spreadsheet program
- View plots in the current directory (if generated)

---

## For Linux/macOS Users

### Step 1: Install Prerequisites
1. Install DWSIM (requires Mono):
   ```bash
   # Ubuntu/Debian
   sudo apt-get install mono-complete
   
   # macOS
   brew install mono
   ```
   Download DWSIM from https://dwsim.org

2. Install Python 3.9+:
   ```bash
   # Most systems have Python pre-installed
   python3 --version
   ```

### Step 2: Setup
Open terminal in this directory and run:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set DWSIM path (adjust to your installation)
export DWSIM_INSTALL_DIR="/path/to/DWSIM"
```

### Step 3: Run
```bash
# Run the main screening script
python run_screening.py

# Generate plots (optional)
python plot_results.py
```

### Step 4: View Results
- Open `results.csv` in your preferred spreadsheet application
- View plots in the current directory (if generated)

---

## Customizing Parameters

Edit the command to sweep different values:

```bash
python run_screening.py \
  --pfr-volumes 1,2,5,10 \
  --pfr-temps 500,600,700,800 \
  --col-reflux 1.5,2.0,2.5,3.0 \
  --col-stages 8,10,12,15
```

---

## Troubleshooting

### Error: "Missing DWSIM assembly"
- Make sure DWSIM is installed
- Verify the DWSIM_INSTALL_DIR path is correct
- Check that DLL files exist in that directory

### Error: "pythonnet is required"
```bash
pip install pythonnet==3.0.3
```

### All simulations fail
- Check DWSIM can run standalone
- Review error messages in results.csv
- Ensure .NET Framework (Windows) or Mono (Linux/macOS) is installed

---

## What Gets Generated

After running `python run_screening.py`:
- **results.csv** - All simulation results with KPIs

After running `python plot_results.py`:
- **pfr_parametric_sweep.png** - PFR trends
- **column_parametric_sweep.png** - Column trends
- **success_rate.png** - Summary statistics

---

## Need Help?

See the comprehensive README.md file for detailed documentation.
