"""
================================================================================
  TURBINE ENGINE THRUST CALCULATOR
================================================================================

  Author: Prasenjit Das, Bangalore
  License: GNU General Public License v3.0 (GPL-3.0)
  
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  
  For details, see the LICENSE file.

  Description:
  Calculates thrust output from a gas turbine engine including compressor,
  combustor, turbine, and nozzle performance with detailed thermodynamic analysis.

================================================================================
"""

import math

def _get_float(prompt, default=None, validator=None, err_msg=None):
	"""Prompt for a float with optional default and validator.
	Returns a float. Keeps prompting until valid input is given.
	"""
	while True:
		if default is None:
			s = input(f"  {prompt}: ")
		else:
			s = input(f"  {prompt}\n     [default: {default}] → ")
		if s.strip() == "":
			if default is not None:
				value = default
				print(f"     ✓ Using default: {value}\n")
				return float(value)
			else:
				print("     ✗ Input required. Please try again.\n")
				continue
		try:
			value = float(s)
		except ValueError:
			print("     ✗ Invalid input. Please enter a valid number.\n")
			continue
		if validator and not validator(value):
			print(f"     ✗ {err_msg or 'Value out of allowed range.'}\n")
			continue
		print(f"     ✓ Value accepted: {value}\n")
		return value


def _get_compressor_pressure_ratios():
	"""Get compressor pressure ratios either by stage or as one overall ratio."""
	while True:
		mode = input(
			"  Compressor pressure-ratio input mode (1=LP and HP separately, 2=overall)\n"
			"     [default: 1] → "
		).strip()
		if mode == "":
			mode = "1"
		if mode not in ("1", "2"):
			print("     ✗ Please enter 1 or 2.\n")
			continue
		break

	if mode == "1":
		low_pressure_ratio = _get_float(
			"Low-pressure compressor (LPC) pressure ratio (unitless, >=1)",
			default=3.0,
			validator=lambda x: x >= 1.0,
			err_msg="Pressure ratio must be >= 1.0",
		)
		high_pressure_ratio = _get_float(
			"High-pressure compressor (HPC) pressure ratio (unitless, >=1)",
			default=5.0,
			validator=lambda x: x >= 1.0,
			err_msg="Pressure ratio must be >= 1.0",
		)
		return low_pressure_ratio, high_pressure_ratio

	overall_ratio = _get_float(
		"Overall compressor pressure ratio (unitless, >=1)",
		default=15.0,
		validator=lambda x: x >= 1.0,
		err_msg="Pressure ratio must be >= 1.0",
	)
	stage_ratio = math.sqrt(overall_ratio)
	print(f"     ✓ Equal stage pressure ratios: {stage_ratio:.4f} (LPC and HPC)\n")
	return stage_ratio, stage_ratio



def _get_temp(prompt, default=None, default_unit='K', validator=None, err_msg=None):
	"""Prompt for a temperature. Accepts numeric with optional unit suffix 'C' or 'K'.
	Returns temperature in Kelvin.
	If user enters a plain number, it's interpreted in `default_unit`.
	"""
	while True:
		if default is None:
			s = input(f"  {prompt}: ")
		else:
			s = input(f"  {prompt}\n     [default: {default}{default_unit}] → ")
		if s.strip() == "":
			if default is not None:
				val = default
				unit = default_unit.lower()
				print(f"     ✓ Using default: {val}{default_unit}\n")
				# convert to K below
			else:
				print("     ✗ Input required. Please try again.\n")
				continue
		else:
			s2 = s.strip().replace('°', '')
			# detect unit suffix
			if len(s2) > 0 and s2[-1].lower() in ('c', 'k'):
				unit = s2[-1].lower()
				num_s = s2[:-1]
			else:
				unit = default_unit.lower()
				num_s = s2
			try:
				val = float(num_s)
			except Exception:
				print("     ✗ Invalid input. Please enter a temperature (e.g. 25C or 298K).\n")
				continue
		# convert to Kelvin
		if unit == 'c':
			kelvin = val + 273.15
		else:
			kelvin = val
		if validator and not validator(kelvin):
			print(f"     ✗ {err_msg or 'Value out of allowed range.'}\n")
			continue
		print(f"     ✓ Value accepted: {val}{unit.upper()} ({kelvin:.2f}K)\n")
		return kelvin


# Improved, validated inputs
print("\n" + "="*60)
print("  COMPRESSOR & TURBINE CONFIGURATION")
print("="*60 + "\n")

Compressor_Stage_1_Pressure_Ratio, Compressor_Stage_2_Pressure_Ratio = _get_compressor_pressure_ratios()
Compressor_And_Turbine_Efficiency = _get_float(
	"Compressor efficiency per stage (fraction, e.g. 0.88)",
	default=0.88,
	validator=lambda x: 0.0 < x <= 1.0,
	err_msg="Efficiency must be between 0 (exclusive) and 1 (inclusive)",
)
Core_Mass_Flow_Rate = _get_float(
	"Core mass flow rate (kg/s)", default=1.0, validator=lambda x: x > 0.0, err_msg="Must be > 0"
)
Bypass_Ratio = _get_float(
	"Bypass ratio (dimensionless, 0 for turbojet)",
	default=2.0,
	validator=lambda x: x >= 0.0,
	err_msg="Bypass ratio must be >= 0",
)
Bleed_Percentage = _get_float(
	"Bleed air extracted from core flow (%)",
	default=0.0,
	validator=lambda x: 0.0 <= x <= 100.0,
	err_msg="Bleed percentage must be between 0 and 100",
)
Bleed_Fraction = Bleed_Percentage / 100.0
Usable_Core_Mass_Flow_Rate = Core_Mass_Flow_Rate * (1.0 - Bleed_Fraction)
Inlet_Mass_Flow_Rate = Core_Mass_Flow_Rate * (1 + Bypass_Ratio)
Compressor_Design_Pressure_Ratio = Compressor_Stage_1_Pressure_Ratio * Compressor_Stage_2_Pressure_Ratio
print(f"Overall two-stage military turbofan compressor pressure ratio: {Compressor_Design_Pressure_Ratio:.4f}")
print(f"Core mass flow rate: {Core_Mass_Flow_Rate:.3f} kg/s")
print(f"Bleed air extracted: {Bleed_Percentage:.2f}% ({Bleed_Fraction:.4f} fraction)")
print(f"Usable core mass flow rate: {Usable_Core_Mass_Flow_Rate:.3f} kg/s")
print(f"Bypass ratio: {Bypass_Ratio:.3f}")
print(f"Total inlet mass flow rate: {Inlet_Mass_Flow_Rate:.3f} kg/s")

print("="*60)
print("  TEMPERATURE INPUTS")
print("="*60 + "\n")

TET = _get_temp("Turbine entry temperature", default=1400.0, default_unit='K', validator=lambda x: x > 0.0)

# Two-stage military turbofan compressor model.
# This assumes a conventional series compressor without intercooling: stage 2 starts from
# the outlet temperature of stage 1 and continues to the final compressor discharge pressure.
# The overall compressor pressure ratio is the product of the LPC and HPC pressure ratios.
temp_k = _get_temp(
	"Inlet temperature", default=15.0, default_unit='C', validator=lambda x: x > 0.0, err_msg="Temperature must be > -273.15°C",
)
T2 = temp_k
temp_c = T2 - 273.15
print(f"Inlet temperature: {temp_c:.2f} °C ({T2:.2f} K)")
PR = Compressor_Design_Pressure_Ratio
eta_c = Compressor_And_Turbine_Efficiency

# Determine temperature-dependent Cp and gamma. Prefer CoolProp if available.
try:
	from CoolProp.CoolProp import PropsSI

	def get_cp_gamma(T, P=101325, fluid='Air'):
		Cp = PropsSI('Cpmass', 'T', T, 'P', P, fluid)  # J/kg/K
		M = PropsSI('M', 'T', T, 'P', P, fluid)        # kg/mol
		R_univ = 8.314462618                            # J/mol/K
		R_spec = R_univ / M                             # J/kg/K
		gamma_local = Cp / (Cp - R_spec)
		return Cp, gamma_local

	cp, gamma = get_cp_gamma(T2)
	print(f"Using CoolProp: Cp={cp:.2f} J/kg/K, gamma={gamma:.5f}")
except Exception:
	gamma = 1.4
	cp = 1004.5
	print("CoolProp not available; using constants: Cp=1004.5 J/kg/K, gamma=1.4. Install with: pip install CoolProp")

# Two-stage military turbofan compressor model.
# This assumes a typical series compressor with no intercooler: stage 2 starts from the outlet
# temperature of stage 1 and continues to the final compressor discharge pressure.
PR1 = Compressor_Stage_1_Pressure_Ratio
PR2 = Compressor_Stage_2_Pressure_Ratio

T_stage1_out = T2 * (1 + (math.pow(PR1, (gamma - 1) / gamma) - 1) / eta_c)
T_stage2_out = T_stage1_out * (1 + (math.pow(PR2, (gamma - 1) / gamma) - 1) / eta_c)
T3 = T_stage2_out

print(f"Two-stage military turbofan compressor characteristics:")
print(f"  LPC pressure ratio: {PR1:.4f}")
print(f"  HPC pressure ratio: {PR2:.4f}")
print(f"  LPC outlet temperature: {T_stage1_out:.2f} K")
print(f"  HPC outlet temperature: {T_stage2_out:.2f} K")
print(f"  Compressor outlet temperature (T3): {T3:.2f} K")

# Total compressor work for a two-stage military turbofan compressor without intercooling
Compressor_Work = Usable_Core_Mass_Flow_Rate * cp * (T3 - T2)
print(f"Compressor work: {Compressor_Work:.2f} W")

# Combustion heat input (Q_in) calculation
# Calculate cp at average temperature between T3 and TET for better accuracy
T_avg_combustion = (T3 + TET) / 2
print(f"Default combustion temperature (average of T3 and TET): {T_avg_combustion:.2f} K")
T_combustion = _get_temp(
	"Combustion temperature (K or °C)",
	default=T_avg_combustion,
	default_unit='K',
	validator=lambda x: x > 0.0,
	err_msg="Temperature must be > 0 K"
)
try:
	cp_combustion, _ = get_cp_gamma(T_combustion)
	print(f"Combustion Cp at {T_combustion:.2f} K: {cp_combustion:.2f} J/kg/K")
except Exception:
	cp_combustion = cp
	print(f"Using T2-based Cp for combustion: {cp_combustion:.2f} J/kg/K")

# Calculate total heat energy required in combustor
# Q_in = mass flow rate × specific heat capacity × temperature rise
# This represents the thermal energy needed to heat air from compressor outlet (T3) to turbine inlet (TET)
Q_in = Usable_Core_Mass_Flow_Rate * cp_combustion * (TET - T3)
print(f"Combustion heat input (Q_in): {Q_in:.2f} W")

# Fuel consumption calculation
# Q_in is the heat energy added in the combustor to raise air from T3 to TET
# This heat comes from fuel combustion; LCV (Lower Calorific Value) is the energy released per kg of fuel
# Fuel mass flow rate = Total heat required / Energy per unit fuel mass
Least_Calorific_Value = _get_float(
	"Jet fuel Lower Calorific Value (J/kg, typically 43.15e6 for Jet A-1)",
	default=43.15e6,
	validator=lambda x: x > 0.0,
	err_msg="LCV must be > 0",
)

# Calculate fuel mass flow rate required to provide Q_in heat energy
# Then display in both kg/s and kg/h for practical reference
Weight_Fuel_Flow = Q_in / Least_Calorific_Value
print(f"Fuel mass flow rate: {Weight_Fuel_Flow:.6f} kg/s")
print(f"Fuel mass flow rate: {Weight_Fuel_Flow * 3600:.2f} kg/h")

print("\n" + "="*60)
print("  TURBINE PERFORMANCE")
print("="*60 + "\n")

# Turbine calculation method selection
print("  Select turbine calculation method:")
print("     1. Use turbine efficiency (calculate T4 from efficiency)")
print("     2. Assume turbine work equals compressor work\n")

turbine_method = _get_float(
	"Calculation method",
	default=1,
	validator=lambda x: x in (1, 2),
	err_msg="Please enter 1 or 2",
)

turbine_method = int(turbine_method)

# Get turbine efficiency input (needed for T4 calculation in both methods)
# Turbine efficiency represents how well the turbine converts thermal energy into mechanical work
# Typical values: 0.85-0.92 depending on turbine design and operating conditions
Turbine_Efficiency = _get_float(
	"Turbine efficiency (fraction, e.g. 0.90)",
	default=0.90,
	validator=lambda x: 0.0 < x <= 1.0,
	err_msg="Efficiency must be between 0 (exclusive) and 1 (inclusive)",
)

# Recalculate gamma at turbine entry temperature (TET) for hot section
try:
	_, gamma_hot = get_cp_gamma(TET)
except Exception:
	gamma_hot = gamma

# Adjust mass flow rate for turbine section: include fuel mass added in combustor.
# For a turbofan, the total incoming air is split into core flow and bypass flow.
# The usable core flow is the air remaining after bleed extraction.
Bypass_Mass_Flow_Rate = Core_Mass_Flow_Rate * Bypass_Ratio
Total_Mass_Flow_Turbine = Usable_Core_Mass_Flow_Rate + Weight_Fuel_Flow
print(f"Core air mass flow rate: {Core_Mass_Flow_Rate:.6f} kg/s")
print(f"Bleed air removed: {Core_Mass_Flow_Rate * Bleed_Fraction:.6f} kg/s")
print(f"Usable core air mass flow rate: {Usable_Core_Mass_Flow_Rate:.6f} kg/s")
print(f"Bypass air mass flow rate: {Bypass_Mass_Flow_Rate:.6f} kg/s")
print(f"Fuel mass flow rate: {Weight_Fuel_Flow:.6f} kg/s")
print(f"Total mass flow through turbine core: {Total_Mass_Flow_Turbine:.6f} kg/s\n")

# Calculate T4 with assumed temporary pressure ratio to determine implied pressure ratio
PR_turbine_temp = Compressor_Design_Pressure_Ratio

if turbine_method == 1:
	# Calculate isentropic exit temperature using hot section gamma
	T4_ideal_temp = TET / math.pow(PR_turbine_temp, (gamma_hot - 1) / gamma_hot)
	# Calculate actual turbine exit temperature using efficiency
	T4_temp = TET - (Turbine_Efficiency * (TET - T4_ideal_temp))
else:
	# Method 2: Calculate T4 from work balance with assumed PR
	try:
		cp_turbine_entry, _ = get_cp_gamma(TET)
	except Exception:
		cp_turbine_entry = cp
	# Initial estimate for T4
	T4_estimated = TET - (Compressor_Work / (Total_Mass_Flow_Turbine * cp_turbine_entry))
	# Refine with actual cp at the estimated exit temperature
	try:
		cp_turbine, _ = get_cp_gamma(T4_estimated)
		T4_temp = TET - (Compressor_Work / (Total_Mass_Flow_Turbine * cp_turbine))
	except Exception:
		T4_temp = T4_estimated

# Calculate implied pressure ratio from temperatures using isentropic relation
# PR = (T4 / TET)^(gamma/(gamma-1)) for isentropic process
# Since we have actual T4, calculate the implied pressure ratio
if T4_temp < TET:
	PR_turbine_implied = math.pow(TET / T4_temp, gamma_hot / (gamma_hot - 1))
else:
	PR_turbine_implied = Compressor_Design_Pressure_Ratio

PR_turbine = _get_float(
	"Turbine pressure ratio",
	default=PR_turbine_implied,
	validator=lambda x: x > 0.0,
	err_msg="Pressure ratio must be > 0",
)

if turbine_method == 1:
	# Calculate turbine exit temperature (T4)
	# For an ideal isentropic expansion, T4_ideal = TET / (PR^((gamma-1)/gamma))
	# Actual exit temperature accounts for turbine efficiency:
	# T4 = TET - eta_turbine × (TET - T4_ideal)

	# Calculate isentropic exit temperature using hot section gamma
	T4_ideal = TET / math.pow(PR_turbine, (gamma_hot - 1) / gamma_hot)

	# Calculate actual turbine exit temperature using efficiency
	T4 = TET - (Turbine_Efficiency * (TET - T4_ideal))

	# Get cp at turbine exit temperature for work calculation
	try:
		cp_turbine, _ = get_cp_gamma(T4)
	except Exception:
		cp_turbine = cp

	# Turbine work output (power extracted from hot gas)
	Turbine_Work = Total_Mass_Flow_Turbine * cp_turbine * (TET - T4)

	print(f"     ✓ Method selected: Turbine Efficiency Based\n")
	print(f"     Isentropic exit temperature (T4_ideal): {T4_ideal:.2f} K ({T4_ideal - 273.15:.2f} °C)")
	print(f"     ✓ Turbine exit temperature (T4): {T4:.2f} K ({T4 - 273.15:.2f} °C)\n")
	print(f"     Turbine efficiency (input): {Turbine_Efficiency * 100:.2f} %")
	print(f"     Turbine work output: {Turbine_Work:.2f} W")
	print(f"     Turbine work output: {Turbine_Work / 1000:.2f} kW\n")

else:
	# Method 2: Turbine work equals compressor work
	# In this simplified assumption, turbine work exactly matches compressor work
	print(f"     ✓ Method selected: Turbine Work = Compressor Work\n")

	Turbine_Work = Compressor_Work

	print(f"     ✓ Turbine work (equals compressor work): {Turbine_Work:.2f} W")
	print(f"     Turbine work: {Turbine_Work / 1000:.2f} kW\n")

	# Calculate turbine exit temperature (T4) from work balance
	# Turbine work constrains the actual exit temperature
	# T4_actual = TET - (Turbine_Work / (mass flow rate × cp))
	
	# Get cp at turbine entry temperature for initial T4_actual estimate
	try:
		cp_turbine_entry, _ = get_cp_gamma(TET)
	except Exception:
		cp_turbine_entry = cp
	# Initial estimate for T4_actual
	T4_actual_estimated = TET - (Turbine_Work / (Total_Mass_Flow_Turbine * cp_turbine_entry))

	
	# Refine with actual cp at the estimated exit temperature
	try:
		cp_turbine, _ = get_cp_gamma(T4_actual_estimated)
		T4 = TET - (Turbine_Work / (Total_Mass_Flow_Turbine * cp_turbine))
	except Exception:
		cp_turbine = cp
		T4 = T4_actual_estimated

	# Calculate T4_ideal by inverting efficiency: η = (TET - T4_actual) / (TET - T4_ideal)
	# Rearranging: T4_ideal = TET - (TET - T4_actual) / η
	T4_ideal = TET - ((TET - T4) / Turbine_Efficiency)

	print(f"     Isentropic exit temperature (T4_ideal): {T4_ideal:.2f} K ({T4_ideal - 273.15:.2f} °C)")
	print(f"     ✓ Turbine exit temperature (T4_actual): {T4:.2f} K ({T4 - 273.15:.2f} °C)")
	print(f"     Turbine efficiency (input): {Turbine_Efficiency * 100:.2f} %\n")

# Calculate turbine exit pressure (P4) using isentropic relation
# For isentropic expansion: T4_ideal / TET = (P4 / P3)^((gamma-1)/gamma)
# Rearranging: P4 = P3 × (T4_ideal / TET)^(gamma/(gamma-1))

P_inlet = 101325  # Sea level atmospheric pressure (Pa)
P3 = P_inlet * PR  # Compressor outlet pressure

# Note: gamma_hot was already calculated above for the hot section

print(f"     Hot section gamma at TET: {gamma_hot:.5f}\n")

# Calculate actual turbine exit pressure from isentropic relation
# P4 = P3 × (T4 / TET)^(gamma/(gamma-1))
P4 = P3 * math.pow(T4 / TET, gamma_hot / (gamma_hot - 1))

print(f"     Inlet pressure: {P_inlet / 1000:.2f} kPa")
print(f"     Compressor outlet pressure (P3): {P3 / 1000:.2f} kPa")
print(f"     Isentropic exit pressure: {P3 / PR_turbine / 1000:.2f} kPa")
print(f"     ✓ Turbine exit pressure (P4): {P4 / 1000:.2f} kPa")
print(f"     Pressure ratio across turbine: 1:{P3 / P4:.2f}\n")

# Net work output
Net_Work = Turbine_Work - Compressor_Work
print(f"     Net work output: {Net_Work:.2f} W")
print(f"     Net work output: {Net_Work / 1000:.2f} kW\n")


# Thermal efficiency of the cycle
if Q_in > 0:
	Thermal_Efficiency = (Net_Work / Q_in) * 100
	print(f"     ✓ Thermal efficiency: {Thermal_Efficiency:.2f} %\n")


print("\n" + "="*60)
print("  NOZZLE CALCULATION (CHOKED NOZZLE)")
print("="*60 + "\n")

# Nozzle inlet conditions (from turbine exit)
T0_nozzle = T4  # Stagnation temperature at nozzle inlet
P0_nozzle = P4  # Stagnation pressure at nozzle inlet

# Get cp and gamma at turbine exit temperature for nozzle calculations
try:
	cp_nozzle, gamma_nozzle = get_cp_gamma(T4)
except Exception:
	cp_nozzle = cp
	gamma_nozzle = gamma_hot

print(f"Nozzle inlet conditions:")
print(f"  Stagnation temperature (T0): {T0_nozzle:.2f} K ({T0_nozzle - 273.15:.2f} °C)")
print(f"  Stagnation pressure (P0): {P0_nozzle / 1000:.2f} kPa")
print(f"  Specific heat (cp): {cp_nozzle:.2f} J/kg/K")
print(f"  Gamma: {gamma_nozzle:.5f}\n")

# For a choked nozzle, flow reaches sonic conditions at the throat
# Critical temperature ratio: T*/T0 = 2/(gamma + 1)
# Critical pressure ratio: P*/P0 = (2/(gamma + 1))^(gamma/(gamma - 1))

T_critical = T0_nozzle * (2 / (gamma_nozzle + 1))
P_critical = P0_nozzle * math.pow(2 / (gamma_nozzle + 1), gamma_nozzle / (gamma_nozzle - 1))

print(f"Critical (sonic) conditions at throat:")
print(f"  Critical temperature (T*): {T_critical:.2f} K ({T_critical - 273.15:.2f} °C)")
print(f"  Critical pressure (P*): {P_critical / 1000:.2f} kPa")
print(f"  Temperature ratio (T*/T0): {T_critical / T0_nozzle:.5f}")
print(f"  Pressure ratio (P*/P0): {P_critical / P0_nozzle:.5f}\n")

# Speed of sound at critical temperature
# a* = sqrt(gamma * R_specific * T*)
R_gas = 287.05  # Specific gas constant for air (J/kg/K)
a_critical = math.sqrt(gamma_nozzle * R_gas * T_critical)

print(f"Speed of sound at critical conditions:")
print(f"  a* = {a_critical:.2f} m/s\n")

# Exit velocity for choked nozzle
# Using isentropic energy equation: V_exit = sqrt(2 * cp * (T0 - T_exit))
# For maximum thrust (fully expanded to ambient), assume isentropic expansion to atmospheric pressure
# Or calculate Mach 1 exit velocity: V_exit = sqrt(gamma * R * T*)

V_exit_sonic = a_critical

print(f"Exit velocity (choked nozzle):")
print(f"  Sonic exit velocity (V_exit = a*): {V_exit_sonic:.2f} m/s\n")

# Mass flow rate through the core nozzle and bypass stream.
# The core flow is the gas stream passing through the turbine and core nozzle.
# The bypass air is accelerated in the fan stream and contributes additional thrust.
mdot_core_nozzle = Total_Mass_Flow_Turbine
mdot_bypass_nozzle = Bypass_Mass_Flow_Rate
mdot_nozzle = mdot_core_nozzle + mdot_bypass_nozzle

print(f"Nozzle mass flow rate:")
print(f"  Core nozzle ṁ = {mdot_core_nozzle:.6f} kg/s")
print(f"  Bypass nozzle ṁ = {mdot_bypass_nozzle:.6f} kg/s")
print(f"  Total nozzle ṁ = {mdot_nozzle:.6f} kg/s\n")

# Calculate nozzle throat area from mass flow rate, velocity, and density
# Using continuity equation: A = mdot / (rho * V)
# Density at critical conditions: rho = P / (R_specific * T)

rho_critical = P_critical / (R_gas * T_critical)

# Nozzle throat area
A_throat = mdot_nozzle / (rho_critical * V_exit_sonic)

print(f"Nozzle throat area calculation:")
print(f"  Density at critical conditions: {rho_critical:.4f} kg/m³")
print(f"  Throat area (A*): {A_throat:.6f} m²")
print(f"  Throat diameter: {2 * math.sqrt(A_throat / 3.14159):.4f} m")

# Total thrust calculation for choked convergent nozzle
# For a choked nozzle, exit conditions occur at the throat (sonic conditions)
# Total thrust = Momentum thrust + Pressure thrust

# 1. Core momentum thrust: F_momentum = mdot_core × V_exit
F_momentum = mdot_core_nozzle * V_exit_sonic

# 2. Core pressure thrust: F_pressure = (P_exit - P_ambient) × A_exit
#    For choked convergent nozzle: P_exit = P_critical, A_exit = A_throat
P_ambient = P_inlet  # Sea level atmospheric pressure
F_pressure = (P_critical - P_ambient) * A_throat

# 3. Bypass stream thrust contribution for a turbofan engine
#    A simple first-order model assumes the bypass stream exits at similar velocity to the core nozzle.
#    This approximates the extra thrust due to the bypass flow without adding a separate fan nozzle model.
F_bypass = mdot_bypass_nozzle * V_exit_sonic

# The bypass flow should not include any bleed extracted from the core stream.
# This keeps the bypass thrust calculation consistent with the usable core mass flow model.

# 4. Total thrust
F_total_nozzle = F_momentum + F_pressure + F_bypass

# Summary
print("="*60)
print("  TURBOFAN THRUST SUMMARY")
print("="*60 + "\n")
print("Nozzle Configuration:")
print(f"  Type: Choked convergent nozzle")
print(f"  Exit Mach number: 1.0 (sonic)\n")
print("Exit Conditions:")
print(f"  Temperature: {T_critical:.2f} K ({T_critical - 273.15:.2f} °C)")
print(f"  Pressure: {P_critical / 1000:.2f} kPa")
print(f"  Velocity: {V_exit_sonic:.2f} m/s")
print(f"  Throat area: {A_throat:.6f} m²")
print(f"  Throat diameter: {2 * math.sqrt(A_throat / 3.14159) * 1000:.2f} mm\n")
print("Thrust Breakdown:")
print(f"  Core Momentum thrust: {F_momentum:.2f} N ({F_momentum / 1000:.3f} kN)")
print(f"  Bypass thrust:    {F_bypass:.2f} N ({F_bypass / 1000:.3f} kN)")
print(f"  Pressure thrust (Choked Convergent Nozzle):  {F_pressure:.2f} N ({F_pressure / 1000:.3f} kN)")
print(f"  ─────────────────────────────────────")
print(f"  Total gross nozzle thrust: {F_total_nozzle:.2f} N ({F_total_nozzle / 1000:.3f} kN)\n")

