import streamlit as st
import pandas as pd
import plotly.express as px

# Title
st.title("🏅 My First Streamlit App")

# Text
st.write("Welcome to Streamlit! Let's explore some simple interactivity.")

# Sidebar input
st.sidebar.header("Filters")
name = st.sidebar.text_input("Enter your name", "Guest")

# Display a greeting
st.write(f"Hello, {name}! 👋")

# Slider
age = st.slider("Select your age", 0, 100, 25)
st.write(f"Your age is: {age}")

# Checkbox
show_data = st.checkbox("Show sample data?")
if show_data:
    df = pd.DataFrame({
        "Fruit": ["Apple", "Banana", "Cherry", "Date"],
        "Count": [10, 20, 15, 7]
    })
    st.dataframe(df)

    # Plot
    fig = px.bar(df, x="Fruit", y="Count", color="Fruit", title="Fruit Count")
    st.plotly_chart(fig)

# Button
if st.button("Click me"):
    st.success("You clicked the button! 🎉")
