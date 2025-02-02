# Import necessary libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page configuration
st.set_page_config(
    page_title="Obesity Risk Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load your dataset
@st.cache_data
def load_data():
    return pd.read_csv('ObesityDataSet_raw_and_data_sinthetic.csv')

df = load_data()

# ============================================
# Dashboard Title and Description
# ============================================
st.title("📊 Obesity Risk Factors Analysis Dashboard")
st.markdown("""
**Objective:** Explore key factors influencing obesity levels (NObeyesdad) through comprehensive visual analysis.
""")

# ============================================
# Helper Functions for Visualizations
# ============================================
def plot_target_distribution():
    """Distribution of target variable (NObeyesdad)"""
    fig = px.bar(df['NObeyesdad'].value_counts().reset_index(), 
                 x='NObeyesdad', y='count', 
                 color='count',
                 title='Distribution of Obesity Levels',
                 labels={'count': 'Number of Cases', 'NObeyesdad': 'Obesity Category'})
    fig.update_layout(title_x=0.5)
    return fig

def plot_age_weight_relationship():
    """Relationship between Age, Weight, and Obesity Level"""
    fig = px.scatter(df, x='Age', y='Weight', 
                    color='NObeyesdad',
                    title='Age vs Weight Colored by Obesity Level',
                    hover_data=['Height', 'Gender'],
                    color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(title_x=0.5)
    return fig

def plot_feature_distributions():
    """Feature distributions split by obesity level"""
    fig = make_subplots(rows=2, cols=2,
                       subplot_titles=('Height Distribution', 'Weight Distribution',
                                      'Physical Activity Frequency', 'Water Consumption'))
    
    # Height Distribution
    fig.add_trace(go.Box(x=df['NObeyesdad'], y=df['Height'], 
                        name='Height', marker_color='#1f77b4'),
                 row=1, col=1)
    
    # Weight Distribution
    fig.add_trace(go.Box(x=df['NObeyesdad'], y=df['Weight'], 
                        name='Weight', marker_color='#ff7f0e'),
                 row=1, col=2)
    
    # Physical Activity
    fig.add_trace(go.Violin(x=df['NObeyesdad'], y=df['FAF'],
                           name='Physical Activity', box_visible=True,
                           marker_color='#2ca02c'),
                 row=2, col=1)
    
    # Water Consumption
    fig.add_trace(go.Violin(x=df['NObeyesdad'], y=df['CH2O'],
                           name='Water Consumption', box_visible=True,
                           marker_color='#d62728'),
                 row=2, col=2)
    
    fig.update_layout(height=800, title_text="Feature Distributions by Obesity Level", 
                     title_x=0.5, showlegend=False)
    return fig

def create_funnel_chart():
    """Funnel chart of obesity divided by gender"""
    funnel_df = df.groupby(['NObeyesdad', 'Gender']).size().reset_index(name='count')
    fig = px.funnel(funnel_df, x='count', y='NObeyesdad', color='Gender',
                   title='Obesity Distribution by Gender')
    fig.update_layout(title_x=0.5)
    return fig

def create_sunburst_chart():
    """Sunburst chart of gender > family history > obesity"""
    fig = px.sunburst(df, path=['Gender', 'family_history_with_overweight', 'NObeyesdad'],
                     title='Obesity Hierarchy: Gender → Family History → Obesity Level',
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(title_x=0.5)
    return fig

def create_grouped_bar():
    """Grouped bar chart for smoking and alcohol impact"""
    # Convert SMOKE to numeric
    df['SMOKE'] = df['SMOKE'].map({'yes': 1, 'no': 0})
    
    smoke_alc_df = df.groupby('NObeyesdad').agg({
        'SMOKE': 'mean',
        'CALC': lambda x: (x == 'Frequently').mean()
    }).reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=smoke_alc_df['NObeyesdad'],
        y=smoke_alc_df['SMOKE'],
        name='Smokers',
        marker_color='#FFA15A'
    ))
    fig.add_trace(go.Bar(
        x=smoke_alc_df['NObeyesdad'],
        y=smoke_alc_df['CALC'],
        name='Frequent Alcohol Consumers',
        marker_color='#00CC96'
    ))
    fig.update_layout(
        title='Impact of Smoking & Alcohol Consumption',
        barmode='group',
        xaxis_title='Obesity Level',
        yaxis_title='Proportion',
        title_x=0.5
    )
    return fig

def create_water_box():
    """Water consumption box plot"""
    fig = px.box(df, x='NObeyesdad', y='CH2O',
                color='NObeyesdad',
                title='Water Consumption Patterns',
                labels={'CH2O': 'Daily Water Consumption'},
                color_discrete_sequence=px.colors.qualitative.Dark2)
    fig.update_layout(title_x=0.5)
    return fig

# ============================================
# Dashboard Layout
# ============================================
# Row 1: Key Metrics
st.header("🔑 Key Metrics Overview")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Samples", len(df))
with col2:
    st.metric("Unique Obesity Categories", df['NObeyesdad'].nunique())
with col3:
    st.metric("Average Age", f"{df['Age'].mean():.1f} years")
with col4:
    st.metric("Average Weight", f"{df['Weight'].mean():.1f} kg")

# Row 2: Target Distribution
st.header("🎯 Target Variable Analysis")
st.plotly_chart(plot_target_distribution(), use_container_width=True)

# Row 3: Feature Distributions
st.header("📈 Feature Distributions by Obesity Level")
st.plotly_chart(plot_feature_distributions(), use_container_width=True)

# Row 4: Demographic Relationships
st.header("👥 Demographic Relationships")
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(create_funnel_chart(), use_container_width=True)
with col2:
    st.plotly_chart(create_sunburst_chart(), use_container_width=True)

# Row 5: Behavioral Factors
st.header("🚬 Behavioral Factors Analysis")
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(create_grouped_bar(), use_container_width=True)
with col2:
    st.plotly_chart(create_water_box(), use_container_width=True)

# Row 6: Age-Weight Relationship
st.header("⚖️ Age-Weight Relationship")
st.plotly_chart(plot_age_weight_relationship(), use_container_width=True)

# ============================================
# Insights Section
# ============================================
st.header("💡 Key Insights")
with st.expander("Show Analysis Insights"):
    st.markdown("""
    1. **Obesity Distribution:** Clear categorization of obesity levels with varying prevalence
    2. **Demographic Patterns:** Gender and family history show strong correlation with obesity levels
    3. **Behavioral Factors:** Smoking and alcohol consumption patterns vary across obesity categories
    4. **Physical Metrics:** Weight distribution shows significant variation between obesity classes
    5. **Water Consumption:** Notable differences in hydration habits across different weight categories
    6. **Age-Weight Correlation:** Visible trend of increasing weight with age in most categories
    """)

# ============================================
# Run with: streamlit run obesity_dashboard.py
# ============================================
