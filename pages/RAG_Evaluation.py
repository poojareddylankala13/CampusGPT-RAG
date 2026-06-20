import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from modules.auth import check_auth
from modules.database import get_evaluation_metrics_logs
from modules.ui import inject_custom_css, render_sidebar

# 1. Auth Guard
check_auth()

# 2. Page Setup
inject_custom_css()
render_sidebar()

st.markdown("<h1 class='gradient-header'>📈 RAG Performance Evaluation</h1>", unsafe_allow_html=True)
st.markdown(
    "Monitor latency benchmarks, context sizes, chunk similarity metrics, and compare local-first vs cloud AI modes."
)

# 3. Load Evaluation Logs
logs = get_evaluation_metrics_logs(limit=100)

if not logs:
    st.info("💡 No performance evaluations logged yet. Ask questions in the Chat assistant to record metrics!")
else:
    df = pd.DataFrame(logs)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # 4. Display KPI Summary
    st.markdown("### 📊 Metrics Summary")

    avg_retrieval = df["retrieval_time"].mean()
    avg_generation = df["generation_time"].mean()
    avg_similarity = df["avg_similarity"].mean() * 100
    avg_context = df["context_length"].mean()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg Retrieval Latency", f"{avg_retrieval:.3f}s")
    with col2:
        st.metric("Avg Generation Latency", f"{avg_generation:.3f}s")
    with col3:
        st.metric("Avg Chunk Match Score", f"{avg_similarity:.1f}%")
    with col4:
        st.metric("Avg Context Size", f"{int(avg_context)} chars")

    st.markdown("---")

    # 5. Latency Charts
    st.markdown("### ⏱️ Latency Distribution Over Time")

    fig_latency = go.Figure()
    fig_latency.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["retrieval_time"],
            mode="lines+markers",
            name="Retrieval Time",
            line=dict(color="#4b6b94", width=2),
            marker=dict(size=6),
        )
    )
    fig_latency.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["generation_time"],
            mode="lines+markers",
            name="Generation Time",
            line=dict(color="#1b365d", width=2),
            marker=dict(size=6),
        )
    )
    fig_latency.update_layout(
        title="Retrieval vs Generation Time History (Seconds)",
        xaxis_title="Execution Time",
        yaxis_title="Seconds",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=50, b=40, l=40, r=20),
        xaxis=dict(showgrid=True, gridcolor="rgba(200,200,200,0.1)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(200,200,200,0.1)"),
    )
    st.plotly_chart(fig_latency, use_container_width=True)

    # 6. Mode comparison (Llama vs Gemini) and Context sizing charts
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 🤖 Engine Latency Comparison")
        # Group by ai_mode and get mean generation time
        df_grouped = df.groupby("ai_mode")["generation_time"].mean().reset_index()
        fig_comp = px.bar(
            df_grouped,
            x="ai_mode",
            y="generation_time",
            labels={"ai_mode": "AI Mode / Engine", "generation_time": "Average Generation Time (s)"},
            color="ai_mode",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_comp.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(t=30, b=20, l=20, r=20),
        )
        st.plotly_chart(fig_comp, use_container_width=True)

    with col_right:
        st.markdown("### 📈 Match Quality vs Context Length")
        fig_scatter = px.scatter(
            df,
            x="context_length",
            y="avg_similarity",
            color="ai_mode",
            size="chunk_count",
            labels={"context_length": "Total Context Length (chars)", "avg_similarity": "Similarity Score (0-1)"},
            hover_data=["query"],
        )
        fig_scatter.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=30, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # 7. Metrics Log Table
    st.markdown("### 📋 Recent Evaluation Logs")
    table_data = df[
        ["timestamp", "query", "ai_mode", "retrieval_time", "generation_time", "avg_similarity", "context_length"]
    ].copy()
    table_data["retrieval_time"] = table_data["retrieval_time"].map(lambda x: f"{x:.3f}s")
    table_data["generation_time"] = table_data["generation_time"].map(lambda x: f"{x:.3f}s")
    table_data["avg_similarity"] = table_data["avg_similarity"].map(lambda x: f"{x*100:.1f}%")
    table_data.columns = [
        "Timestamp",
        "User Query",
        "AI Mode",
        "Retrieval Time",
        "Gen Time",
        "Avg Similarity",
        "Context Length (chars)",
    ]

    st.dataframe(table_data, use_container_width=True)
