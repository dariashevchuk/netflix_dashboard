import pandas as pd
from dash import Dash, dash_table, dcc, html, Input, Output, State

# 1) Load the CSV
df = pd.read_csv("netflix_titles.csv")

# 2) Parse date_added as datetime (for any future filtering, though not strictly needed here)
df["date_added_parsed"] = pd.to_datetime(df["date_added"], format="%B %d, %Y", errors="coerce")

# 3) Create any additional columns you’d like (optional):
#    e.g., extract numeric duration or split genres, but for this “row→detail” demo we’ll just show raw text.
#    We’ll assume we want to display: title, type, release_year, rating, duration, country, director, cast, description.

# 4) For convenience, reset index so that DataTable row indices match df indices exactly
df = df.reset_index(drop=True)


app = Dash(__name__)

# Define which columns to show in the DataTable by default
# Here we show: Title, Type, Release Year, Rating
columns_to_display = ["title", "type", "release_year", "rating"]

app.layout = html.Div(
    style={"display": "flex", "flexDirection": "row", "height": "100vh"},
    children=[
        # ┌─────────────────────────────────────────┐
        # │ LEFT COLUMN: DataTable                 │
        # └─────────────────────────────────────────┘
        html.Div(
            style={
                "width": "45%",
                "padding": "10px",
                "borderRight": "1px solid #ccc",
                "overflowY": "auto",
            },
            children=[
                html.H2("Netflix Titles"),
                dash_table.DataTable(
                    id="titles-table",
                    columns=[{"name": col.replace("_", " ").title(), "id": col} for col in columns_to_display],
                    data=df.to_dict("records"),            # feed full data; DataTable handles pagination
                    page_size=10,                            # show 10 rows per page
                    row_selectable="single",                # allow selecting exactly one row
                    selected_rows=[],                       # no selection by default
                    style_table={"overflowX": "auto"},
                    style_cell={
                        "minWidth": "120px",
                        "width": "120px",
                        "maxWidth": "180px",
                        "whiteSpace": "normal",
                    },
                ),
            ],
        ),

        # ┌─────────────────────────────────────────┐
        # │ RIGHT COLUMN: Detail Panel             │
        # └─────────────────────────────────────────┘
        html.Div(
            id="detail-panel",
            style={"width": "55%", "padding": "20px"},
            children=[
                html.H2("Select a Title"),
                html.P("Click a row on the left to see details here."),
            ],
        ),
    ],
)
@app.callback(
    Output("detail-panel", "children"),
    Input("titles-table", "selected_rows"),
    State("titles-table", "data"),
)
def update_detail_panel(selected_rows, table_data):
    """
    When a user selects a row in the DataTable, 'selected_rows' is a list of indices.
    We’ll grab that index, look up the corresponding row in 'table_data' (which matches df),
    and build a set of html.Div / html.P children to display all the relevant info.
    """
    if not selected_rows:
        # No selection: show placeholder text
        return [
            html.H2("Select a Title"),
            html.P("Click a row on the left to see details here."),
        ]

    # There is exactly one selected row (because we set row_selectable="single")
    row_index = selected_rows[0]

    # table_data is a list of dicts (each dict = one row with keys = column IDs). 
    # But note: 'table_data[row_index]' corresponds exactly to df.iloc[row_index].
    row = table_data[row_index]

    # Build a detail card showing all fields. You can style this however you like.
    # Example: Show title, type, release_year, rating, duration, country, director, cast, description.

    detail_children = []

    # 1) Title as Big Header
    detail_children.append(html.H1(row["title"], style={"marginBottom": "10px"}))

    # 2) Basic metadata (Type, Year, Rating, Duration, Country)
    meta_items = []
    meta_items.append(html.Span(f"Type: {row.get('type', 'N/A')}", style={"marginRight": "20px"}))
    meta_items.append(html.Span(f"Year: {row.get('release_year', 'N/A')}", style={"marginRight": "20px"}))
    meta_items.append(html.Span(f"Rating: {row.get('rating', 'N/A')}", style={"marginRight": "20px"}))
    meta_items.append(html.Span(f"Duration: {row.get('duration', 'N/A')}", style={"marginRight": "20px"}))
    meta_items.append(html.Span(f"Country: {row.get('country', 'N/A')}", style={"marginRight": "20px"}))
    detail_children.append(html.Div(meta_items, style={"marginBottom": "15px"}))

    # 3) Director & Cast
    detail_children.append(html.P([html.B("Director: "), row.get("director", "Unknown")], style={"marginBottom": "5px"}))
    detail_children.append(html.P([html.B("Cast: "), row.get("cast", "Unknown")], style={"marginBottom": "15px"}))

    # 4) Date Added
    date_added = row.get("date_added", "Unknown")
    detail_children.append(html.P([html.B("Date Added to Netflix: "), date_added], style={"marginBottom": "15px"}))

    # 5) Genres (Listed_in)
    detail_children.append(html.P([html.B("Genres: "), row.get("listed_in", "Unknown")], style={"marginBottom": "15px"}))

    # 6) Description (take the full text)
    detail_children.append(html.Div([
        html.B("Description:"),
        html.P(row.get("description", ""), style={"whiteSpace": "pre-wrap"})
    ], style={"paddingTop": "10px", "borderTop": "1px solid #ddd"}))

    return detail_children

if __name__ == "__main__":
    app.run(debug=True)
