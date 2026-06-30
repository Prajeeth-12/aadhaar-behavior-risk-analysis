import dash
from dash import dcc, html, dash_table, callback_context, no_update
from dash.dependencies import Input, Output, State, ALL, MATCH
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import warnings
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from report_generator import generate_report

# Suppress pandas FutureWarning (Plotly/Pandas compatibility issue)
warnings.simplefilter(action='ignore', category=FutureWarning)

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUTS_DIR = os.path.join(BASE_DIR, '..', 'outputs')

# --- Load Data ---
def load_data():
    try:
        # 1. Main District Data
        main_path = os.path.join(OUTPUTS_DIR, 'district_analysis_results.csv')
        df = pd.read_csv(main_path)
        
        # 2. Feature Importance
        feat_path = os.path.join(OUTPUTS_DIR, 'feature_importance.csv')
        feat_df = pd.read_csv(feat_path) if os.path.exists(feat_path) else pd.DataFrame()
        
        # 3. Model Comparison
        model_path = os.path.join(OUTPUTS_DIR, 'model_comparison.csv')
        model_df = pd.read_csv(model_path) if os.path.exists(model_path) else pd.DataFrame()
        
        return df, feat_df, model_df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df, feat_df, model_df = load_data()

# --- Preprocessing: On-the-fly Analytics ---
# Compute PCA for High-Dimensional Visualization
if not df.empty:
    numeric_cols = [c for c in df.columns if df[c].dtype in ['int64', 'float64'] and 'total' in c or 'age' in c or 'score' in c]
    # Fill NAs just in case
    x = df[numeric_cols].fillna(0)
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x)
    
    pca = PCA(n_components=3)
    components = pca.fit_transform(x_scaled)
    
    df['PC1'] = components[:, 0]
    df['PC2'] = components[:, 1]
    df['PC3'] = components[:, 2]

# --- Plotly Theme ---
COMMON_LAYOUT = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#1C2025', family='Plus Jakarta Sans'),
    margin=dict(l=40, r=40, t=40, b=40),
    xaxis=dict(showgrid=True, gridcolor='rgba(0, 0, 0, 0.1)'),
    yaxis=dict(showgrid=True, gridcolor='rgba(0, 0, 0, 0.1)'),
)

# --- Components ---
def create_metric_card(title, value, trend=None, color_class="text-primary"):
    return html.Div([
        html.H3(title, className="kpi-label"),
        html.Div(value, className=f"kpi-value {color_class}"),
        html.Div(trend, className="text-muted small") if trend else None
    ], className="glass-card h-100")

sidebar = html.Div([
    html.Div([
        #html.Div(className="logo-icon"),
        html.Span("AADHAAR PRS ANALYTICS", className="logo-text mono-font", style={"fontSize": "12px", "lineHeight": "1.2"}),
    ], className="logo"),
    
    html.Div([
        html.Div([html.I(className="bi bi-grid-fill"), "Mission Control"], id="nav-overview", className="nav-item active"),
        html.Div([html.I(className="bi bi-graph-up"), "Deep Analytics"], id="nav-analytics", className="nav-item"),
        html.Div([html.I(className="bi bi-images"), "Chart Gallery"], id="nav-gallery", className="nav-item"),
        html.Div([html.I(className="bi bi-cpu"), "ML Insights"], id="nav-ml", className="nav-item"),
        html.Div([html.I(className="bi bi-table"), "Data Registry"], id="nav-data", className="nav-item"),
        html.Div([html.I(className="bi bi-file-text"), "Executive Report"], id="nav-report", className="nav-item"),
    ], className="nav-menu"),

    html.Div([
        html.Div([
            html.Span("Team ", className="text-secondary fw-bold", style={"fontSize": "11px", "letterSpacing": "0.5px"}),
            html.Span("Algo", className="fw-bold", style={"fontSize": "11px", "color": "#000000", "letterSpacing": "0.5px"}),
            html.Span("QX", className="fw-bold", style={"fontSize": "11px", "color": "#FF5F1F", "letterSpacing": "0.5px"}),
            html.Span(" | UIDAI_4834", className="text-muted fw-bold", style={"fontSize": "11px", "letterSpacing": "0.5px"})
        ], className="mb-3"),
        html.H6("TEAM MEMBERS", className="text-muted small mt-4 mb-3", style={"letterSpacing": "1px", "fontSize": "10px"}),
        html.Div([html.I(className="bi bi-person-fill me-2"), "Kaveri K"], className="text-secondary small fw-bold mb-2"),
        html.Div([html.I(className="bi bi-person-fill me-2"), "Dhanya G"], className="text-secondary small fw-bold mb-2"),
        html.Div([html.I(className="bi bi-person-fill me-2"), "Bala Saravanan K"], className="text-secondary small fw-bold mb-2"),
        html.Div([html.I(className="bi bi-person-fill me-2"), "Prajeeth H"], className="text-secondary small fw-bold mb-2"),
        html.Div([html.I(className="bi bi-person-fill me-2"), "Sreesanth R"], className="text-secondary small fw-bold mb-2")
    ], className="mt-auto pt-4 border-top", style={"borderColor": "rgba(255,255,255,0.1)"})
], className="sidebar")

# --- App Init ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "AADHAAR PRS ANALYTICS FROM ANTIGRAVITY"

# --- Layout ---
app.layout = html.Div([
    sidebar,
    html.Div([
        dcc.Store(id='current-page', data='overview'),
        html.Div(id='page-content')
    ], className="main-content"),
    
    # Image Popup Modal
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Detailed View"), close_button=True),
        dbc.ModalBody(html.Img(id="modal-image", src="", style={"width": "100%", "height": "auto"})),
    ], id="image-modal", size="xl", centered=True, is_open=False),
    
    # Global Components (Hidden)
    dcc.Download(id="download-pdf")
], className="app-container")

# --- Page Renderers ---
def render_overview():
    # 1. Map (Scatter Geo or just Bubble Plot on States) -> Let's use Bubble Chart for State Performance
    state_summary = df.groupby('state')[['prs_score', 'total_enrolled']].mean().reset_index()
    fig_bubble = px.scatter(state_summary, x='total_enrolled', y='prs_score', size='total_enrolled', 
                            color='prs_score', hover_name='state',
                            color_continuous_scale='Oranges', title="State Intelligence Map (PRS vs Volume)",
                            template='plotly_white')
    fig_bubble.update_layout(**COMMON_LAYOUT, height=400)
    
    # 2. Risk Distribution
    fig_risk = px.histogram(df, x='risk_level', color='risk_level', 
                            color_discrete_map={'Low': '#2ea043', 'Medium': '#d29922', 'High': '#f85149', 'Critical': '#bd00ff'},
                            title="National Risk Vector", template='plotly_white')
    fig_risk.update_layout(**COMMON_LAYOUT, height=350, showlegend=False)


    return html.Div([
        html.H2("Mission Control", className="section-title"),
        
        # KPI Row
        dbc.Row([
            dbc.Col(create_metric_card("Monitored Districts", f"{len(df)}"), width=3),
            dbc.Col(create_metric_card("Total Population Est", f"{df['total_enrolled'].sum()/1e6:.2f}M", color_class="text-accent-secondary"), width=3),
            dbc.Col(create_metric_card("Avg PRS Score", f"{df['prs_score'].mean():.2f}", color_class="text-accent"), width=3),
            dbc.Col(create_metric_card("Critical Anomalies", f"{len(df[df['risk_level']=='High'])}", color_class="text-danger"), width=3),
        ], className="mb-4"),
        
        # Charts
        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_bubble)], className="glass-card"), width=8),
            dbc.Col(html.Div([dcc.Graph(figure=fig_risk)], className="glass-card"), width=4),
        ])
    ])

def render_analytics():
    # 3D PCA
    fig_3d = px.scatter_3d(df, x='PC1', y='PC2', z='PC3', color='risk_level', 
                           hover_name='district', hover_data=['state', 'prs_score'],
                           color_discrete_map={'Low': '#2ea043', 'Medium': '#d29922', 'High': '#f85149', 'Critical': '#bd00ff'},
                           title="Multi-Dimensional District Clustering (PCA)", template='plotly_white')
    fig_3d.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#1C2025'), margin=dict(l=0, r=0, t=40, b=0), height=600)
    
    # Anomaly Scatter
    fig_anom = px.scatter(df, x='total_enrolled', y='ml_predicted_failures', color='risk_level',
                          log_x=True, log_y=True, hover_name='district',
                          title="Anomaly Detection: Predicted Failures vs Volume", template='plotly_white')
    fig_anom.update_layout(**COMMON_LAYOUT, height=400)

    return html.Div([
        html.H2("Deep Analytics", className="section-title"),
        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_3d)], className="glass-card h-100"), width=8),
            dbc.Col([
                html.Div([dcc.Graph(figure=fig_anom)], className="glass-card mb-4"),
                html.Div([
                    html.H4("Cluster Insights", className="text-secondary mb-3"),
                    html.P("Districts cluster clearly along volumetrics (PC1) and biometric update intensity (PC2). Outliers in the upper quadrant indicate high-risk migration hubs.", className="small text-muted")
                ], className="glass-card")
            ], width=4)
        ])
    ])

def render_gallery():
    return html.Div([
        html.H2("Visual Intelligence Gallery", className="section-title"),
        
        dbc.Tabs([
            dbc.Tab(label="Time Series", children=[
                dbc.Row([
                    dbc.Col(html.Img(src=app.get_asset_url('timeseries_daily_trend.png'), id={'type': 'gallery-img', 'index': 'timeseries_daily_trend.png'}, n_clicks=0, className="img-fluid glass-card mb-4_all_imgs", style={"width": "100%", "height": "350px", "objectFit": "contain", "cursor": "pointer"}), width=6),
                    dbc.Col(html.Img(src=app.get_asset_url('trend_decomposition.png'), id={'type': 'gallery-img', 'index': 'trend_decomposition.png'}, n_clicks=0, className="img-fluid glass-card mb-4_all_imgs", style={"width": "100%", "height": "350px", "objectFit": "contain", "cursor": "pointer"}), width=6)
                ], className="py-4")
            ], tab_id="tab-ts"),
            
            dbc.Tab(label="Clustering Analysis", children=[
                dbc.Row([
                    dbc.Col(html.Img(src=app.get_asset_url('clustering_visualization.png'), id={'type': 'gallery-img', 'index': 'clustering_visualization.png'}, n_clicks=0, className="img-fluid glass-card mb-4_all_imgs", style={"width": "100%", "height": "350px", "objectFit": "contain", "cursor": "pointer"}), width=6),
                    dbc.Col(html.Img(src=app.get_asset_url('clustering_elbow.png'), id={'type': 'gallery-img', 'index': 'clustering_elbow.png'}, n_clicks=0, className="img-fluid glass-card mb-4_all_imgs", style={"width": "100%", "height": "350px", "objectFit": "contain", "cursor": "pointer"}), width=6)
                ], className="py-4")
            ], tab_id="tab-cluster"),
            
            dbc.Tab(label="Model Diagnostics", children=[
                dbc.Row([
                    dbc.Col(html.Img(src=app.get_asset_url('learning_curves.png'), id={'type': 'gallery-img', 'index': 'learning_curves.png'}, n_clicks=0, className="img-fluid glass-card mb-4_all_imgs", style={"width": "100%", "height": "350px", "objectFit": "contain", "cursor": "pointer"}), width=6),
                    dbc.Col(html.Img(src=app.get_asset_url('classification_confusion_matrix.png'), id={'type': 'gallery-img', 'index': 'classification_confusion_matrix.png'}, n_clicks=0, className="img-fluid glass-card mb-4_all_imgs", style={"width": "100%", "height": "350px", "objectFit": "contain", "cursor": "pointer"}), width=6),
                    dbc.Col(html.Img(src=app.get_asset_url('intervention_simulation.png'), id={'type': 'gallery-img', 'index': 'intervention_simulation.png'}, n_clicks=0, className="img-fluid glass-card mb-4_all_imgs", style={"width": "100%", "height": "350px", "objectFit": "contain", "cursor": "pointer"}), width=6),
                    dbc.Col(html.Div(className="d-flex align-items-center justify-content-center h-100", children=[html.H4("Sensitivity Analysis", className="text-secondary opacity-50")]), width=6) 
                ], className="py-4")
            ], tab_id="tab-diag"),
            
            dbc.Tab(label="Demographics", children=[
                dbc.Row([
                    dbc.Col(html.Img(src=app.get_asset_url('univariate_age_distributions.png'), id={'type': 'gallery-img', 'index': 'univariate_age_distributions.png'}, n_clicks=0, className="img-fluid glass-card mb-4_all_imgs", style={"width": "100%", "height": "350px", "objectFit": "contain", "cursor": "pointer"}), width=6),
                    dbc.Col(html.Div(className="d-flex align-items-center justify-content-center h-100 glass-card", children=[html.P("Additional demographic cuts pending data integration.", className="text-muted small")]), width=6)
                ], className="py-4")
            ], tab_id="tab-demo"),
        ], active_tab="tab-ts", style={"marginBottom": "2rem"})
    ])

def render_ml():
    # Feature Importance
    if not feat_df.empty:
        fig_feat = px.bar(feat_df.head(10).sort_values(by='importance_mean', ascending=True), 
                          x='importance_mean', y='feature', orientation='h',
                          title="Predictive Factors (SHAP/Permutation Importance)", 
                          color='importance_mean', color_continuous_scale='Oranges',
                          template='plotly_white')
        fig_feat.update_layout(**COMMON_LAYOUT, height=400)
    else:
        fig_feat = go.Figure()

    # Model Comparison
    if not model_df.empty:
        fig_model = px.bar(model_df, x='model', y='r2', title="Model Accuracy (R² Score)",
                           color='r2', color_continuous_scale='Magma', template='plotly_white')
        fig_model.update_layout(**COMMON_LAYOUT, height=400)
        fig_model.update_yaxes(range=[0.8, 1.0])
    else:
        fig_model = go.Figure()

    return html.Div([
        html.H2("Machine Learning Intelligence", className="section-title"),
        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=fig_feat)], className="glass-card"), width=6),
            dbc.Col(html.Div([dcc.Graph(figure=fig_model)], className="glass-card"), width=6),
        ])
    ])

def render_data():
    return html.Div([
        html.H2("District Data Registry", className="section-title"),
        html.Div([
            dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{"name": i, "id": i} for i in ['state', 'district', 'total_enrolled', 'prs_score', 'risk_level']],
                page_size=20,
                sort_action="native",
                filter_action="native",
                style_header={'backgroundColor': '#161b22', 'color': '#ffffff', 'fontWeight': 'bold'},
                style_data={'backgroundColor': '#0d1117', 'color': '#e6edf3', 'border': '1px solid #30363d'},
                style_filter={'backgroundColor': '#161b22', 'color': '#e6edf3'},
            )
        ], className="glass-card")
    ])

def render_report():
    return html.Div([
        html.H2("Executive Summary", className="section-title"),
        
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4("Analysis Conclusion"),
                    html.Hr(style={"borderTop": "1px solid rgba(255,255,255,0.1)"}),
                    html.P("Our comprehensive analysis of 764 districts reveals a robust Aadhaar ecosystem with distinct behavioral signatures. The Proactive-Reactive Score (PRS) successfully categorizes districts into actionable cohorts, identifying a predictable 'Transition' phase that precedes localized crises.", className="lead"),
                    
                    html.H5("Key Findings", className="text-secondary mt-4"),
                    html.Ul([
                        html.Li("764 Districts Processed: Complete national coverage achieved with 100% data integrity."),
                        html.Li("ML Accuracy > 99%: The Lasso Regression model predicts enrollment failures with R²=0.9926, validating the PRS methodology."),
                        html.Li("Crisis Detection: 10 'Crisis-Dependent' and 140 'Reactive' districts identified for immediate intervention."),
                        html.Li("Regional Pattern: The East region exhibits significantly higher reactive traits (Avg PRS: 0.459), correlating with known migration corridors.")
                    ]),
                    
                    html.H5("Strategic Recommendations", className="text-secondary mt-4"),
                    html.P("1. Immediate deployment of mobile enrollment units to the 10 identified Crisis-Dependent districts."),
                    html.P("2. Digital literacy campaigns in the 140 Reactive districts to shift behavior towards proactivity."),
                    html.P("3. Continued monitoring of the 16 high-confidence anomalies flagged by the Multi-Layered Outlier Detection system.")
                ], className="glass-card h-100")
            ], width=8),
            
            dbc.Col([
                html.Div([
                    html.H4("Intervention ROI"),
                    html.Img(src=app.get_asset_url('intervention_simulation.png'), id={'type': 'gallery-img', 'index': 'intervention_simulation.png'}, n_clicks=0, className="img-fluid rounded border border-secondary mb-3", style={"cursor": "pointer"}),
                    html.P("Simulation indicates that 'Awareness Drives' provide the highest ROI for 'Transition' districts, while 'Direct Intervention' is required for 'Crisis-Dependent' zones.", className="small text-muted")
                ], className="glass-card mb-4"),
                
                html.Div([
                    html.H4("Download Report"),
                    html.Button("Download Full PDF", id="btn-download-pdf", className="btn btn-outline-primary w-100"),
                ], className="glass-card")
            ], width=4)
        ])
    ])

# --- Validation Layout (Silences false positives for dynamic components) ---
app.validation_layout = html.Div([
    app.layout,
    render_overview(),
    render_analytics(),
    render_gallery(),
    render_ml(),
    render_data(),
    render_report()
])

# --- Callbacks ---
@app.callback(
    [Output('page-content', 'children'),
     Output('nav-overview', 'className'),
     Output('nav-analytics', 'className'),
     Output('nav-gallery', 'className'),
     Output('nav-ml', 'className'),
     Output('nav-data', 'className'),
     Output('nav-report', 'className')],
    [Input('nav-overview', 'n_clicks'),
     Input('nav-analytics', 'n_clicks'),
     Input('nav-gallery', 'n_clicks'),
     Input('nav-ml', 'n_clicks'),
     Input('nav-data', 'n_clicks'),
     Input('nav-report', 'n_clicks')]
)
def navigate(n1, n2, n3, n4, n5, n6):
    ctx = callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'nav-overview'
    
    # Active Class Logic
    base_class = 'nav-item'
    classes = {k: base_class for k in ['nav-overview', 'nav-analytics', 'nav-gallery', 'nav-ml', 'nav-data', 'nav-report']}
    classes[button_id] = f'{base_class} active'
    
    content = render_overview()
    if button_id == 'nav-analytics': content = render_analytics()
    elif button_id == 'nav-gallery': content = render_gallery()
    elif button_id == 'nav-ml': content = render_ml()
    elif button_id == 'nav-data': content = render_data()
    elif button_id == 'nav-report': content = render_report()
    
    return content, *classes.values()

@app.callback(
    Output("download-pdf", "data"),
    Input("btn-download-pdf", "n_clicks"),
    prevent_initial_call=True,
)
def download_report(n_clicks):
    if n_clicks:
        # Generate the report on the fly (or serve existing one)
        report_path = os.path.join(os.path.dirname(__file__), 'assets', 'UIDAI_Report.pdf')
        # We use a temp path or assert path first. Let's direct generate to assets
        output_file = generate_report(output_path=report_path, text_summary_path=os.path.join(BASE_DIR, '..', 'outputs', 'executive_summary.txt'))
        return dcc.send_file(output_file)

@app.callback(
    [Output("image-modal", "is_open"), Output("modal-image", "src")],
    [Input({"type": "gallery-img", "index": ALL}, "n_clicks")],
    [State("image-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_modal(n_clicks, is_open):
    ctx = callback_context
    if not ctx.triggered:
        return is_open, no_update
    
    # Debugging
    print(f"Triggered: {ctx.triggered_id}")
    
    # Robustly get the ID
    trigger_id = ctx.triggered_id
    
    # If trigger_id is a dict (Pattern Matching), extract index
    if trigger_id and isinstance(trigger_id, dict):
        img_filename = trigger_id.get('index')
        if img_filename:
            return True, app.get_asset_url(img_filename)
            
    return is_open, no_update

# --- Run ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
