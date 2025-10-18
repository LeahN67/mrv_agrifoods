# greenscope_mrv_clic.py
# GreenScope MRV – Bridging Climate Finance Gap for Sub-Saharan African Agrifood
# Built for CLIC Lab Application
# Run with: streamlit run greenscope_mrv_clic.py

import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
import plotly.graph_objects as go
import plotly.express as px

# ==============================
# 1. SIMULATED DATA GENERATION
# ==============================

def create_simulated_data():
    """Generate realistic farm data for Sub-Saharan African context"""
    farms = pd.DataFrame({
        "farm_id": ["KM001", "KM002", "KM003", "KM004", "KM005"],
        "farm_name": ["Mwangi Family Farm", "Green Acres Cooperative", "Njoroge Smallholder", 
                      "Wanjiku Women's Group", "Kamau Agroforestry"],
        "lat": [-1.123, -0.987, -1.345, -1.456, -0.789],
        "lng": [36.456, 35.889, 36.789, 36.234, 36.012],
        "area_ha": [1.8, 3.2, 0.9, 2.1, 4.5],
        "crop_type": ["Maize", "Mixed legumes", "Sorghum", "Vegetables", "Coffee"],
        "practice": ["Cover cropping", "Agroforestry", "Reduced tillage", 
                     "Composting", "Shade-grown coffee"],
        "intervention_date": [datetime(2025, 2, 1), datetime(2025, 1, 15), 
                            datetime(2025, 3, 10), datetime(2025, 2, 20), 
                            datetime(2025, 1, 5)],
        "baseline_start": [datetime(2024, 2, 1), datetime(2024, 1, 15), 
                          datetime(2024, 3, 10), datetime(2024, 2, 20), 
                          datetime(2024, 1, 5)],
        "baseline_end": [datetime(2025, 1, 31), datetime(2025, 1, 14), 
                        datetime(2025, 3, 9), datetime(2025, 2, 19), 
                        datetime(2025, 1, 4)],
        "farmer_type": ["Smallholder", "Cooperative", "Smallholder", 
                       "Women-led", "Medium-scale"],
        "carbon_potential_tCO2": [4.2, 8.5, 2.1, 5.3, 12.4]
    })

    # Generate time-series indicators
    indicators = []
    end_date = datetime(2025, 10, 18)
    for _, farm in farms.iterrows():
        current = farm["baseline_start"]
        ndvi_base = 0.38 + (hash(farm["farm_id"]) % 10) * 0.01
        soil_base = 0.17 + (hash(farm["farm_id"]) % 10) * 0.005
        
        while current <= end_date:
            weeks_post = max(0, (current - farm["intervention_date"]).days // 7)
            # Progressive improvement post-intervention
            ndvi = min(0.70, round(ndvi_base + 0.0035 * weeks_post, 3))
            soil = min(0.28, round(soil_base + 0.0018 * weeks_post, 3))
            rain_anom = -18 if current < farm["intervention_date"] else 8
            
            # Add some realistic variation
            import random
            random.seed(int((current - datetime(2024, 1, 1)).days + hash(farm["farm_id"])))
            ndvi += random.uniform(-0.02, 0.02)
            soil += random.uniform(-0.01, 0.01)
            rain_anom += random.uniform(-5, 5)
            
            indicators.append({
                "farm_id": farm["farm_id"],
                "date": current,
                "ndvi": round(max(0.2, min(0.75, ndvi)), 3),
                "soil_moisture": round(max(0.10, min(0.30, soil)), 3),
                "rainfall_anomaly_pct": round(rain_anom, 1)
            })
            current += timedelta(weeks=1)

    indicators_df = pd.DataFrame(indicators)

    # Ground truth validation
    validation = pd.DataFrame({
        "farm_id": ["KM001", "KM002", "KM003", "KM004", "KM005"],
        "submission_date": [datetime(2025, 4, 3), datetime(2025, 3, 20), 
                          datetime(2025, 5, 12), datetime(2025, 4, 15), 
                          datetime(2025, 3, 8)],
        "practice_confirmed": ["Cover cropping", "Agroforestry", "Reduced tillage",
                              "Composting & mulching", "Shade-grown coffee"],
        "notes": [
            "Planted beans and vetch as cover after maize harvest. Soil health improving.",
            "Planted 50 Grevillea robusta trees along field edges. Enhanced biodiversity.",
            "Switched to ox-plow only once; no deep tillage. Reduced fuel costs.",
            "Weekly composting using crop residues and manure. Healthier vegetables.",
            "Maintained tree canopy cover. Birds returning, better coffee quality."
        ],
        "verification_method": ["Field visit + photos", "Field visit + GPS", 
                               "Farmer interview", "Field visit + photos",
                               "Field visit + canopy analysis"]
    })
    
    # Finance-ready metrics
    carbon_credits = pd.DataFrame({
        "farm_id": ["KM001", "KM002", "KM003", "KM004", "KM005"],
        "estimated_tCO2_yr": [4.2, 8.5, 2.1, 5.3, 12.4],
        "credit_price_usd": [15, 15, 15, 15, 15],
        "annual_revenue_usd": [63, 127.5, 31.5, 79.5, 186],
        "verification_cost_usd": [120, 180, 90, 150, 240],
        "net_benefit_5yr_usd": [195, 457.5, 67.5, 247.5, 690]
    })

    return farms, indicators_df, validation, carbon_credits

# ==============================
# 2. ENHANCED PDF REPORT
# ==============================

class CLICMRVReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        # CLIC-aligned header
        self.set_fill_color(34, 139, 34)
        self.rect(0, 0, 210, 40, 'F')
        
        self.set_xy(10, 8)
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "GreenScope MRV", 0, 1, "L")
        
        self.set_font("Helvetica", "", 11)
        self.set_xy(10, 20)
        self.cell(0, 8, "Bridging Climate Finance for Sub-Saharan African Agrifood Systems", 0, 1, "L")
        
        self.set_font("Helvetica", "I", 9)
        self.set_xy(10, 28)
        self.cell(0, 6, "CLIC Lab Innovation | Measurement, Reporting & Verification", 0, 1, "L")
        
        self.ln(18)

    def footer(self):
        self.set_y(-20)
        self.set_draw_color(34, 139, 34)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        
        self.ln(3)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, "SIMULATED DATA - MVP DEMONSTRATION", 0, 0, "C")
        self.ln(4)
        self.set_font("Helvetica", "", 8)
        self.cell(0, 5, "greenscope.mrv | Built for CLIC Lab", 0, 0, "C")

    def add_project_header(self, farm, carbon_data):
        # Enhanced project header with carbon potential
        self.set_fill_color(240, 255, 240)
        self.set_draw_color(34, 139, 34)
        self.rect(10, self.get_y(), 190, 42, 'DF')
        
        y_start = self.get_y()
        self.set_xy(15, y_start + 3)
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(34, 139, 34)
        self.cell(0, 7, f"{farm['farm_name']}", 0, 1)
        
        self.set_xy(15, self.get_y())
        self.set_font("Helvetica", "", 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 5, f"Project ID: {farm['farm_id']} | Type: {farm['farmer_type']} | Practice: {farm['practice']}", 0, 1)
        
        self.set_xy(15, self.get_y())
        self.cell(0, 5, f"Location: {farm['lat']:.3f}, {farm['lng']:.3f} | Area: {farm['area_ha']} ha | Crop: {farm['crop_type']}", 0, 1)
        
        self.set_xy(15, self.get_y())
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(255, 140, 0)
        self.cell(0, 5, f"Carbon Sequestration Potential: {carbon_data['estimated_tCO2_yr']:.1f} tCO2e/year", 0, 1)
        
        self.set_xy(15, self.get_y())
        self.set_text_color(100, 100, 100)
        self.set_font("Helvetica", "I", 9)
        self.cell(0, 5, f"Baseline: {farm['baseline_start'].strftime('%b %Y')} - {farm['baseline_end'].strftime('%b %Y')} | Reporting: Apr 2025 - Oct 2025", 0, 1)
        
        self.ln(45)

    def add_section_title(self, title, icon=""):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(34, 139, 34)
        self.cell(0, 8, f"{icon} {title}", 0, 1)
        self.set_line_width(0.3)
        self.set_draw_color(34, 139, 34)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def add_metric_box(self, title, baseline, current, unit, x_pos):
        box_width = 58
        box_height = 32
        
        self.set_fill_color(245, 255, 245)
        self.rect(x_pos, self.get_y(), box_width, box_height, 'DF')
        
        self.set_xy(x_pos + 2, self.get_y() + 2)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(80, 80, 80)
        self.cell(box_width - 4, 5, title, 0, 0, "C")
        
        if baseline > 0:
            change_pct = ((current - baseline) / baseline) * 100
            arrow = "+" if change_pct > 0 else ""
        else:
            change_pct = 0
            arrow = ""
        
        self.set_xy(x_pos + 2, self.get_y() + 7)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(box_width - 4, 4, f"Baseline: {baseline:.2f} {unit}", 0, 0, "C")
        
        self.set_xy(x_pos + 2, self.get_y() + 5)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(34, 139, 34)
        self.cell(box_width - 4, 5, f"{current:.2f} {unit}", 0, 0, "C")
        
        self.set_xy(x_pos + 2, self.get_y() + 6)
        self.set_font("Helvetica", "B", 9)
        color = (34, 139, 34) if change_pct >= 0 else (220, 20, 60)
        self.set_text_color(*color)
        self.cell(box_width - 4, 4, f"{arrow}{change_pct:.0f}%", 0, 0, "C")

    def add_finance_section(self, carbon_data):
        self.add_section_title("Climate Finance Potential", "")
        
        # Finance box
        self.set_fill_color(255, 250, 235)
        self.set_draw_color(255, 140, 0)
        self.rect(10, self.get_y(), 190, 48, 'DF')
        
        y_fin = self.get_y()
        self.set_xy(15, y_fin + 3)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(0, 0, 0)
        self.cell(0, 5, "Carbon Credit Revenue Projection", 0, 1)
        
        self.set_xy(15, self.get_y())
        self.set_font("Helvetica", "", 10)
        self.cell(0, 5, f"Annual Carbon Sequestration: {carbon_data['estimated_tCO2_yr']:.1f} tCO2e", 0, 1)
        
        self.set_xy(15, self.get_y())
        self.cell(0, 5, f"Carbon Credit Price: ${carbon_data['credit_price_usd']:.0f}/tCO2e", 0, 1)
        
        self.set_xy(15, self.get_y())
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(34, 139, 34)
        self.cell(0, 5, f"Annual Revenue: ${carbon_data['annual_revenue_usd']:.2f}", 0, 1)
        
        self.set_xy(15, self.get_y())
        self.set_font("Helvetica", "", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, f"Verification Cost: ${carbon_data['verification_cost_usd']:.0f} | 5-Year Net Benefit: ${carbon_data['net_benefit_5yr_usd']:.2f}", 0, 1)
        
        self.set_xy(15, self.get_y())
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 5, "Note: Prices based on voluntary carbon market averages. Aggregation reduces per-farm costs.", 0, 1)
        
        self.ln(50)

def generate_clic_report(farm, indicators, validation_row, carbon_data):
    pdf = CLICMRVReport()
    pdf.add_page()
    
    pdf.add_project_header(farm, carbon_data)
    
    # Calculate metrics
    baseline_data = indicators[indicators["date"] <= farm["baseline_end"]]
    current_data = indicators[indicators["date"] > farm["baseline_end"]]
    
    ndvi_b = baseline_data["ndvi"].mean()
    ndvi_c = current_data["ndvi"].mean()
    soil_b = baseline_data["soil_moisture"].mean()
    soil_c = current_data["soil_moisture"].mean()
    rain_b = baseline_data["rainfall_anomaly_pct"].mean()
    rain_c = current_data["rainfall_anomaly_pct"].mean()
    
    # Impact indicators
    pdf.add_section_title("Climate Impact Indicators", "")
    
    y_pos = pdf.get_y()
    pdf.add_metric_box("NDVI (Biomass)", ndvi_b, ndvi_c, "", 10)
    pdf.set_y(y_pos)
    pdf.add_metric_box("Soil Moisture", soil_b, soil_c, "cm3/cm3", 72)
    pdf.set_y(y_pos)
    
    # Rainfall box
    rain_delta = rain_c - rain_b
    pdf.set_fill_color(245, 255, 245)
    pdf.rect(134, y_pos, 58, 32, 'DF')
    pdf.set_xy(136, y_pos + 2)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(54, 5, "Rainfall Anomaly", 0, 0, "C")
    pdf.set_xy(136, y_pos + 9)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(54, 4, f"Baseline: {rain_b:.0f}%", 0, 0, "C")
    pdf.set_xy(136, y_pos + 14)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(34, 139, 34)
    pdf.cell(54, 5, f"{rain_c:.0f}%", 0, 0, "C")
    pdf.set_xy(136, y_pos + 20)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(34, 139, 34)
    pdf.cell(54, 4, f"{rain_delta:+.0f}% change", 0, 0, "C")
    
    pdf.set_y(y_pos + 38)
    
    # Finance section
    pdf.add_finance_section(carbon_data)
    
    # Validation
    pdf.add_section_title("Ground Truth Validation", "")
    
    pdf.set_fill_color(255, 250, 240)
    pdf.set_draw_color(255, 165, 0)
    pdf.rect(10, pdf.get_y(), 190, 32, 'DF')
    
    y_val = pdf.get_y()
    pdf.set_xy(15, y_val + 3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 5, f"Practice Confirmed: {validation_row['practice_confirmed']}", 0, 1)
    
    pdf.set_xy(15, pdf.get_y())
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Verification: {validation_row['verification_method']} | Date: {validation_row['submission_date'].strftime('%B %d, %Y')}", 0, 1)
    
    pdf.set_xy(15, pdf.get_y())
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(180, 4, f'Farmer Notes: "{validation_row["notes"]}"')
    
    pdf.ln(34)
    
    # Methodology
    pdf.add_section_title("Methodology & Data Sources", "")
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 5, "Remote Sensing Data (AI-Estimated):", 0, 1)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(10, 5, "", 0, 0)
    pdf.cell(0, 5, "- Vegetation: Sentinel-2 NDVI time series (10m resolution)", 0, 1)
    pdf.cell(10, 5, "", 0, 0)
    pdf.cell(0, 5, "- Rainfall: CHIRPS (Climate Hazards Group, 0.05deg resolution)", 0, 1)
    pdf.cell(10, 5, "", 0, 0)
    pdf.cell(0, 5, "- Soil Moisture: ERA5-Land reanalysis (9km resolution)", 0, 1)
    
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 5, "Validation Approach:", 0, 1)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 5, "Hybrid MRV combining satellite imagery with farmer-reported ground truth. Baseline: 12-month pre-intervention average. Carbon estimates based on IPCC Tier 2 methods for cropland management.")
    
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(34, 139, 34)
    pdf.cell(0, 5, "Confidence: High (AI + Field-Validated)", 0, 1)
    
    return pdf

# ==============================
# 3. STREAMLIT APPLICATION
# ==============================

def main():
    st.set_page_config(page_title="GreenScope MRV - CLIC Lab", layout="wide", page_icon="🌿")
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #228B22 0%, #32CD32 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #f0fff0;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #228B22;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌿 GreenScope MRV</h1>
        <p>Bridging the Climate Finance Gap for Sub-Saharan African Agrifood Systems</p>
        <small>Built for CLIC Lab | Transparent MRV for Smallholder Farmers</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    farms_df, indicators_df, validation_df, carbon_df = create_simulated_data()
    
    # Sidebar
    st.sidebar.header("🎯 CLIC Lab Innovation")
    st.sidebar.markdown("""
    **Challenge**: Only 4.3% of climate finance reaches agrifood, yet the sector accounts for 
    ~33% of GHG emissions.
    
    **Solution**: Low-cost, scalable MRV combining:
    - 🛰️ Satellite remote sensing
    - 📱 Farmer validation (mobile-first)
    - 💰 Carbon credit aggregation
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Select Farm Project")
    selected_id = st.sidebar.selectbox(
        "Choose a farm to view details:",
        farms_df["farm_id"],
        format_func=lambda x: f"{farms_df[farms_df['farm_id']==x]['farm_name'].values[0]} ({x})"
    )
    
    # Get farm data
    farm = farms_df[farms_df["farm_id"] == selected_id].iloc[0]
    indicators = indicators_df[indicators_df["farm_id"] == selected_id].copy()
    validation = validation_df[validation_df["farm_id"] == selected_id].iloc[0]
    carbon = carbon_df[carbon_df["farm_id"] == selected_id].iloc[0]
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Portfolio Analytics",
        "👨‍🌾 Farmer Dashboard", 
        "💼 Investor View", 
        "🌍 Climate Impact"
    ])
    
    with tab1:
        st.header("📊 Portfolio-Level Analytics")
        st.markdown("### Aggregated Impact Across All Projects")
        
        # Portfolio metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_farms = len(farms_df)
        total_area = farms_df['area_ha'].sum()
        total_carbon = carbon_df['estimated_tCO2_yr'].sum()
        total_revenue = carbon_df['annual_revenue_usd'].sum()
        
        col1.metric("Total Projects", total_farms, "Active farms")
        col2.metric("Total Area", f"{total_area:.1f} ha", "Under management")
        col3.metric("Carbon Potential", f"{total_carbon:.1f} tCO2e/yr", "Annual sequestration")
        col4.metric("Revenue Potential", f"${total_revenue:.0f}/yr", "Carbon credits")
        
        # Portfolio map
        st.subheader("🗺️ Geographic Distribution")
        portfolio_map = folium.Map(location=[-1.2, 36.0], zoom_start=9)
        
        for _, farm_row in farms_df.iterrows():
            carbon_val = carbon_df[carbon_df['farm_id'] == farm_row['farm_id']]['estimated_tCO2_yr'].values[0]
            folium.CircleMarker(
                location=[farm_row['lat'], farm_row['lng']],
                radius=farm_row['area_ha'] * 3,
                popup=f"<b>{farm_row['farm_name']}</b><br>{farm_row['practice']}<br>{carbon_val:.1f} tCO2e/yr",
                color='green',
                fill=True,
                fillColor='lightgreen',
                fillOpacity=0.6
            ).add_to(portfolio_map)
        
        st_folium(portfolio_map, width=900, height=400)
        
        # Practice distribution
        st.subheader("🌾 Climate-Smart Practices")
        
        col1, col2 = st.columns(2)
        
        with col1:
            practice_counts = farms_df['practice'].value_counts()
            fig_practice = px.pie(values=practice_counts.values, names=practice_counts.index,
                                 title="Distribution of Practices",
                                 color_discrete_sequence=px.colors.sequential.Greens)
            st.plotly_chart(fig_practice, use_container_width=True)
        
        with col2:
            farmer_types = farms_df['farmer_type'].value_counts()
            fig_types = px.bar(x=farmer_types.index, y=farmer_types.values,
                              title="Farmer Types",
                              labels={'x': 'Type', 'y': 'Count'},
                              color=farmer_types.values,
                              color_continuous_scale='Greens')
            st.plotly_chart(fig_types, use_container_width=True)
        
        # Carbon comparison
        st.subheader("💚 Carbon Sequestration by Project")
        carbon_comparison = farms_df.merge(carbon_df[['farm_id', 'estimated_tCO2_yr', 'annual_revenue_usd']], 
                                          on='farm_id')
        
        fig_carbon = px.bar(carbon_comparison, 
                           x='farm_name', 
                           y='estimated_tCO2_yr',
                           title="Annual Carbon Sequestration Potential",
                           labels={'estimated_tCO2_yr': 'tCO2e per year', 'farm_name': 'Farm'},
                           color='estimated_tCO2_yr',
                           color_continuous_scale='Greens')
        fig_carbon.update_layout(showlegend=False)
        st.plotly_chart(fig_carbon, use_container_width=True)
    
    with tab2:
        st.header(f"{farm['farm_name']} - Operational Dashboard")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Map
            m = folium.Map(location=[farm["lat"], farm["lng"]], zoom_start=13)
            folium.Marker(
                [farm["lat"], farm["lng"]],
                popup=f"<b>{farm['farm_name']}</b><br>{farm['practice']}<br>{farm['area_ha']} ha",
                icon=folium.Icon(color="green", icon="leaf", prefix='fa')
            ).add_to(m)
            st_folium(m, width=700, height=350)
        
        with col2:
            st.markdown("### Carbon Potential")
            st.metric("Annual Sequestration", f"{carbon['estimated_tCO2_yr']:.1f} tCO2e")
            st.metric("Potential Revenue", f"${carbon['annual_revenue_usd']:.0f}/year")
        
        # Time series
        st.subheader("📈 Environmental Indicators Over Time")
        indicators["date"] = pd.to_datetime(indicators["date"])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=indicators["date"], y=indicators["ndvi"], 
                                name="NDVI (Vegetation)", line=dict(color="green", width=2)))
        fig.add_trace(go.Scatter(x=indicators["date"], y=indicators["soil_moisture"], 
                                name="Soil Moisture", line=dict(color="brown", width=2)))
        
        # Add intervention line using add_shape instead
        fig.add_shape(
            type="line",
            x0=farm["intervention_date"],
            x1=farm["intervention_date"],
            y0=0,
            y1=1,
            yref="paper",
            line=dict(color="red", width=2, dash="dash")
        )
        
        # Add annotation for the intervention line
        fig.add_annotation(
            x=farm["intervention_date"],
            y=1,
            yref="paper",
            text="Intervention Start",
            showarrow=False,
            yshift=10,
            font=dict(color="red")
        )
        
        fig.update_layout(height=400, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
        
        # Validation
        st.subheader("✅ Ground Truth Validation")
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"**Practice Confirmed**: {validation['practice_confirmed']}")
            st.info(f"**Method**: {validation['verification_method']}")
        with col2:
            st.info(f"**Date**: {validation['submission_date'].strftime('%B %d, %Y')}")
            st.caption(f"_{validation['notes']}_")
    
    with tab3:
        st.header("💼 Investor Impact Report")
        
        # Calculate metrics
        baseline = indicators[indicators["date"] <= farm["baseline_end"]]
        current = indicators[indicators["date"] > farm["baseline_end"]]
        
        ndvi_delta = ((current["ndvi"].mean() - baseline["ndvi"].mean()) / baseline["ndvi"].mean()) * 100
        soil_delta = ((current["soil_moisture"].mean() - baseline["soil_moisture"].mean()) / baseline["soil_moisture"].mean()) * 100
        rain_delta = current["rainfall_anomaly_pct"].mean() - baseline["rainfall_anomaly_pct"].mean()
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🌱 Vegetation Index", f"+{ndvi_delta:.1f}%", "Biomass increase")
        col2.metric("💧 Soil Moisture", f"+{soil_delta:.1f}%", "Resilience boost")
        col3.metric("🌧️ Climate Stress", f"{rain_delta:+.1f}%", "Rainfall improved")
        col4.metric("🌍 Carbon Credit", f"{carbon['estimated_tCO2_yr']:.1f} tCO2e/yr", "Sequestration")
        
        st.markdown("---")
        
        # Finance section
        st.subheader("💰 Climate Finance Potential")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            #### Revenue Model
            - **Carbon Credits**: ${:.0f}/year
            - **Verification Cost**: ${:.0f}
            - **Net Annual**: ${:.0f}
            - **5-Year Total**: ${:.0f}
            """.format(
                carbon['annual_revenue_usd'],
                carbon['verification_cost_usd'],
                carbon['annual_revenue_usd'] - carbon['verification_cost_usd'],
                carbon['net_benefit_5yr_usd']
            ))
        
        with col2:
            st.markdown("""
            #### Impact Highlights
            - ✅ AI-estimated + Farmer-validated
            - ✅ Baseline comparison methodology
            - ✅ Transparent data provenance
            - ✅ Finance-ready metrics
            """)
        
        # Chart
        finance_data = pd.DataFrame({
            'Category': ['Annual Revenue', 'Verification Cost', 'Net Benefit (5yr)'],
            'Amount (USD)': [carbon['annual_revenue_usd'], carbon['verification_cost_usd'], 
                           carbon['net_benefit_5yr_usd']]
        })
        
        fig = px.bar(finance_data, x='Category', y='Amount (USD)', 
                    title="Financial Breakdown",
                    color='Category',
                    color_discrete_sequence=['#228B22', '#FF8C00', '#32CD32'])
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Download report
        if st.button("📥 Download MRV Report (PDF)", type="primary"):
            pdf = generate_clic_report(farm, indicators, validation, carbon)
            pdf_bytes = bytes(pdf.output())
            st.download_button(
                label="💾 Save Investor Report",
                data=pdf_bytes,
                file_name=f"GreenScope_CLIC_MRV_{farm['farm_id']}.pdf",
                mime="application/pdf"
            )
            st.success("✅ Report generated successfully!")
    
    with tab4:
        st.header("🌍 Climate Impact Summary")
        
        st.markdown("""
        ### Addressing the Climate Finance Gap in Sub-Saharan Africa
        
        **The Challenge:**
        - 🌾 Agrifood systems = **33% of global GHG emissions**
        - 🦋 **60% of biodiversity loss** linked to agriculture
        - 💰 Only **4.3% of climate finance** reaches agrifood sector
        - 📈 Need **7x increase** in finance to meet 2030 goals
        """)
        
        st.markdown("---")
        
        st.subheader("🎯 GreenScope Solution for CLIC Lab")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            #### Innovation Components
            
            1. **Low-Cost MRV**
               - Satellite data (free/low-cost)
               - AI-powered analysis
               - Mobile farmer validation
               - <$50 per farm/year
            
            2. **Aggregation Model**
               - Pool smallholder farms
               - Reduce transaction costs
               - Increase bargaining power
               - Enable market access
            
            3. **Transparent Reporting**
               - Real-time dashboards
               - Investor-ready reports
               - Verifiable impact metrics
               - Open data standards
            """)
        
        with col2:
            st.markdown("""
            #### Impact Pathways
            
            **Mitigation:**
            - Soil carbon sequestration
            - Reduced tillage emissions
            - Enhanced biomass storage
            - Agroforestry co-benefits
            
            **Adaptation:**
            - Improved soil moisture
            - Climate resilience
            - Drought tolerance
            - Biodiversity restoration
            
            **Livelihoods:**
            - Additional farm income
            - Market access
            - Technical support
            - Community benefits
            """)
        
        st.markdown("---")
        
        st.subheader("📈 Scaling Potential")
        
        # Scaling scenarios
        scenarios = pd.DataFrame({
            'Scenario': ['Current MVP', '100 Farms', '1,000 Farms', '10,000 Farms'],
            'Farms': [5, 100, 1000, 10000],
            'Area (ha)': [12.5, 250, 2500, 25000],
            'Carbon (tCO2e/yr)': [32.5, 650, 6500, 65000],
            'Revenue ($k/yr)': [0.49, 9.8, 98, 980]
        })
        
        st.dataframe(scenarios, use_container_width=True)
        
        st.info("""
        **Key Insight**: At scale (10,000 farms), this approach could:
        - Sequester 65,000 tCO2e annually
        - Generate $980,000 in carbon revenue per year
        - Cover 25,000 hectares with climate-smart agriculture
        - Support 10,000+ smallholder households
        """)
        
        st.markdown("---")
        
        st.subheader("🤝 Alignment with CLIC Lab Goals")
        
        st.success("""
        ✅ **Bridge Finance Gap**: Reduces MRV costs from $500+ to <$50 per farm
        
        ✅ **Scale Finance**: Aggregation enables access to carbon markets for smallholders
        
        ✅ **Low-Carbon Pathways**: Validates and incentivizes regenerative practices
        
        ✅ **Climate Resilience**: Tracks adaptation outcomes alongside mitigation
        
        ✅ **Sub-Saharan Africa Focus**: Piloted in Kenya with expansion potential
        
        ✅ **Innovation**: Combines AI, satellite tech, and farmer participation
        """)
        
        st.markdown("---")
        
        st.subheader("📋 Next Steps for CLIC Partnership")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **Phase 1: Pilot** (Months 1-6)
            - Validate with 50-100 farms
            - Refine MRV protocols
            - Test farmer engagement
            - Baseline carbon estimates
            """)
        
        with col2:
            st.markdown("""
            **Phase 2: Scale** (Months 7-18)
            - Expand to 500+ farms
            - Partner with cooperatives
            - Develop carbon aggregation
            - Pilot credit sales
            """)
        
        with col3:
            st.markdown("""
            **Phase 3: Market** (Months 19-36)
            - Full market integration
            - 5,000+ farm portfolio
            - Verified carbon credits
            - Investor returns
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 20px;'>
        <p><b>GreenScope MRV</b> | Built for CLIC Lab Application</p>
        <p>Bridging the climate finance gap for Sub-Saharan African agrifood systems</p>
        <p><i>Simulated data for MVP demonstration purposes</i></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 