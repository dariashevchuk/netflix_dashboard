# app.py

import pandas as pd
import plotly.express as px
from dash import Dash, dash_table, dcc, html, Input, Output, State

# ────────────────────────────────────────────────────────────────────────────────
# 1) Load & preprocess the Netflix dataset
# ────────────────────────────────────────────────────────────────────────────────

# Replace "netflix_titles.csv" with the correct path if needed
df = pd.read_csv("netflix_titles.csv")

# Parse 'date_added' for any future time-based filters (optional)
df["date_added_parsed"] = pd.to_datetime(df["date_added"], format="%B %d, %Y", errors="coerce")

# Create a "country" column in which each title appears once per country.
# The original dataset has a pipe-delimited string of countries in the 'country' column.
# We will explode that so each row represents a single title–country combination.
df_countries = df[["show_id", "title", "country"]].copy()
df_countries["country"] = df_countries["country"].fillna("")
df_countries["country_list"] = df_countries["country"].str.split(",\s*")
df_countries = df_countries.explode("country_list")
df_countries["country_list"] = df_countries["country_list"].str.strip()
df_countries = df_countries[df_countries["country_list"] != ""]

# Count how many titles appear per country
vc = df_countries["country_list"].value_counts().sort_values(ascending=False)
country_counts = pd.DataFrame({
    "country": vc.index,
    "count": vc.values
})

# ────────────────────────────────────────────────────────────────────────────────
# 2) Create a DataTable listing all titles
# ────────────────────────────────────────────────────────────────────────────────

# We will display a subset of columns in the table
columns_to_display = ["title", "type", "release_year", "rating"]

# ────────────────────────────────────────────────────────────────────────────────
# 3) Build the Plotly Express choropleth figure
#    — use a pink color scale with no artificial capping
# ────────────────────────────────────────────────────────────────────────────────

# Define a simple pink gradient from very light pink to deeper pink
pink_scale = ["#ffe6f2", "#ff4da6"]

# Let Plotly automatically choose the color range so that no values are capped
fig_country = px.choropleth(
    country_counts,
    locations="country",
    locationmode="country names",
    color="count",
    hover_name="country",
    color_continuous_scale=pink_scale,
    title="Number of Netflix Titles by Country",
)
fig_country.update_layout(
    margin=dict(l=0, r=0, t=40, b=0),
    coloraxis_colorbar=dict(
        title="Title Count",
        thicknessmode="pixels",
        thickness=15,
        lenmode="fraction",
        len=0.5,
    ),
)

# ────────────────────────────────────────────────────────────────────────────────
# 4) Initialize the Dash app
# ────────────────────────────────────────────────────────────────────────────────

app = Dash(__name__)

app.layout = html.Div(
    style={"display": "flex", "flexDirection": "row", "height": "100vh"},
    children=[
        # ┌───────────────────────────────────────────────────────────────────────────┐
        # │ LEFT COLUMN: DataTable                                                 │
        # └───────────────────────────────────────────────────────────────────────────┘
        html.Div(
            style={
                "flex": "1",
                "padding": "20px",
                "overflowY": "auto",
                "borderRight": "1px solid #ddd",
            },
            children=[
                html.H2("Netflix Titles"),
                dash_table.DataTable(
                    id="titles-table",
                    columns=[{"name": col.replace("_", " ").title(), "id": col} for col in columns_to_display],
                    data=df.to_dict("records"),
                    page_size=10,
                    row_selectable="single",
                    selected_rows=[],
                    style_table={"overflowX": "auto"},
                    style_cell={
                        "minWidth": "120px",
                        "width": "120px",
                        "maxWidth": "180px",
                        "whiteSpace": "normal",
                    },
                ),
                html.Div(id="detail-panel", style={"marginTop": "20px"}),
            ],
        ),

        # ┌───────────────────────────────────────────────────────────────────────────┐
        # │ RIGHT COLUMN: Choropleth Map                                            │
        # └───────────────────────────────────────────────────────────────────────────┘
        html.Div(
            style={
                "flex": "2",
                "padding": "20px",
                "display": "flex",
                "flexDirection": "column",
            },
            children=[
                dcc.Graph(id="country-map", figure=fig_country),
                # Removed instructional text as requested
            ],
        ),
    ],
)

# ────────────────────────────────────────────────────────────────────────────────
# 5) Callback to display details of a selected title
# ────────────────────────────────────────────────────────────────────────────────

@app.callback(
    Output("detail-panel", "children"),
    Input("titles-table", "selected_rows"),
    State("titles-table", "data"),
)
def display_title_details(selected_rows, rows):
    if not selected_rows:
        return html.Div()

    # Only one row is selectable at a time, so we take the first index
    idx = selected_rows[0]
    row = rows[idx]

    detail_children = []
    detail_children.append(html.H3(row.get("title", "No Title")))
    detail_children.append(
        html.P([html.B("Type: "), row.get("type", "Unknown")], style={"marginBottom": "5px"})
    )
    detail_children.append(
        html.P([html.B("Release Year: "), row.get("release_year", "Unknown")], style={"marginBottom": "5px"})
    )
    detail_children.append(
        html.P([html.B("Rating: "), row.get("rating", "Unknown")], style={"marginBottom": "5px"})
    )
    detail_children.append(
        html.P([html.B("Duration: "), row.get("duration", "Unknown")], style={"marginBottom": "5px"})
    )
    detail_children.append(
        html.P([html.B("Genres: "), row.get("listed_in", "Unknown")], style={"marginBottom": "15px"})
    )
    detail_children.append(
        html.Div(
            [
                html.B("Description:"),
                html.P(row.get("description", ""), style={"whiteSpace": "pre-wrap"}),
            ],
            style={"paddingTop": "10px", "borderTop": "1px solid #ddd"},
        )
    )

    return detail_children

# ────────────────────────────────────────────────────────────────────────────────
# 6) Run the app (use app.run instead of app.run_server for newer Dash versions)
# ────────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)
