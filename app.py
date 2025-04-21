import streamlit as st
import numpy as np

def get_dead_time(voltage):
    voltages = [10.0, 11.0, 12.0, 13.0, 14.0, 15.0]
    dead_times = [1.6, 1.3, 1.0, 0.8, 0.6, 0.5]  # ms
    return float(np.interp(voltage, voltages, dead_times))

def fuel_injector_calculator():
    st.title("💉 Fuel Injector Calculator")

    fuel_type = st.selectbox("Fuel Type", ['e85', '95 Octane', '98 Octane', 'Methanol'])

    if fuel_type == '95 Octane':
        st.caption("Stoichiometric AFR: 14.7 | Fuel density: 0.74 g/cc")
    elif fuel_type == '98 Octane':
        st.caption("Stoichiometric AFR: 14.6 | Fuel density: 0.74 g/cc")
    elif fuel_type == 'Methanol':
        st.caption("Stoichiometric AFR: 6.4 | Fuel density: 0.791 g/cc")
    else:  # e85
        st.caption("Stoichiometric AFR: 9.77 | Fuel density: 0.79 g/cc")

    engine_type = st.selectbox("Engine Type", ["Naturally Aspirated", "Turbocharged"])

    cylinders = st.number_input("Number of Cylinders", min_value=1, max_value=16, value=4, step=1)

    # Text fields for displacement and injector size
    displacement_input = st.text_input("Engine Displacement (cc)", value="2000")
    injector_input = st.text_input("Injector Size (cc/min)", value="1300")

    try:
        displacement_cc = int(displacement_input)
        injector_cc = int(injector_input)
    except ValueError:
        st.error("Please enter valid numbers for displacement and injector size.")
        return

    rpm = st.slider("Engine RPM", 500, 10000, 6000, step=100)
    ve_percent = st.slider("Volumetric Efficiency (%)", 50, 120, 91)
    map_kpa = st.slider("Manifold Air Pressure (kPa)", 80, 400, 300)
    lambda_target = st.slider("Target Lambda", 0.6, 1.2, 0.8)
    iat_c = st.slider("Intake Air Temp (°C)", -20, 80, 20)
    voltage = st.slider("Battery Voltage (V)", 10.0, 15.0, 13.8, step=0.1)

    molar_mass_air = 28.97
    R = 8.314

    if fuel_type == '95 Octane':
        afr_stoich = 14.7
        fuel_density = 0.74
        fuel_energy = 19000
    elif fuel_type == '98 Octane':
        afr_stoich = 14.6
        fuel_density = 0.74
        fuel_energy = 19000
    elif fuel_type == 'Methanol':
        afr_stoich = 6.4
        fuel_density = 0.791
        fuel_energy = 9500
    else:  # e85
        afr_stoich = 9.765
        fuel_density = 0.79
        fuel_energy = 12500

    bsfc = 0.45 if engine_type == "Naturally Aspirated" else 0.55

    target_afr = afr_stoich * lambda_target
    ve_decimal = ve_percent / 100.0
    engine_cycle_per_min = rpm / 2
    air_volume_lpm = (displacement_cc / 1000) * engine_cycle_per_min * ve_decimal

    temp_K = iat_c + 273.15
    map_pa = map_kpa * 1000
    air_density = (map_pa * molar_mass_air) / (R * temp_K) / 1000

    air_mass_gpm = air_volume_lpm * air_density
    fuel_mass_gpm = air_mass_gpm / target_afr

    fuel_mass_per_cyl = fuel_mass_gpm / engine_cycle_per_min / cylinders
    fuel_volume_per_cyl_cc = fuel_mass_per_cyl / fuel_density
    injector_cc_per_ms = injector_cc / 60000
    base_pw_ms = fuel_volume_per_cyl_cc / injector_cc_per_ms

    dead_time_ms = get_dead_time(voltage)
    actual_pw_ms = base_pw_ms + dead_time_ms

    time_per_cycle_ms = 120000 / rpm
    duty_cycle = (actual_pw_ms / time_per_cycle_ms) * 100

    st.subheader("📊 Results")
    st.write(f"**Target AFR:** {target_afr:.2f}")
    st.write(f"**Base Pulse Width:** {base_pw_ms:.2f} ms")
    st.write(f"**Dead Time:** {dead_time_ms:.2f} ms (at {voltage:.1f} V)")
    st.write(f"**Actual Pulse Width:** {actual_pw_ms:.2f} ms")
    st.write(f"**Injector Duty Cycle:** {duty_cycle:.2f} %")

    st.subheader("⛽ Fuel Flow Breakdown")
    fuel_volume_gpm = fuel_mass_gpm / fuel_density
    fuel_volume_per_injector = fuel_volume_gpm / cylinders
    st.write(f"**Total Fuel Volume:** {fuel_volume_gpm:.2f} cc/min")
    st.write(f"**Fuel Volume per Injector:** {fuel_volume_per_injector:.2f} cc/min")

    st.subheader("🏎️ Power Estimation")
    fuel_mass_lph = (fuel_mass_gpm / 453.592) * 60
    hp_theoretical = (fuel_mass_lph * fuel_energy * 0.25) / 2545
    hp_bsfc = fuel_mass_lph / bsfc
    st.write(f"**Theoretical HP (25% Efficiency):** {hp_theoretical:.0f} hp")
    st.write(f"**Estimated Engine HP (Based on BSFC ~{bsfc}):** {hp_bsfc:.0f} hp")

if __name__ == "__main__":
    fuel_injector_calculator()
