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
st.markdown("**Objective:** Explore key factors influencing obesity levels (NObeyesdad) through visual analysis.")

# ============================================
# Updated Target Distribution
# ============================================
def plot_target_distribution():
    """Sorted bar chart for obesity level distribution with a single color and in-bar annotations."""
    
    category_counts = df['NObeyesdad'].value_counts().sort_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=category_counts.index.astype(str),  # Ensure categorical x-axis
        y=category_counts.values, 
        text=category_counts.values,  # Display count as text
        textposition='outside',  # Place text above the bars
        marker_color='#0086eb',  # Single color for all bars
    ))
    
    fig.update_layout(
        title="Distribution of Obesity Levels",
        xaxis_title="Obesity Category",
        yaxis_title="Number of Cases",
        title_x=0.5,
        showlegend=False  # No legend needed for a single-color plot
    )
    
    return fig



# ============================================
# New Stacked Bar Chart (FAF vs Obesity)
# ============================================
# Define categorical mapping for FAF
FAF_MAPPING = {
    0: 'I do not have',
    1: '1 or 2 days',
    2: '2 or 4 days',
    3: '4 or 5 days'
}

def plot_faf_stacked():
    """Stacked bar chart of obesity levels stacked by physical activity (FAF) with categorized labels."""
    
    global df  # Ensure df is accessible inside the function
    
    # Map FAF to categorical labels
    df['FAF_category'] = df['FAF'].map(FAF_MAPPING)
    
    # Group data
    faf_distribution = df.groupby(['NObeyesdad', 'FAF_category']).size().reset_index(name='count')
    
    # Define discrete color scale
    color_scale = px.colors.qualitative.Plotly  # Or use other qualitative color scales
    
    # Create an empty figure
    fig = go.Figure()
    
    # Create one trace for each FAF_category
    for i, category in enumerate(faf_distribution['FAF_category'].unique()):
        category_data = faf_distribution[faf_distribution['FAF_category'] == category]
        
        fig.add_trace(go.Bar(
            x=category_data['NObeyesdad'], 
            y=category_data['count'], 
            name=category,
            text=category_data['count'],  # Add the text for annotations
            textposition='inside',  # Place text inside the bars
            marker_color=color_scale[i % len(color_scale)]  # Set color from the color scale
        ))
    
    # Update layout
    fig.update_layout(
        title='Physical Activity (FAF) Across Obesity Levels',
        barmode='stack',  # Stack the bars
        xaxis_title='Obesity Level',
        yaxis_title='Number of Cases',
        title_x=0.5,
        showlegend=True,  # Show legend for the different FAF categories
    )
    
    return fig






def plot_height_weight_relationship():
    """Relationship between Height, Weight, and Obesity Level"""
    fig = px.scatter(df, x='Height', y='Weight', 
                    color='NObeyesdad',
                    title='Height vs Weight Colored by Obesity Level',
                    hover_data=['Height', 'Gender'],
                    color_discrete_sequence=px.colors.qualitative.Plotly)
    fig.update_layout(title_x=0.5)
    return fig


def create_funnel_chart():
    """Funnel chart of obesity divided by gender"""
    funnel_df = df.groupby(['NObeyesdad', 'Gender']).size().reset_index(name='count')
    fig = px.funnel(funnel_df, x='count', y='NObeyesdad', color='Gender',
                   title='Obesity Distribution by Gender',
                    color_discrete_sequence=px.colors.qualitative.Plotly)
    fig.update_layout(title_x=0.5)
    return fig

def create_sunburst_chart():
    """Sunburst chart of gender > family history > obesity"""
    fig = px.sunburst(df, path=['Gender', 'family_history_with_overweight', 'NObeyesdad'],
                     title='Obesity Hierarchy: Gender → Family History → Obesity Level',
                     color_discrete_sequence=px.colors.qualitative.D3)
    fig.update_layout(title_x=0.5)
    return fig

def create_grouped_bar():
    """Grouped bar chart for smoking and alcohol impact (percentages)."""
    
    # Convert SMOKE to numeric
    df['SMOKE'] = df['SMOKE'].map({'yes': 1, 'no': 0})
    
    # Compute proportions
    smoke_alc_df = df.groupby('NObeyesdad').agg({
        'SMOKE': 'mean',
        'CALC': lambda x: (x == 'Frequently').mean()
    }).reset_index()
    
    # Convert to percentage
    smoke_alc_df[['SMOKE', 'CALC']] *= 100  
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=smoke_alc_df['NObeyesdad'],
        y=smoke_alc_df['SMOKE'],
        name='Smokers',
        marker_color='#00f59b',
        text=smoke_alc_df['SMOKE'].round(1).astype(str) + '%',  # Add percentage labels
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        x=smoke_alc_df['NObeyesdad'],
        y=smoke_alc_df['CALC'],
        name='Frequent Alcohol Consumers',
        marker_color='#7014f2',
        text=smoke_alc_df['CALC'].round(1).astype(str) + '%',  # Add percentage labels
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Impact of Smoking & Alcohol Consumption',
        barmode='group',
        xaxis_title='Obesity Level',
        yaxis_title='Percentage (%)',  # Update y-axis label
        title_x=0.5,
        yaxis=dict(tickformat=".0f")  # Ensure whole number format on y-axis
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

st.header('🔍 Customer Churn Insights: Understanding Key Drivers of Attrition')
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

# Row 3: Behavioral Factors
st.header("🚬 Behavioral Factors Analysis")
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(plot_faf_stacked(), use_container_width=True)
with col2:
    st.plotly_chart(create_grouped_bar(), use_container_width=True)

st.plotly_chart(create_water_box(), use_container_width=True)  
# Row 4: Demographic Relationships
st.header("👥 Demographic Relationships")
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(create_funnel_chart(), use_container_width=True)
with col2:
    st.plotly_chart(create_sunburst_chart(), use_container_width=True)

# Row 5: Age-Weight Relationship
st.header("⚖️ Height-Weight Relationship")
st.plotly_chart(plot_height_weight_relationship(), use_container_width=True)



