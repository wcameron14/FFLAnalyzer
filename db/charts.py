from draft_analysis import get_snake_value_data, get_auction_value_data, analyze_auction_draft, analyze_snake_draft, get_draft_type
from visualization import plot_snake_value, plot_auction_value
import app.database.queries as db
import pandas as pd

conn, cur = db.connect_to_db()

# Get the draft type
draft_type = get_draft_type(conn)

df, owners = get_snake_value_data(conn)
result = analyze_snake_draft(df, owners)


if draft_type == 1:
    print("Entering auction block")
    df = get_auction_value_data(conn)
    print(df)
    result = analyze_auction_draft(df)
    print(result)
    #Plot the results
    plot_auction_value(result)
elif draft_type == 2:
    print("Entering snake block")
    df = get_snake_value_data(conn)
    print(df)
    result = analyze_snake_draft(df, owners)
    print(result)
    # Plot the results
    plot_snake_value(result)
