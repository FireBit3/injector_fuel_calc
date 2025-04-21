import streamlit as st

def fuel_injector_calculator():
    st.title("💉 Fuel Injector Calculator")

    fuel_type = st.selectbox("Fuel Type", ['e85', '95'])
    displacement_cc = st.slider("Engine Displacement (cc)", 500, 8000, 2000, step=100)
    injector_cc = st.slider("Injector Size (cc/min)", 100, 3000, 1300, step=50)
    rpm = st.slider("Engine RPM", 500, 10000, 6000, step=100)
    ve_percent = st.slider("Volumetric Efficiency (%)", 50, 120, 91)
    map_kpa = st.slider("Manifold Air Pressure (kPa)", 80, 400, 300)
    lambda_target = st.slider("Target Lambda", 0.6, 1.2, 0.8)
    iat_c = st.slider("Intake Air Temp (°C)", -20, 80, 20)

    cylinders = 4
    molar_mass_air = 28.97
    R = 8.314
    afr_stoich = 14.7 if fuel_type == '95' else 9.765
    target_afr = afr_stoich * lambda_target
    ve_decimal = ve_percent / 100.0

    engine_cycle_per_min = rpm / 2
    air_volume_lpm = (displacement_cc / 1000) * engine_cycle_per_min * ve_decimal

    temp_K = iat_c + 273.15
    map_pa = map_kpa * 1000
    air_density = (map_pa * molar_mass_air) / (R * temp_K) / 1000

    air_mass_gpm = air_volume_lpm * air_density
    fuel_mass_gpm = air_mass_gpm / target_afr
    fuel_density = 0.74 if fuel_type == '95' else 0.79

    fuel_mass_per_cyl = fuel_mass_gpm / engine_cycle_per_min / cylinders
    fuel_volume_per_cyl_cc = fuel_mass_per_cyl / fuel_density
    injector_cc_per_ms = injector_cc / 60000
    base_pw_ms = fuel_volume_per_cyl_cc / injector_cc_per_ms
    time_per_cycle_ms = 120000 / rpm
    duty_cycle = (base_pw_ms / time_per_cycle_ms) * 100

    st.subheader("📊 Results")
    st.write(f"**Target AFR:** {target_afr:.2f}")
    st.write(f"**Base Pulse Width:** {base_pw_ms:.2f} ms")
    st.write(f"**Injector Duty Cycle:** {duty_cycle:.2f} %")

if __name__ == "__main__":
    fuel_injector_calculator()