#!/usr/bin/env python3
"""
run_screening.py

Headless DWSIM Automation screening script.
- Part A: PFR (A -> B) with isothermal, volume-sized reactor
- Part B: Binary distillation column
- Part C: Parametric sweeps for both models

Note: This script uses pythonnet to load DWSIM .NET assemblies. Adjust
DWSIM assembly paths and property IDs if your DWSIM version differs.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import sys
import traceback
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple


# -----------------------------
# Configuration + Data Models
# -----------------------------

@dataclass
class PFRParams:
    reactor_volume_m3: float
    temperature_k: float
    pressure_pa: float
    feed_mol_s: float
    feed_z_a: float
    k0: float
    ea_jmol: float


@dataclass
class ColumnParams:
    stages: int
    feed_stage: int
    reflux_ratio: float
    pressure_pa: float
    distillate_rate_mol_s: float
    feed_mol_s: float
    feed_z_light: float


@dataclass
class ResultRow:
    case_id: str
    model: str
    status: str
    message: str
    sweep_var_1: str
    sweep_val_1: float
    sweep_var_2: str
    sweep_val_2: float
    conversion: float
    outlet_b_mol_s: float
    reactor_duty_kw: float
    outlet_temp_k: float
    distillate_purity: float
    bottoms_purity: float
    condenser_duty_kw: float
    reboiler_duty_kw: float


# -----------------------------
# DWSIM Automation Wrapper
# -----------------------------

class DwsimFacade:
    """Thin wrapper around DWSIM Automation API.

    This intentionally isolates DWSIM-specific calls so they can be adapted
    for different versions without touching the sweep logic.
    """

    def __init__(self, dwsim_dir: str | None):
        self.dwsim_dir = dwsim_dir or os.environ.get("DWSIM_INSTALL_DIR")
        if not self.dwsim_dir:
            raise RuntimeError(
                "DWSIM install directory not provided. Set DWSIM_INSTALL_DIR."
            )

        self._load_assemblies(self.dwsim_dir)
        self._init_automation()

    def _load_assemblies(self, dwsim_dir: str) -> None:
        try:
            # Configure pythonnet to use Mono on macOS/Linux
            import platform
            if platform.system() in ["Darwin", "Linux"]:
                from pythonnet import load
                try:
                    load("mono")
                    print("Loaded Mono runtime for pythonnet")
                except Exception as e:
                    print(f"Warning: Could not explicitly load Mono: {e}")
                    
            import clr  # type: ignore
        except Exception as exc:
            raise RuntimeError(
                "pythonnet is required. Install with `pip install pythonnet`."
            ) from exc

        # Typical DWSIM installation paths contain these assemblies.
        # Adjust if your DWSIM version places them elsewhere.
        dlls = [
            "DWSIM.Automation.dll",
            "DWSIM.Interfaces.dll",
            "DWSIM.Thermodynamics.dll",
            "DWSIM.UnitOperations.dll",
        ]

        for dll in dlls:
            path = os.path.join(dwsim_dir, dll)
            if not os.path.exists(path):
                raise RuntimeError(f"Missing DWSIM assembly: {path}")
            clr.AddReference(path)

        # Import after adding references
        # pylint: disable=import-error
        import DWSIM.Automation as dwsim_auto  # type: ignore

        self.dwsim_auto = dwsim_auto

    def _init_automation(self) -> None:
        # DWSIM.Automation.Automation3 is the standard entry point
        self.automation = self.dwsim_auto.Automation3()

    # --------- Flowsheet Builders ---------

    def create_simulation(self):
        """Create a new flowsheet with property package."""
        sim = self.automation.CreateFlowsheet()
        
        # Add a property package (using Peng-Robinson as default)
        # Note: Component names must match those in the property package
        try:
            # Add components A and B (using nitrogen and ethane as placeholders)
            # In a real scenario, you would define custom components or use appropriate ones
            self.automation.AddCompound(sim, "Nitrogen")  # Placeholder for A
            self.automation.AddCompound(sim, "Ethane")    # Placeholder for B
            
            # Add property package
            pp = self.automation.AddPropertyPackage(sim, "Peng-Robinson")
            self.automation.SetFlowsheetPropertyPackage(sim, pp)
        except Exception as e:
            print(f"Warning: Property package setup issue: {e}")
            # Continue anyway - some DWSIM versions handle this differently
        
        return sim

    def add_pfr_flowsheet(self, sim, params: PFRParams):
        """Builds a minimal PFR flowsheet.

        Objects:
        - Material stream Feed
        - PFR Reactor
        - Material stream Product
        """
        # NOTE: ObjectType IDs can vary by DWSIM version; update if needed.
        obj = self.dwsim_auto
        try:
            feed = self.automation.AddObject(sim, obj.Enums.ObjectType.MaterialStream, 100, 100, "FEED")
            prod = self.automation.AddObject(sim, obj.Enums.ObjectType.MaterialStream, 400, 100, "PRODUCT")
            pfr = self.automation.AddObject(sim, obj.Enums.ObjectType.PFR, 250, 100, "PFR")

            # Connect streams
            self.automation.ConnectObjects(sim, feed, pfr, 0, 0)
            self.automation.ConnectObjects(sim, pfr, prod, 0, 0)

            # Configure feed composition
            # Using Nitrogen as A and Ethane as B (placeholders)
            self.automation.SetObjectPropertyValue(sim, feed, "Temperature", params.temperature_k)
            self.automation.SetObjectPropertyValue(sim, feed, "Pressure", params.pressure_pa)
            self.automation.SetObjectPropertyValue(sim, feed, "MassFlow", params.feed_mol_s * 28.0)  # Approximate
            
            # Set composition using available components
            comp_a = "Nitrogen"  # Placeholder for A
            comp_b = "Ethane"    # Placeholder for B
            
            # Try both property name formats
            try:
                self.automation.SetObjectPropertyValue(sim, feed, f"Composition.MoleFraction.{comp_a}", params.feed_z_a)
                self.automation.SetObjectPropertyValue(sim, feed, f"Composition.MoleFraction.{comp_b}", 1.0 - params.feed_z_a)
            except:
                self.automation.SetObjectPropertyValue(sim, feed, f"MoleFrac[{comp_a}]", params.feed_z_a)
                self.automation.SetObjectPropertyValue(sim, feed, f"MoleFrac[{comp_b}]", 1.0 - params.feed_z_a)

            # Flash feed to set initial state
            self.automation.SetObjectPropertyValue(sim, feed, "FlashSpec", "TP")

            # Configure reactor
            self.automation.SetObjectPropertyValue(sim, pfr, "ReactionSetID", 0)
            self.automation.SetObjectPropertyValue(sim, pfr, "ReactorOperationMode", "Isothermal")
            self.automation.SetObjectPropertyValue(sim, pfr, "Volume", params.reactor_volume_m3)
            self.automation.SetObjectPropertyValue(sim, pfr, "OutletTemperature", params.temperature_k)

            # Add reaction: A -> B
            # Note: Reaction setup varies significantly by DWSIM version
            # This is a simplified approach - may need adjustment
            try:
                rxn_set = self.automation.GetFlowsheetObject(sim, "ReactionSets")[0]
                reaction = self.automation.CreateReaction(sim, "Conversion")
                self.automation.SetReactionProperty(sim, reaction, "BaseComponent", comp_a)
                self.automation.SetReactionProperty(sim, reaction, "ReactionBasis", "Molar")
                self.automation.SetReactionProperty(sim, reaction, "Expression", str(params.k0))
                self.automation.AddReactionToSet(sim, rxn_set, reaction)
            except Exception as e:
                print(f"Warning: Reaction setup issue: {e}")

        except Exception as e:
            raise RuntimeError(f"Failed to build PFR flowsheet: {e}") from e

        return feed, pfr, prod

    def add_column_flowsheet(self, sim, params: ColumnParams):
        """Builds a minimal distillation column flowsheet.

        Objects:
        - Material stream Feed
        - Distillation Column
        - Material stream Distillate
        - Material stream Bottoms
        """
        obj = self.dwsim_auto
        try:
            feed = self.automation.AddObject(sim, obj.Enums.ObjectType.MaterialStream, 100, 300, "FEED_COL")
            dist = self.automation.AddObject(sim, obj.Enums.ObjectType.MaterialStream, 400, 200, "DIST")
            bot = self.automation.AddObject(sim, obj.Enums.ObjectType.MaterialStream, 400, 400, "BOT")
            col = self.automation.AddObject(sim, obj.Enums.ObjectType.DistillationColumn, 250, 300, "COLUMN")

            # Connect streams
            self.automation.ConnectObjects(sim, feed, col, 0, 0)
            self.automation.ConnectObjects(sim, col, dist, 0, 0)
            self.automation.ConnectObjects(sim, col, bot, 1, 0)

            # Use Nitrogen (light) and Ethane (heavy) as binary mixture
            light_comp = "Nitrogen"
            heavy_comp = "Ethane"

            # Feed conditions
            self.automation.SetObjectPropertyValue(sim, feed, "Temperature", 350.0)
            self.automation.SetObjectPropertyValue(sim, feed, "Pressure", params.pressure_pa)
            self.automation.SetObjectPropertyValue(sim, feed, "MassFlow", params.feed_mol_s * 29.0)  # Approximate MW
            
            # Set composition
            try:
                self.automation.SetObjectPropertyValue(sim, feed, f"Composition.MoleFraction.{light_comp}", params.feed_z_light)
                self.automation.SetObjectPropertyValue(sim, feed, f"Composition.MoleFraction.{heavy_comp}", 1.0 - params.feed_z_light)
            except:
                self.automation.SetObjectPropertyValue(sim, feed, f"MoleFrac[{light_comp}]", params.feed_z_light)
                self.automation.SetObjectPropertyValue(sim, feed, f"MoleFrac[{heavy_comp}]", 1.0 - params.feed_z_light)

            # Flash feed
            self.automation.SetObjectPropertyValue(sim, feed, "FlashSpec", "TP")

            # Column specifications
            self.automation.SetObjectPropertyValue(sim, col, "NumberOfStages", params.stages)
            self.automation.SetObjectPropertyValue(sim, col, "CondenserType", "Total")
            self.automation.SetObjectPropertyValue(sim, col, "ReboilerType", "Kettle")
            
            # Feed stage (1-indexed)
            feed_stage_idx = max(1, min(params.feed_stage, params.stages))
            self.automation.SetObjectPropertyValue(sim, col, "FeedStageNumber", feed_stage_idx)
            
            # Column operating specs
            self.automation.SetObjectPropertyValue(sim, col, "CondenserPressure", params.pressure_pa)
            self.automation.SetObjectPropertyValue(sim, col, "RefluxRatio", params.reflux_ratio)
            self.automation.SetObjectPropertyValue(sim, col, "DistillateFlowRate", params.distillate_rate_mol_s)

        except Exception as e:
            raise RuntimeError(f"Failed to build distillation column flowsheet: {e}") from e

        return feed, col, dist, bot

    # --------- Simulation + Results ---------

    def solve(self, sim) -> None:
        self.automation.CalculateFlowsheet(sim)

    def get_pfr_results(self, sim, pfr, prod) -> Tuple[float, float, float, float]:
        """Extract PFR simulation results with error handling."""
        try:
            # Conversion - try multiple property names
            conv = 0.0
            for prop in ["Conversion", "ReactionConversion", "X"]:
                try:
                    conv = float(self.automation.GetObjectPropertyValue(sim, pfr, prop))
                    if conv > 0:
                        break
                except:
                    continue
            
            # Outlet composition for B
            b_flow = 0.0
            comp_b = "Ethane"  # Placeholder for B
            try:
                total_flow = float(self.automation.GetObjectPropertyValue(sim, prod, "MolarFlow"))
                try:
                    b_frac = float(self.automation.GetObjectPropertyValue(sim, prod, f"Composition.MoleFraction.{comp_b}"))
                except:
                    b_frac = float(self.automation.GetObjectPropertyValue(sim, prod, f"MoleFrac[{comp_b}]"))
                b_flow = total_flow * b_frac
            except Exception as e:
                print(f"Warning: Could not calculate B flow: {e}")
            
            # Heat duty
            duty_kw = 0.0
            for prop in ["HeatLoad", "HeatDuty", "DutyValue"]:
                try:
                    duty_w = float(self.automation.GetObjectPropertyValue(sim, pfr, prop))
                    duty_kw = duty_w / 1000.0
                    break
                except:
                    continue
            
            # Outlet temperature
            t_out = 0.0
            for prop in ["Temperature", "T", "OutletTemperature"]:
                try:
                    t_out = float(self.automation.GetObjectPropertyValue(sim, prod, prop))
                    if t_out > 0:
                        break
                except:
                    continue
                    
            return conv, b_flow, duty_kw, t_out
        except Exception as e:
            raise RuntimeError(f"Failed to extract PFR results: {e}") from e

    def get_column_results(self, sim, col, dist, bot) -> Tuple[float, float, float, float]:
        """Extract distillation column simulation results with error handling."""
        try:
            light_comp = "Nitrogen"
            heavy_comp = "Ethane"
            
            # Distillate purity (light component)
            x_d = 0.0
            try:
                x_d = float(self.automation.GetObjectPropertyValue(sim, dist, f"Composition.MoleFraction.{light_comp}"))
            except:
                try:
                    x_d = float(self.automation.GetObjectPropertyValue(sim, dist, f"MoleFrac[{light_comp}]"))
                except:
                    pass
            
            # Bottoms purity (heavy component)
            x_b = 0.0
            try:
                x_b = float(self.automation.GetObjectPropertyValue(sim, bot, f"Composition.MoleFraction.{heavy_comp}"))
            except:
                try:
                    x_b = float(self.automation.GetObjectPropertyValue(sim, bot, f"MoleFrac[{heavy_comp}]"))
                except:
                    pass
            
            # Condenser duty
            q_c = 0.0
            for prop in ["CondenserDuty", "CondenserHeatLoad", "QCondenser"]:
                try:
                    q_c_w = float(self.automation.GetObjectPropertyValue(sim, col, prop))
                    q_c = abs(q_c_w) / 1000.0  # Convert to kW and take absolute value
                    break
                except:
                    continue
            
            # Reboiler duty
            q_r = 0.0
            for prop in ["ReboilerDuty", "ReboilerHeatLoad", "QReboiler"]:
                try:
                    q_r_w = float(self.automation.GetObjectPropertyValue(sim, col, prop))
                    q_r = abs(q_r_w) / 1000.0  # Convert to kW and take absolute value
                    break
                except:
                    continue
                    
            return x_d, x_b, q_c, q_r
        except Exception as e:
            raise RuntimeError(f"Failed to extract column results: {e}") from e


# -----------------------------
# Sweep Logic
# -----------------------------

def sweep_pfr(dwsim: DwsimFacade, vol_list: List[float], t_list: List[float]) -> List[ResultRow]:
    rows: List[ResultRow] = []
    base = PFRParams(
        reactor_volume_m3=1.0,
        temperature_k=600.0,
        pressure_pa=101325.0,
        feed_mol_s=10.0,
        feed_z_a=1.0,
        k0=1.0e6,
        ea_jmol=80000.0,
    )

    for v in vol_list:
        for t in t_list:
            case_id = f"PFR_V{v}_T{t}"
            params = PFRParams(**{**asdict(base), "reactor_volume_m3": v, "temperature_k": t})
            rows.append(run_pfr_case(dwsim, params, "reactor_volume_m3", v, "temperature_k", t, case_id))

    return rows


def run_pfr_case(
    dwsim: DwsimFacade,
    params: PFRParams,
    var1: str,
    val1: float,
    var2: str,
    val2: float,
    case_id: str,
) -> ResultRow:
    try:
        sim = dwsim.create_simulation()
        _, pfr, prod = dwsim.add_pfr_flowsheet(sim, params)
        dwsim.solve(sim)
        conv, b_flow, duty_kw, t_out = dwsim.get_pfr_results(sim, pfr, prod)
        return ResultRow(
            case_id=case_id,
            model="PFR",
            status="OK",
            message="",
            sweep_var_1=var1,
            sweep_val_1=val1,
            sweep_var_2=var2,
            sweep_val_2=val2,
            conversion=conv,
            outlet_b_mol_s=b_flow,
            reactor_duty_kw=duty_kw,
            outlet_temp_k=t_out,
            distillate_purity=0.0,
            bottoms_purity=0.0,
            condenser_duty_kw=0.0,
            reboiler_duty_kw=0.0,
        )
    except Exception as exc:
        return ResultRow(
            case_id=case_id,
            model="PFR",
            status="FAILED",
            message=f"{exc.__class__.__name__}: {exc}",
            sweep_var_1=var1,
            sweep_val_1=val1,
            sweep_var_2=var2,
            sweep_val_2=val2,
            conversion=0.0,
            outlet_b_mol_s=0.0,
            reactor_duty_kw=0.0,
            outlet_temp_k=0.0,
            distillate_purity=0.0,
            bottoms_purity=0.0,
            condenser_duty_kw=0.0,
            reboiler_duty_kw=0.0,
        )


def sweep_column(dwsim: DwsimFacade, rr_list: List[float], stages_list: List[int]) -> List[ResultRow]:
    rows: List[ResultRow] = []
    base = ColumnParams(
        stages=10,
        feed_stage=5,
        reflux_ratio=2.0,
        pressure_pa=101325.0,
        distillate_rate_mol_s=4.0,
        feed_mol_s=10.0,
        feed_z_light=0.5,
    )

    for rr in rr_list:
        for n in stages_list:
            case_id = f"COL_RR{rr}_N{n}"
            params = ColumnParams(**{**asdict(base), "reflux_ratio": rr, "stages": n})
            rows.append(run_column_case(dwsim, params, "reflux_ratio", rr, "stages", float(n), case_id))

    return rows


def run_column_case(
    dwsim: DwsimFacade,
    params: ColumnParams,
    var1: str,
    val1: float,
    var2: str,
    val2: float,
    case_id: str,
) -> ResultRow:
    try:
        sim = dwsim.create_simulation()
        _, col, dist, bot = dwsim.add_column_flowsheet(sim, params)
        dwsim.solve(sim)
        x_d, x_b, q_c, q_r = dwsim.get_column_results(sim, col, dist, bot)
        return ResultRow(
            case_id=case_id,
            model="COLUMN",
            status="OK",
            message="",
            sweep_var_1=var1,
            sweep_val_1=val1,
            sweep_var_2=var2,
            sweep_val_2=val2,
            conversion=0.0,
            outlet_b_mol_s=0.0,
            reactor_duty_kw=0.0,
            outlet_temp_k=0.0,
            distillate_purity=x_d,
            bottoms_purity=x_b,
            condenser_duty_kw=q_c,
            reboiler_duty_kw=q_r,
        )
    except Exception as exc:
        return ResultRow(
            case_id=case_id,
            model="COLUMN",
            status="FAILED",
            message=f"{exc.__class__.__name__}: {exc}",
            sweep_var_1=var1,
            sweep_val_1=val1,
            sweep_var_2=var2,
            sweep_val_2=val2,
            conversion=0.0,
            outlet_b_mol_s=0.0,
            reactor_duty_kw=0.0,
            outlet_temp_k=0.0,
            distillate_purity=0.0,
            bottoms_purity=0.0,
            condenser_duty_kw=0.0,
            reboiler_duty_kw=0.0,
        )


# -----------------------------
# IO + CLI
# -----------------------------

def write_results(path: str, rows: List[ResultRow]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def parse_list(arg: str) -> List[float]:
    return [float(x.strip()) for x in arg.split(",") if x.strip()]


def parse_list_int(arg: str) -> List[int]:
    return [int(x.strip()) for x in arg.split(",") if x.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Headless DWSIM screening script")
    parser.add_argument("--dwsim-dir", default=os.environ.get("DWSIM_INSTALL_DIR"), help="DWSIM install dir")
    parser.add_argument("--pfr-volumes", default="1,2,5", help="Comma list of reactor volumes (m3)")
    parser.add_argument("--pfr-temps", default="500,600,700", help="Comma list of PFR temperatures (K)")
    parser.add_argument("--col-reflux", default="1.5,2.0,3.0", help="Comma list of reflux ratios")
    parser.add_argument("--col-stages", default="8,10,12", help="Comma list of number of stages")
    parser.add_argument("--results", default="results.csv", help="Output CSV path")

    args = parser.parse_args()

    try:
        dwsim = DwsimFacade(args.dwsim_dir)
    except Exception as exc:
        print(f"Failed to initialize DWSIM: {exc}", file=sys.stderr)
        return 2

    rows: List[ResultRow] = []

    try:
        rows.extend(sweep_pfr(dwsim, parse_list(args.pfr_volumes), parse_list(args.pfr_temps)))
        rows.extend(sweep_column(dwsim, parse_list(args.col_reflux), parse_list_int(args.col_stages)))
    except Exception as exc:
        print("Unexpected failure during sweep", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return 3

    if not rows:
        print("No results produced.", file=sys.stderr)
        return 4

    write_results(args.results, rows)
    print(f"Wrote {len(rows)} cases to {args.results}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
