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
    """Sorted bar chart for obesity level distribution with a single color and annotations."""
    category_counts = df['NObeyesdad'].value_counts().sort_index()
    fig = px.bar(category_counts, 
                 x=category_counts.index, 
                 y=category_counts.values, 
                 title="Distribution of Obesity Levels",
                 labels={'x': 'Obesity Category', 'y': 'Number of Cases'},
                 color_discrete_sequence=['#0086eb'])  # Single color
    
    # Add annotations
    for i, count in enumerate(category_counts.values):
        fig.add_annotation(
            x=category_counts.index[i],
            y=count + 10,  # Offset for better visibility
            text=str(count),
            showarrow=False,
            font=dict(size=12, color='black')
        )
    
    fig.update_layout(
        title_x=0.5,
        showlegend=False  # Hide legend since it's a single color
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
    
    # Create stacked bar plot
    fig = px.bar(
        faf_distribution, 
        x='NObeyesdad', 
        y='count', 
        color='FAF_category', 
        title='Physical Activity (FAF) Across Obesity Levels', 
        labels={'count': 'Number of Cases', 'FAF_category': 'Physical Activity Frequency'},
        barmode='stack',
        color_discrete_sequence=color_scale
    )
    
    fig.update_layout(title_x=0.5)
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
        marker_color='#00f59b'
    ))
    fig.add_trace(go.Bar(
        x=smoke_alc_df['NObeyesdad'],
        y=smoke_alc_df['CALC'],
        name='Frequent Alcohol Consumers',
        marker_color='#7014f2'
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
st.header("⚖️ Age-Weight Relationship")
st.plotly_chart(plot_height_weight_relationship(), use_container_width=True)



