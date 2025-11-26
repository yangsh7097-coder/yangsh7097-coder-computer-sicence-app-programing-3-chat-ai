import streamlit as st
import pandas as pd
import numpy as np

st.title('My First Streamlit App')

st.write(pd.DataFrame({'name': ['Alice', 'Bob', 'Charlie', 'David'], 'age': [25, 30, 35, 40]}))

df = pd.DataFrame(np.random.randn(500, 2) / [10, 10], columns=['a', 'b'])

st.line_chart(df)

st.markdown(
    """
    This is a playgroud for you to try Streamlit and had fun.
    **There's :rainbow[so much] you can buulid!**

    We prepared a few examples to get you started. Just
    click on the buttons above and discover what you can do with Streamlit.
    """)

if st.button("Send balloon!"):
    st.balloons()