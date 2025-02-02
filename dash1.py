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
    """Sorted bar chart for obesity level distribution with distinct colors."""
    category_counts = df['NObeyesdad'].value_counts().sort_index()
    fig = px.bar(category_counts, 
                 x=category_counts.index, 
                 y=category_counts.values, 
                 title="Distribution of Obesity Levels",
                 labels={'x': 'Obesity Category', 'y': 'Number of Cases'},
                 color=category_counts.index,
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(title_x=0.5)
    return fig

# ============================================
# New Stacked Bar Chart (FAF vs Obesity)
# ============================================
def plot_faf_stacked():
    """Stacked bar chart of obesity levels stacked by physical activity (FAF)."""
    faf_distribution = df.groupby(['NObeyesdad', 'FAF']).size().reset_index(name='count')
    fig = px.bar(faf_distribution, 
                 x='NObeyesdad', y='count', color='FAF', 
                 title='Physical Activity (FAF) Across Obesity Levels', 
                 labels={'count': 'Number of Cases', 'FAF': 'Physical Activity Frequency'},
                 barmode='stack')
    fig.update_layout(title_x=0.5)
    return fig

# ============================================
# Convert Categorical & Numerical Feature Plots to Plotly
# ============================================
def plot_categorical_features():
    """Plot categorical feature distributions."""
    categorical_features = df.select_dtypes(exclude="number").columns
    figs = []
    for feature in categorical_features:
        # Correcting how the value counts are handled
        value_counts = df[feature].value_counts().reset_index()
        value_counts.columns = [feature, 'count']  # Rename columns
        fig = px.bar(value_counts, 
                     x=feature, y='count', 
                     title=f'{feature} Distribution',
                     labels={feature: 'Category', 'count': 'Count'},
                     color=feature)
        fig.update_layout(title_x=0.5)
        figs.append(fig)
    return figs


def plot_numerical_features():
    """Plot numerical feature distributions (histogram + boxplot)."""
    numerical_features = df.select_dtypes(include="number").columns
    figs = []
    for feature in numerical_features:
        fig = make_subplots(rows=1, cols=2, subplot_titles=(f'{feature} Histogram', f'{feature} Boxplot'))
        fig.add_trace(go.Histogram(x=df[feature], name='Histogram', marker_color='blue'), row=1, col=1)
        fig.add_trace(go.Box(y=df[feature], name='Boxplot', marker_color='red'), row=1, col=2)
        fig.update_layout(title_text=f'{feature} Distribution', title_x=0.5)
        figs.append(fig)
    return figs

import plotly.express as px

def plot_categorical_features_target():
    """Plot categorical features vs target using interactive stacked bar charts."""
    categorical_features = df.select_dtypes(exclude="number").columns.drop('NObeyesdad', errors='ignore')
    fig = make_subplots(rows=1, cols=len(categorical_features),
                        subplot_titles=[f"{feat} vs Obesity" for feat in categorical_features],
                        shared_yaxes=True)
    
    for i, feature in enumerate(categorical_features):
        grouped = df.groupby(['NObeyesdad', feature]).size().reset_index(name='count')
        pivot_df = grouped.pivot(index='NObeyesdad', columns=feature, values='count').fillna(0)
        
        for j, category in enumerate(pivot_df.columns):
            fig.add_trace(
                go.Bar(
                    x=pivot_df.index,
                    y=pivot_df[category],
                    name=str(category),
                    marker_color=px.colors.qualitative.Pastel[j % len(px.colors.qualitative.Pastel)],
                    showlegend=(i == 0)  # Show legend only for first subplot
                ),
                row=1,
                col=i + 1
            )
        
        fig.update_xaxes(title_text='Obesity Level', row=1, col=i + 1)
        fig.update_yaxes(title_text="Count", row=1, col=i + 1)
    
    fig.update_layout(
        height=500,
        barmode='stack',
        title_text="Categorical Features vs Obesity Level",
        margin=dict(t=100),
        legend_title_text="Categories"
    )
    return fig

# ============================================
# Numerical Features vs Target
# ============================================
def plot_numerical_features_target():
    """Plot numerical features vs target using interactive KDE plots."""
    numerical_features = df.select_dtypes(include="number").columns.drop('NObeyesdad', errors='ignore')
    fig = make_subplots(rows=1, cols=len(numerical_features),
                        subplot_titles=[f"{feat} Density" for feat in numerical_features],
                        shared_yaxes=True)
    
    for i, feature in enumerate(numerical_features):
        for j, target in enumerate(df['NObeyesdad'].unique()):
            data = df[df['NObeyesdad'] == target][feature].dropna()
            if len(data) > 1:
                kde = gaussian_kde(data)
                x = np.linspace(data.min(), data.max(), 500)
                y = kde(x)
                
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=y,
                        mode='lines',
                        name=target,
                        line=dict(color=px.colors.qualitative.Pastel[j % len(px.colors.qualitative.Pastel)], width=2),
                        showlegend=(i == 0)  # Show legend only for first subplot
                    ),
                    row=1,
                    col=i + 1
                )
        
        fig.update_xaxes(title_text=feature, row=1, col=i + 1)
        fig.update_yaxes(title_text="Density", row=1, col=i + 1)
    
    fig.update_layout(
        height=500,
        title_text="Numerical Features Density by Obesity Level",
        margin=dict(t=100),
        legend_title_text="Obesity Levels"
    )
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
st.plotly_chart(plot_age_weight_relationship(), use_container_width=True)

# ============================================
# Categorical & Numerical Feature Plots
# ============================================
st.header("📊 Categorical Feature Analysis")
for fig in plot_categorical_features():
    st.plotly_chart(fig, use_container_width=True)

st.header("📊 Numerical Feature Analysis")
for fig in plot_numerical_features():
    st.plotly_chart(fig, use_container_width=True)

# Row 4: Categorical Features vs Target
st.header("📊 Categorical Features vs Obesity Level")
st.plotly_chart(plot_categorical_features_target(), use_container_width=True)

# Row 5: Numerical Features vs Target
st.header("📈 Numerical Features vs Obesity Level")
st.plotly_chart(plot_numerical_features_target(), use_container_width=True)

