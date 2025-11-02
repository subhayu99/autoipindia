"""
AutoIPIndia Dashboard - Dash Frontend
A professional admin panel for managing Indian trademark statuses.
"""

import dash
from dash import dcc, html, dash_table, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc
from dash_ag_grid import AgGrid
import pandas as pd
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TOKEN = os.getenv("API_TOKEN")

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    title="AutoIPIndia Dashboard",
    suppress_callback_exceptions=True
)

# Expose server for Gunicorn
server = app.server

# API Client Helper
class APIClient:
    """Helper class for making authenticated API calls"""

    @staticmethod
    def get_headers():
        if not API_TOKEN:
            raise ValueError("API_TOKEN not configured")
        return {"Authorization": f"Bearer {API_TOKEN}"}

    @staticmethod
    def get_all_trademarks():
        """Fetch all trademarks from the API"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/retrieve/all",
                headers=APIClient.get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching trademarks: {e}")
            return []

    @staticmethod
    def ingest_trademark(application_number=None, wordmark=None, class_name=None):
        """Ingest a specific trademark"""
        try:
            if application_number:
                response = requests.get(
                    f"{API_BASE_URL}/ingest/tm/{application_number}",
                    headers=APIClient.get_headers(),
                    timeout=120
                )
            elif wordmark and class_name:
                response = requests.get(
                    f"{API_BASE_URL}/ingest/tm",
                    params={"wordmark": wordmark, "class_name": class_name},
                    headers=APIClient.get_headers(),
                    timeout=120
                )
            else:
                return {"success": False, "error": "Missing parameters"}

            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def search_trademark(application_number=None, wordmark=None, class_name=None):
        """Search for a specific trademark"""
        try:
            if application_number:
                response = requests.get(
                    f"{API_BASE_URL}/search/tm/{application_number}",
                    headers=APIClient.get_headers(),
                    timeout=30
                )
            elif wordmark and class_name:
                response = requests.get(
                    f"{API_BASE_URL}/search/tm",
                    params={"wordmark": wordmark, "class_name": class_name},
                    headers=APIClient.get_headers(),
                    timeout=30
                )
            else:
                return None

            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error searching trademark: {e}")
            return None


# App Layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1([
                html.I(className="fas fa-trademark me-3"),
                "AutoIPIndia Dashboard"
            ], className="text-primary mb-0"),
            html.P("Indian Trademark Status Management", className="text-muted")
        ], width=8),
        dbc.Col([
            dbc.Button([
                html.I(className="fas fa-sync-alt me-2"),
                "Refresh All"
            ], id="refresh-btn", color="primary", className="float-end mt-3")
        ], width=4)
    ], className="mb-4 mt-3"),

    # Statistics Cards
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="total-count", className="text-primary"),
                    html.P("Total Trademarks", className="text-muted mb-0")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="registered-count", className="text-success"),
                    html.P("Registered", className="text-muted mb-0")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="pending-count", className="text-warning"),
                    html.P("Pending", className="text-muted mb-0")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="other-count", className="text-info"),
                    html.P("Other Status", className="text-muted mb-0")
                ])
            ])
        ], width=3),
    ], className="mb-4"),

    # Add New Trademark Form
    dbc.Card([
        dbc.CardHeader([
            html.I(className="fas fa-plus-circle me-2"),
            "Add New Trademark"
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Application Number"),
                    dbc.Input(id="input-app-number", placeholder="e.g., 1234567", type="text")
                ], width=4),
                dbc.Col([
                    html.P("OR", className="text-center text-muted mt-4")
                ], width=1),
                dbc.Col([
                    dbc.Label("Wordmark"),
                    dbc.Input(id="input-wordmark", placeholder="e.g., NIKE", type="text")
                ], width=3),
                dbc.Col([
                    dbc.Label("Class"),
                    dbc.Input(id="input-class", placeholder="e.g., 25", type="number")
                ], width=2),
                dbc.Col([
                    dbc.Button([
                        html.I(className="fas fa-download me-2"),
                        "Ingest"
                    ], id="ingest-btn", color="success", className="mt-4 w-100")
                ], width=2)
            ]),
            dbc.Alert(id="ingest-alert", is_open=False, dismissable=True, className="mt-3")
        ])
    ], className="mb-4"),

    # Search/Filter Section
    dbc.Card([
        dbc.CardHeader([
            html.I(className="fas fa-search me-2"),
            "Search & Filter"
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Input(
                        id="search-input",
                        placeholder="Search by application number, wordmark, or status...",
                        type="text",
                        debounce=True
                    )
                ], width=10),
                dbc.Col([
                    dbc.Button([
                        html.I(className="fas fa-times")
                    ], id="clear-search", color="secondary", outline=True)
                ], width=2)
            ])
        ])
    ], className="mb-4"),

    # Main Data Table
    dbc.Card([
        dbc.CardHeader([
            html.I(className="fas fa-table me-2"),
            "Trademarks Database"
        ]),
        dbc.CardBody([
            html.Div(id="table-container"),
            html.Div(id="selected-info", className="mt-3")
        ])
    ], className="mb-4"),

    # Hidden components for state management
    dcc.Store(id="table-data-store"),
    dcc.Interval(id="auto-refresh-interval", interval=60000, n_intervals=0, disabled=True),

    # Modal for refresh confirmation
    dbc.Modal([
        dbc.ModalHeader("Refresh Trademark"),
        dbc.ModalBody(id="modal-body"),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="modal-cancel", color="secondary"),
            dbc.Button("Refresh", id="modal-confirm", color="primary")
        ])
    ], id="refresh-modal", is_open=False),

], fluid=True, className="py-3")


# Callbacks

@callback(
    [Output("table-data-store", "data"),
     Output("total-count", "children"),
     Output("registered-count", "children"),
     Output("pending-count", "children"),
     Output("other-count", "children")],
    [Input("refresh-btn", "n_clicks"),
     Input("auto-refresh-interval", "n_intervals")],
    prevent_initial_call=False
)
def update_data(n_clicks, n_intervals):
    """Fetch data from API and update statistics"""
    data = APIClient.get_all_trademarks()

    if not data:
        return [], "0", "0", "0", "0"

    df = pd.DataFrame(data)

    # Calculate statistics
    total = len(df)
    registered = len(df[df['status'].str.contains('Registered', case=False, na=False)]) if 'status' in df.columns else 0
    pending = len(df[df['status'].str.contains('Pending|Examination', case=False, na=False)]) if 'status' in df.columns else 0
    other = total - registered - pending

    return data, str(total), str(registered), str(pending), str(other)


@callback(
    Output("table-container", "children"),
    [Input("table-data-store", "data"),
     Input("search-input", "value")]
)
def update_table(data, search_value):
    """Update the data table with optional filtering"""
    if not data:
        return dbc.Alert("No data available. Click 'Refresh All' to load data.", color="info")

    df = pd.DataFrame(data)

    # Apply search filter
    if search_value:
        mask = df.astype(str).apply(lambda x: x.str.contains(search_value, case=False, na=False)).any(axis=1)
        df = df[mask]

    # Format timestamp
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')

    # Reorder columns for better display
    column_order = ['application_number', 'wordmark', 'class_name', 'status', 'timestamp']
    available_columns = [col for col in column_order if col in df.columns]
    df = df[available_columns]

    # Create AG Grid table
    column_defs = [
        {
            "headerName": "Application Number",
            "field": "application_number",
            "filter": True,
            "sortable": True,
            "checkboxSelection": True,
            "width": 200
        },
        {
            "headerName": "Wordmark",
            "field": "wordmark",
            "filter": True,
            "sortable": True,
            "width": 200
        },
        {
            "headerName": "Class",
            "field": "class_name",
            "filter": True,
            "sortable": True,
            "width": 100
        },
        {
            "headerName": "Status",
            "field": "status",
            "filter": True,
            "sortable": True,
            "width": 300
        },
        {
            "headerName": "Last Updated",
            "field": "timestamp",
            "filter": True,
            "sortable": True,
            "width": 200
        }
    ]

    return AgGrid(
        id="trademark-table",
        rowData=df.to_dict("records"),
        columnDefs=column_defs,
        defaultColDef={
            "resizable": True,
            "sortable": True,
            "filter": True
        },
        dashGridOptions={
            "pagination": True,
            "paginationPageSize": 20,
            "rowSelection": "single",
            "animateRows": True
        },
        style={"height": "600px"}
    )


@callback(
    Output("selected-info", "children"),
    Input("trademark-table", "selectedRows")
)
def show_selected_info(selected_rows):
    """Show information about selected trademark with refresh button"""
    if not selected_rows:
        return dbc.Alert("Select a trademark row to view details and refresh options", color="light", className="mb-0")

    row = selected_rows[0]

    return dbc.Card([
        dbc.CardHeader("Selected Trademark"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Strong("Application Number: "),
                    html.Span(row.get('application_number', 'N/A'))
                ], width=3),
                dbc.Col([
                    html.Strong("Wordmark: "),
                    html.Span(row.get('wordmark', 'N/A'))
                ], width=3),
                dbc.Col([
                    html.Strong("Class: "),
                    html.Span(row.get('class_name', 'N/A'))
                ], width=2),
                dbc.Col([
                    html.Strong("Status: "),
                    html.Span(row.get('status', 'N/A'))
                ], width=2),
                dbc.Col([
                    dbc.Button([
                        html.I(className="fas fa-sync-alt me-2"),
                        "Re-ingest"
                    ], id="reingest-btn", color="warning", size="sm", className="float-end")
                ], width=2)
            ])
        ])
    ], color="light", className="mt-0")


@callback(
    [Output("ingest-alert", "children"),
     Output("ingest-alert", "is_open"),
     Output("ingest-alert", "color"),
     Output("input-app-number", "value"),
     Output("input-wordmark", "value"),
     Output("input-class", "value")],
    [Input("ingest-btn", "n_clicks"),
     Input("reingest-btn", "n_clicks")],
    [State("input-app-number", "value"),
     State("input-wordmark", "value"),
     State("input-class", "value"),
     State("trademark-table", "selectedRows")],
    prevent_initial_call=True
)
def handle_ingest(ingest_clicks, reingest_clicks, app_num, wordmark, class_name, selected_rows):
    """Handle trademark ingestion (new or re-ingest)"""
    triggered_id = ctx.triggered_id

    # Determine which button was clicked
    if triggered_id == "reingest-btn" and selected_rows:
        row = selected_rows[0]
        app_num = row.get('application_number')
        result = APIClient.ingest_trademark(application_number=app_num)
    elif triggered_id == "ingest-btn":
        if app_num:
            result = APIClient.ingest_trademark(application_number=app_num)
        elif wordmark and class_name:
            result = APIClient.ingest_trademark(wordmark=wordmark, class_name=class_name)
        else:
            return "Please provide either Application Number OR (Wordmark + Class)", True, "warning", app_num, wordmark, class_name
    else:
        return "", False, "info", app_num, wordmark, class_name

    # Check result
    if "error" in result:
        return f"Error: {result['error']}", True, "danger", app_num, wordmark, class_name
    else:
        success_count = result.get('success', 0)
        failed_count = result.get('failed', 0)
        message = f"Success! Ingested: {success_count}, Failed: {failed_count}"
        return message, True, "success", "", "", ""


@callback(
    Output("search-input", "value", allow_duplicate=True),
    Input("clear-search", "n_clicks"),
    prevent_initial_call=True
)
def clear_search(n_clicks):
    """Clear search input"""
    return ""


# Run the app
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8050))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    app.run_server(host="0.0.0.0", port=port, debug=debug)
