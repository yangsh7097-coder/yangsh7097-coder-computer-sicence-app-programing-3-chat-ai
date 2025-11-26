import streamlit as st
import pandas as pd
import numpy as np

st.write("My streamlit supports a wide range of data visualizations, including [plotly](https://plotly.com/python)")


all_users = ["Alice", "Bob", "Charlie"]
with st.container(border=True):
    users = st.multiselect("Users", all_users, default=all_users)
    rolling_average = st.toggle("Rolling average")

np.random.seed(42)
data = pd.DataFrame(np.random.randn(20, len(users)), columns=users)

if rolling_average:
    data = data.rolling(7).mean().dropna()

tab1, tab2 = st.tabs(["Chart", "Dataframe"])
tab1.line_chart(data, height=250)
tab2.dataframe(data, height=250, use_container_width=True)

st.write("Got lots of data? Great! Streamlit can show [dataframes](https://docs.streamlit.io/library/api-reference/data/Dataframe)")
num_rows = st.slider("Number of rows", 1, 10000, 500)

np.random.seed(42)
table_data = []
for i in range(num_rows):
    table_data.append(
        {
            "Preview": f"https://picsum.photos/400/200?lock={i}",
            "Views": np.random.randint(0, 1000),
            "Active": np.random.choice([True, False]),
            "Category": np.random.choice(["🎂LLM", "📊DATA", "⚙️Tool"]),
            "Progress": np.random.randint(1, 100),
        }
    )
table_data = pd.DataFrame(table_data)

config = {
    "Preview": st.column_config.ImageColumn(),
    "Progress": st.column_config.ProgressColumn(),
}

if st.toggle("Enable editing"):
    edited_data = st.data_editor(table_data, column_config=config, use_container_width=True)
else:
    st.dataframe(table_data, column_config=config, use_container_width=True)