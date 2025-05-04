import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from skyfield.api import load, EarthSatellite
from datetime import datetime

# Streamlit config
st.set_page_config(layout="wide")
st.title("🌍 Live Satellite Tracker")
st.markdown("Tracking **Kosmos 482** Satellite")

# Input location
col1, col2 = st.columns(2)
with col1:
    my_lat = st.number_input("Your Latitude", value=16.8409)
with col2:
    my_lon = st.number_input("Your Longitude", value=96.1735)

# Kosmos 482 TLE data (hardcoded)
name_kosmos = "Kosmos 482"
tle1_kosmos = "1 06073U 72023B   24123.65777316  .00000803  00000+0  14121-3 0  9990"
tle2_kosmos = "2 06073  51.5533 146.5134 5188798  22.7442 354.1140  5.44340810267680"

# Load time and satellite
ts = load.timescale()

# Initialize crash_time variable
crash_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Try to load satellite, and handle when TLE data is invalid
try:
    sat_kosmos = EarthSatellite(tle1_kosmos, tle2_kosmos, name_kosmos, ts)
    satellite_data_valid = True
except Exception as e:
    satellite_data_valid = False
    error_message = "The Satellite has crashed and the TLE data is no longer available."
    crash_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Get current and path data
def get_satellite_data(satellite, ts):
    time_now = ts.now()
    geocentric = satellite.at(time_now)
    subpoint = geocentric.subpoint()
    lat = subpoint.latitude.degrees
    lon = subpoint.longitude.degrees
    alt = subpoint.elevation.km
    velocity = geocentric.velocity.km_per_s
    speed = np.linalg.norm(velocity)

    times = ts.utc(time_now.utc_datetime().year,
                   time_now.utc_datetime().month,
                   time_now.utc_datetime().day,
                   np.linspace(0, 24, 100))
    positions = [satellite.at(t).subpoint() for t in times]
    lats = [pos.latitude.degrees for pos in positions]
    lons = [pos.longitude.degrees for pos in positions]

    return lat, lon, alt, speed, lats, lons

# Plotting
fig, ax = plt.subplots(figsize=(12, 6))
m = Basemap(projection='cyl', resolution='c')
m.drawcoastlines()
m.drawcountries()
m.drawmapboundary(fill_color='midnightblue')
m.fillcontinents(color='forestgreen', lake_color='darkgreen')
m.drawparallels(np.arange(-90., 91., 30.))
m.drawmeridians(np.arange(-180., 181., 60.))

# Plot your location
x_my, y_my = m(my_lon, my_lat)
ax.scatter(x_my, y_my, color='white', marker='^', s=100, label="Your Location")

if satellite_data_valid:
    # Plot Kosmos 482 path and position
    lat, lon, alt, speed, path_lats, path_lons = get_satellite_data(sat_kosmos, ts)
    path_x, path_y = m(path_lons, path_lats)
    ax.plot(path_x, path_y, linestyle='--', color='lime')
    x, y = m(lon, lat)
    ax.scatter(x, y, color='lime', edgecolor='black', s=100, zorder=5, label=sat_kosmos.name)

    # Info
    st.markdown(f"**{sat_kosmos.name}** — Lat: `{lat:.2f}°`, Lon: `{lon:.2f}°`, Alt: `{alt:.1f} km`, Speed: `{speed:.2f} km/s`")
else:
    # Display crash message with time
    ax.text(0.5, 0.5, f"The Satellite has crashed\nAt: {crash_time}", color='red', fontsize=20, ha='center', va='center', transform=ax.transAxes)

ax.legend(loc='lower left', fontsize=9)
st.pyplot(fig)

# Reload button
if st.button("🔁 Reload Satellite Data"):
    st.rerun()

st.markdown("Design by Mr Zay Bhone Aung")
