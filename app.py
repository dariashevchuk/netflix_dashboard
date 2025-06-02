import os
import pandas as pd
import plotly.express as px
from dash import Dash, dash_table, dcc, html, Input, Output, State

df = pd.read_csv("netflix_titles.csv")
df["date_added_parsed"] = pd.to_datetime(df["date_added"], errors="coerce")

df_countries = df[["show_id", "title", "country"]].copy()
df_countries["country"] = df_countries["country"].fillna("")
df_countries["country_list"] = df_countries["country"].str.split(r",\s*")
df_countries = df_countries.explode("country_list")
df_countries["country_list"] = df_countries["country_list"].str.strip()
df_countries = df_countries[df_countries["country_list"] != ""]
vc = df_countries["country_list"].value_counts().sort_values(ascending=False)
country_counts = pd.DataFrame({"country": vc.index, "count": vc.values})

df_genre = df.copy()
df_genre["genre"] = df_genre["listed_in"].str.split(r", ")
df_genre = df_genre.explode("genre")
df_genre["date_added_parsed"] = pd.to_datetime(df_genre["date_added"], errors="coerce")

df_ratings = df.copy()
df_ratings["release_year"] = pd.to_numeric(df_ratings["release_year"], errors="coerce")
df_ratings = df_ratings.dropna(subset=["release_year"])
valid_years = sorted([int(year) for year in df_ratings['release_year'].unique()])

df_additions = df.dropna(subset=["date_added_parsed"]).copy()
df_additions["year_month"] = df_additions["date_added_parsed"].dt.to_period("M").dt.to_timestamp()

df_dir = df[["show_id", "title", "director", "type"]].copy()
df_dir = df_dir.dropna(subset=["director"])
df_dir["director_list"] = df_dir["director"].str.split(r",\s*")
df_dir = df_dir.explode("director_list")
df_dir["director_list"] = df_dir["director_list"].str.strip()

columns_to_display = ["title", "type", "release_year", "rating"]

pink_scale = ["#ffe6f2", "#ff4da6"]
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
    title_font=dict(color="black", size=18),
    font=dict(color="black")
)

spongebob_colors = ["#FFEB3B", "#03A9F4", "#E91E63", "#9C27B0", "#FF9800", "#8BC34A", "#00BCD4", "#FFC107", "#673AB7", "#FF5722"]

app = Dash(__name__)
app.title = "Netflix Dashboard"

app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='About', children=[
            html.Div([
                html.Img(src='assets/logo.png', style={'width': '200px', 'margin': '20px auto', 'display': 'block'}),
                html.H2("About This Dashboard", style={"textAlign": "center", "color": "black"}),
                html.P("This dashboard provides a comprehensive analysis of Netflix's content library using various interactive visualizations. Here's what each section represents:", style={"padding": "10px 40px", "fontSize": "16px"}),
                html.Ul([
                    html.Li([html.B("Main Dashboard: "), "Displays a choropleth map and data table of Netflix titles." ]),
                    html.Li([html.B("Top Genres: "), "Bar chart of the top 10 most popular genres." ]),
                    html.Li([html.B("Rating Breakdown: "), "Pie chart showing distribution of content ratings." ]),
                    html.Li([html.B("Yearly Trends: "), "Line chart showing titles added over time." ]),
                    html.Li([html.B("Director Popularity: "), "Bar chart of the top 10 directors." ])
                ], style={"padding": "0 40px", "fontSize": "16px"})
            ], style={"maxWidth": "900px", "margin": "auto"})
        ]),
        dcc.Tab(label='Main Dashboard', children=[
            html.Div(style={"display": "flex", "height": "90vh"}, children=[
                html.Div(style={"flex": "1", "padding": "20px", "overflowY": "auto", "borderRight": "1px solid #ddd"}, children=[
                    html.H2("Netflix Titles"),
                    dash_table.DataTable(
                        id="titles-table",
                        columns=[{"name": col.replace("_", " ").title(), "id": col} for col in columns_to_display],
                        data=df.to_dict("records"),
                        page_size=15,
                        row_selectable="single",
                        selected_rows=[],
                        style_table={"overflowX": "auto"},
                        style_cell={"minWidth": "150px", "width": "150px", "maxWidth": "200px", "whiteSpace": "normal"},
                    ),
                    html.Div(id="detail-panel", style={"marginTop": "20px"})
                ]),
                html.Div(style={"flex": "1", "padding": "20px"}, children=[dcc.Graph(id="country-map", figure=fig_country)])
            ])
        ]),
        dcc.Tab(label='Top Genres', children=[
            html.Div([
                html.H2("Top Netflix Genres", style={"textAlign": "center", "color": "black"}),
                html.Div([
                    html.Label("Select Date Range"),
                    dcc.DatePickerRange(id='genre-date-range', start_date=df_genre['date_added_parsed'].min(), end_date=df_genre['date_added_parsed'].max(), display_format='YYYY-MM-DD'),
                    html.Label("Filter by Type"),
                    dcc.Dropdown(id='genre-type', options=[{'label': i, 'value': i} for i in df_genre['type'].dropna().unique()], placeholder="Choose Movie or TV Show")
                ], style={"width": "50%", "margin": "auto"}),
                dcc.Graph(id='genre-bar-chart')
            ])
        ]),
        dcc.Tab(label='Rating Breakdown', children=[
            html.Div([
                html.H2("Netflix Content Rating Breakdown", style={"textAlign": "center", "color": "black"}),
                html.Div([
                    html.Label("Select Release Year"),
                    dcc.Slider(id='rating-year', min=0, max=len(valid_years) - 1, value=len(valid_years) - 1, marks={i: str(valid_years[i]) for i in range(len(valid_years)) if i % 5 == 0 or i == len(valid_years) - 1}, step=1),
                    html.Label("Filter by Type"),
                    dcc.Dropdown(id='rating-type', options=[{'label': i, 'value': i} for i in df_ratings['type'].dropna().unique()], placeholder="Choose Movie or TV Show")
                ], style={"width": "60%", "margin": "auto"}),
                dcc.Graph(id='rating-pie-chart')
            ])
        ]),
        dcc.Tab(label='Yearly Trends', children=[
            html.Div([
                html.H2("Titles Added Over Time", style={"textAlign": "center", "color": "black"}),
                html.Div([
                    html.Label("Select Date Range"),
                    dcc.DatePickerRange(id='trend-date-range', start_date=df_additions["year_month"].min().date(), end_date=df_additions["year_month"].max().date(), display_format='YYYY-MM-DD'),
                    html.Label("Filter by Type", style={"marginLeft": "20px"}),
                    dcc.Dropdown(id='trend-type', options=[{'label': t, 'value': t} for t in df_additions['type'].dropna().unique()], placeholder="Choose Movie or TV Show", style={"width": "200px", "marginLeft": "10px"})
                ], style={"width": "70%", "margin": "auto", "display": "flex", "alignItems": "center", "justifyContent": "center", "gap": "20px", "paddingBottom": "20px"}),
                dcc.Graph(id='trend-line-chart')
            ], style={"padding": "20px"})
        ]),
        dcc.Tab(label='Director Popularity', children=[
            html.Div([
                html.H2("Top 10 Directors on Netflix", style={"textAlign": "center", "color": "black"}),
                html.Div([
                    html.Label("Filter by Type"),
                    dcc.Dropdown(id='director-type', options=[{'label': t, 'value': t} for t in df_dir['type'].dropna().unique()], placeholder="Choose Movie or TV Show", style={"width": "200px", "marginLeft": "10px"})
                ], style={"width": "50%", "margin": "auto", "display": "flex", "alignItems": "center", "justifyContent": "center", "paddingBottom": "20px"}),
                dcc.Graph(id='director-bar-chart')
            ], style={"padding": "20px"})
        ])
    ])
])

@app.callback(
    Output("detail-panel", "children"),
    Input("titles-table", "selected_rows"),
    State("titles-table", "data")
)
def display_title_details(selected_rows, rows):
    if not selected_rows:
        return html.Div()
    idx = selected_rows[0]
    row = rows[idx]
    return [
        html.H3(row.get("title", "No Title")),
        html.P([html.B("Type: "), row.get("type", "Unknown")], style={"marginBottom": "5px"}),
        html.P([html.B("Release Year: "), row.get("release_year", "Unknown")], style={"marginBottom": "5px"}),
        html.P([html.B("Rating: "), row.get("rating", "Unknown")], style={"marginBottom": "5px"}),
        html.P([html.B("Duration: "), row.get("duration", "Unknown")], style={"marginBottom": "5px"}),
        html.P([html.B("Genres: "), row.get("listed_in", "Unknown")], style={"marginBottom": "15px"}),
        html.Div([html.B("Description:"), html.P(row.get("description", ""), style={"whiteSpace": "pre-wrap"})], style={"paddingTop": "10px", "borderTop": "1px solid #ddd"})
    ]

@app.callback(
    Output('genre-bar-chart', 'figure'),
    Input('genre-date-range', 'start_date'),
    Input('genre-date-range', 'end_date'),
    Input('genre-type', 'value')
)
def update_genre_chart(start_date, end_date, content_type):
    filtered = df_genre.copy()
    if start_date:
        filtered = filtered[filtered['date_added_parsed'] >= pd.to_datetime(start_date)]
    if end_date:
        filtered = filtered[filtered['date_added_parsed'] <= pd.to_datetime(end_date)]
    if content_type:
        filtered = filtered[filtered['type'] == content_type]
    top_genres = filtered['genre'].value_counts().nlargest(10).reset_index()
    top_genres.columns = ['Genre', 'Count']
    colors = spongebob_colors[:len(top_genres)]
    fig = px.bar(top_genres, x='Count', y='Genre', orientation='h', title="Top Genres on Netflix", color='Genre', color_discrete_sequence=colors)
    fig.update_layout(yaxis=dict(title=None), xaxis_title="Count", title_font=dict(color="black", size=18), font=dict(color="black"), showlegend=False)
    return fig

@app.callback(
    Output('rating-pie-chart', 'figure'),
    Input('rating-year', 'value'),
    Input('rating-type', 'value')
)
def update_rating_chart(year_index, content_type):
    year = valid_years[year_index]
    filtered = df_ratings[df_ratings['release_year'] == year]
    if content_type:
        filtered = filtered[filtered['type'] == content_type]
    rating_counts = filtered['rating'].value_counts().reset_index()
    rating_counts.columns = ['Rating', 'Count']
    colors = spongebob_colors[:len(rating_counts)]
    fig = px.pie(rating_counts, names='Rating', values='Count', title=f"Rating Breakdown ({year})", color='Rating', color_discrete_sequence=colors)
    fig.update_layout(title_font=dict(color="black", size=18), font=dict(color="black"))
    return fig

@app.callback(
    Output('trend-line-chart', 'figure'),
    Input('trend-date-range', 'start_date'),
    Input('trend-date-range', 'end_date'),
    Input('trend-type', 'value')
)
def update_trend_chart(start_date, end_date, content_type):
    filtered = df_additions.copy()
    if start_date:
        filtered = filtered[filtered['year_month'] >= pd.to_datetime(start_date)]
    if end_date:
        filtered = filtered[filtered['year_month'] <= pd.to_datetime(end_date)]
    if content_type:
        filtered = filtered[filtered['type'] == content_type]
    monthly_counts = filtered.groupby('year_month').size().reset_index(name='Count')
    fig = px.line(monthly_counts, x='year_month', y='Count', title="Titles Added Per Month", markers=True)
    fig.update_layout(xaxis_title="Month", yaxis_title="Number of Titles", title_font=dict(color="black", size=18), font=dict(color="black"))
    return fig

@app.callback(
    Output('director-bar-chart', 'figure'),
    Input('director-type', 'value')
)
def update_director_chart(content_type):
    filtered = df_dir.copy()
    if content_type:
        filtered = filtered[filtered['type'] == content_type]
    director_counts = filtered['director_list'].value_counts().nlargest(10).reset_index()
    director_counts.columns = ['Director', 'Count']
    colors = spongebob_colors[:len(director_counts)]
    fig = px.bar(director_counts, x='Count', y='Director', orientation='h', title="Top 10 Directors on Netflix", color='Director', color_discrete_sequence=colors)
    fig.update_layout(yaxis=dict(title=None), xaxis_title="Count", title_font=dict(color="black", size=18), font=dict(color="black"), showlegend=False)
    return fig

if __name__ == "__main__":
    port = int(environ.get("PORT", 4000))
    app.run_server(host="0.0.0.0", port=port, debug=True)
