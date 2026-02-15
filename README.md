POCKET TECHNICIAN Smart Shrimp Farm Decision Support System

------------------------------------------------------------------------

Pocket Technician is a Streamlit-based shrimp farm management and
analytics application designed to support technicians and farm managers
with scientifically driven decision-making tools.

The system integrates sampling analytics, feed management logic,
survival estimation, water quality monitoring, profitability analysis,
and reporting features into a single mobile-friendly interface.

  ---------------
  CORE FEATURES
  ---------------

1.  Sampling & Growth Analytics

-   Average Body Weight (ABW) calculation: ABW = 1000 / count
-   Feed-based survival estimation
-   Biomass calculation (current & expected)
-   DOC (Day of Culture) tracking (stocking day = DOC 1)
-   Weekly metrics from second sampling onward: • Weekly Growth •
    Average Daily Growth (ADG) • Weekly Biomass Gain • Weekly Survival
    Change • Weekly FCR
-   Growth curve visualization
-   Mortality curve visualization

------------------------------------------------------------------------

2.  Feed Tray Management

-   Feed adjustment logic based on: • Body weight category • Feed left
    on check tray • Consumption time
-   Automatic increase / reduction recommendations
-   Weekly feed efficiency trend (FCR graph)

------------------------------------------------------------------------

3.  IoT Water Quality Integration Supports:

-   Manual water quality entry
-   API-based IoT sensor integration

Parameters monitored: - Temperature - Dissolved Oxygen (DO) - pH -
Ammonia - Nitrite

Includes automatic risk alerts based on safe biological thresholds.

------------------------------------------------------------------------

4.  Profit & Carrying Capacity Analysis

-   Pond volume calculation (Area × Depth)
-   Biomass per m³ calculation
-   Carrying capacity warning system
-   Weekly FCR-based economic analysis
-   Profit estimation
-   Profit per m³ calculation

------------------------------------------------------------------------

5.  Reporting & Export

-   Advanced Technician PDF Report including: • Sampling summary table •
    Weekly metrics table • Growth curve • Mortality curve • Feed
    efficiency graph • Economic summary • Carrying capacity analysis
-   Pond-wise Excel export for sampling records

------------------------------------------------------------------------

TECHNOLOGY STACK

-   Python
-   Streamlit
-   Pandas
-   Matplotlib
-   ReportLab
-   OpenPyXL
-   Requests
-   JSON-based local storage

------------------------------------------------------------------------

INSTALLATION

1.  Install Python (3.9+ recommended)

2.  Install required packages:

pip install streamlit pandas matplotlib reportlab openpyxl requests

3.  Run the application:

streamlit run app.py

------------------------------------------------------------------------

BIOLOGICAL MODEL USED

-   ABW derived from count per kg
-   Survival estimated using feed-based reference chart
-   Biomass calculated from survival × ABW
-   Weekly FCR derived from feed usage and biomass gain
-   Carrying capacity based on biomass per cubic meter

------------------------------------------------------------------------

TARGET USERS

-   Shrimp farm technicians
-   Aquaculture farm managers
-   Aquaculture consultants
-   Smart farm operators
-   IoT-integrated aquaculture systems

------------------------------------------------------------------------

DISCLAIMER

This application provides decision-support insights based on modeled
aquaculture principles. Final farm decisions should always consider
real-time environmental and biological conditions.

------------------------------------------------------------------------

VISION

Pocket Technician bridges:

Biology × Feed Management × Economics × Water Quality × IoT

Creating a practical, technician-grade aquaculture intelligence system
for modern shrimp farming.

------------------------------------------------------------------------
