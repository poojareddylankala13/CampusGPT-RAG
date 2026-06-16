import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging

logger = logging.getLogger("CampusGPT.analytics")

def create_storage_chart(docs_storage):
    """Generates a Plotly pie chart representing storage space distribution by document."""
    if not docs_storage:
        return None
        
    df = pd.DataFrame(docs_storage)
    # Convert sizes to KB/MB for readability
    df['size_kb'] = df['file_size'] / 1024
    
    fig = px.pie(
        df,
        values='size_kb',
        names='name',
        title='Document Storage Distribution (KB)',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(textinfo='percent+label', textposition='inside')
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff' if not px.colors.qualitative.Plotly else '#333333'),
        margin=dict(t=40, b=20, l=20, r=20)
    )
    return fig

def create_activity_chart(questions_by_day, searches_by_day):
    """Generates a combined Plotly line chart for questions and searches over time."""
    if not questions_by_day and not searches_by_day:
        return None
        
    df_q = pd.DataFrame(questions_by_day) if questions_by_day else pd.DataFrame(columns=['date_val', 'count_val'])
    df_s = pd.DataFrame(searches_by_day) if searches_by_day else pd.DataFrame(columns=['date_val', 'count_val'])
    
    fig = go.Figure()
    
    if not df_q.empty:
        df_q['date_val'] = pd.to_datetime(df_q['date_val'])
        fig.add_trace(go.Scatter(
            x=df_q['date_val'], 
            y=df_q['count_val'],
            mode='lines+markers',
            name='Chat Questions',
            line=dict(color='#1b365d', width=3),
            marker=dict(size=8)
        ))
        
    if not df_s.empty:
        df_s['date_val'] = pd.to_datetime(df_s['date_val'])
        fig.add_trace(go.Scatter(
            x=df_s['date_val'], 
            y=df_s['count_val'],
            mode='lines+markers',
            name='Semantic Searches',
            line=dict(color='#4b6b94', width=3, dash='dash'),
            marker=dict(size=8)
        ))
        
    fig.update_layout(
        title='System Activity Over Time',
        xaxis_title='Date',
        yaxis_title='Count',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=50, b=40, l=40, r=20),
        xaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.1)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.1)')
    )
    return fig

def create_user_activity_chart(user_activity):
    """Generates a horizontal bar chart displaying user question activities."""
    if not user_activity:
        return None
        
    df = pd.DataFrame(user_activity)
    
    fig = px.bar(
        df,
        x='count_val',
        y='name',
        orientation='h',
        title='Most Active Users (Chat Questions)',
        labels={'count_val': 'Questions Asked', 'name': 'User Name'},
        color='count_val',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis={'categoryorder':'total ascending'},
        margin=dict(t=40, b=20, l=20, r=20)
    )
    return fig

def create_feedback_chart(feedback_scores):
    """Generates a donut chart displaying helpful vs. not helpful feedback."""
    if not feedback_scores:
        return None
        
    df = pd.DataFrame(feedback_scores)
    # Map rating to display labels
    rating_map = {'helpful': 'Helpful (👍)', 'not_helpful': 'Not Helpful (👎)'}
    df['rating_label'] = df['rating'].map(rating_map)
    
    # Define custom colors
    colors = {'Helpful (👍)': '#2ec4b6', 'Not Helpful (👎)': '#e71d36'}
    
    fig = px.pie(
        df,
        values='count_val',
        names='rating_label',
        title='Response Feedback Rating Breakdown',
        hole=0.5,
        color='rating_label',
        color_discrete_map=colors
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=20, l=20, r=20)
    )
    return fig
