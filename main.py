# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import calendar  # Import calendar to get month names

app = Dash()

# Load the data
df = pd.read_csv('./output/converted/converted.csv')

# Convert the 'Date' column to datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Extract the year, month, week, and day name from the 'Date' column
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Week'] = df['Date'].dt.isocalendar().week  # ISO week number
df['Day'] = df['Date'].dt.day_name()  # Day name (e.g., "Monday")

# Create a new column that associates the day of the week with the day of the month in the format "Dayname, Day"
df['Day_of_Month_Week'] = df['Day'] + ", " + df['Date'].dt.day.astype(str)

# Create a dictionary to hold figures for each year
yearly_figures = {}
for year in df['Year'].unique():  # Loop through unique years
    filtered_df = df[df['Year'] == year]
    monthly_figures = {}
    for month in range(1, 13):  # Loop through months 1 to 12
        month_df = filtered_df[filtered_df['Month'] == month]
        if not month_df.empty:  # Only create plots if data exists for the month
            weekly_figures = {}
            for week in month_df['Week'].unique():  # Loop through unique weeks
                week_df = month_df[month_df['Week'] == week]
                if not week_df.empty:  # Only create a plot if data exists for the week
                    # Update the grouping and sorting logic to reflect the new format
                    df_grouped = week_df.groupby(['Day_of_Month_Week', 'Region'], as_index=False).sum(numeric_only=True)
                    # Sort by the day of the week and day of the month
                    df_grouped['Day_of_Month_Week'] = pd.Categorical(
                        df_grouped['Day_of_Month_Week'],
                        categories=[
                            f"{day_name}, {day}" for day_name in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                            for day in range(1, 32)  # Assuming up to 31 days in a month
                        ],
                        ordered=True
                    )
                    df_grouped = df_grouped.sort_values('Day_of_Month_Week')
                    month_name = calendar.month_name[month]  # Get the month name
                    fig = px.line(df_grouped, x="Day_of_Month_Week", y="Sales", color="Region", markers=True,
                                  title=f"Sales for {month_name} {year}, Week {week}", line_shape='spline')
                    weekly_figures[f"Week {week}"] = fig
            monthly_figures[calendar.month_name[month]] = weekly_figures
    yearly_figures[year] = monthly_figures

# Create tabs for each year's plot
app.layout = html.Div(children=[
    html.H1(children='Pink Morsel Sales'),
    html.H3(children='Weekly Sales by Year and Month'),

    dcc.Tabs(id="tabs", children=[
        dcc.Tab(label=f"Year {year}", children=[
            dcc.Tabs(id=f"tabs-year-{year}", children=[
                dcc.Tab(label=f"{month}", children=[
                    dcc.Tabs(id=f"tabs-year-{year}-month-{month}", children=[
                        dcc.Tab(label=f"{week}", children=[
                            dcc.Graph(
                                id=f"graph-year-{year}-month-{month}-week-{week}",
                                figure=yearly_figures[year][month][week]
                            )
                        ]) for week in yearly_figures[year][month].keys()  # Create a tab for each week
                    ])
                ]) for month in yearly_figures[year].keys()  # Create a tab for each month
            ])
        ]) for year in yearly_figures.keys()  # Create a tab for each year
    ])
])

if __name__ == '__main__':
    app.run(debug=True)
