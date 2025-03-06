import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

# Connect to SQLite database
conn = sqlite3.connect('department.db')

# Load tables into Pandas DataFrames
df_programs = pd.read_sql_query("SELECT * FROM Programs", conn)
df_terms = pd.read_sql_query("SELECT * FROM Terms", conn)
df_enrollments = pd.read_sql_query("SELECT * FROM Enrollments", conn)
df_students = pd.read_sql_query("SELECT * FROM Students", conn)

# Close connection
conn.close()

# Merge enrollments with programs, terms, and students
df_enrollment_students = df_enrollments.merge(df_students, on='student_id', how='left')
df_enrollment_students = df_enrollment_students.merge(df_terms, on='term_id', how='left')
df_enrollment_students = df_enrollment_students.merge(df_programs, on='program_id', how='left')

# Aggregate enrollments by term and program
enrollment_trends = df_enrollment_students.groupby(['term_name', 'program_name']).size().reset_index(name='enrollments')

# Streamlit UI for Enrollment Trends
st.title("Enrollment Trends by Program")

# Program selection
distinct_programs = enrollment_trends['program_name'].unique()
selected_programs = st.multiselect("Select Programs", distinct_programs, default=distinct_programs[:2])

# Filter data
df_filtered = enrollment_trends[enrollment_trends['program_name'].isin(selected_programs)]

# Plot enrollment trends
fig = px.line(df_filtered, x='term_name', y='enrollments', color='program_name', markers=True,
              title="Enrollment Trends Over Time by Program",
              labels={'term_name': "Term and Year", 'enrollments': "Enrollment", 'program_name': "Program Name"})
st.plotly_chart(fig)

# Streamlit UI for Financial Aid Distribution
st.subheader("Financial Aid Distribution Among Enrolled Students")

# Program selection with unique key
selected_program_fa = st.selectbox("Select Program", df_programs['program_name'].unique(), key="fa_program")

# Gender selection with unique key
selected_gender = st.selectbox("Select Gender", df_students['gender'].unique(), key="fa_gender")

# Filter data based on selection and create a copy to avoid warnings
df_filtered_fa = df_enrollment_students[
    (df_enrollment_students['program_name'] == selected_program_fa) &
    (df_enrollment_students['gender'] == selected_gender)
].copy()  # ✅ Make an explicit copy to prevent SettingWithCopyWarning

# Convert enrollment_date to year safely
df_filtered_fa.loc[:, 'enrollment_year'] = pd.to_datetime(df_filtered_fa['enrollment_date']).dt.year

# Aggregate financial aid data by year
financial_aid_summary = df_filtered_fa.groupby(['enrollment_year', 'Financial_Aid']).size().reset_index(name='count')

# Create a bar chart
fig_fa = px.bar(financial_aid_summary, x='enrollment_year', y='count', color='Financial_Aid',
                title=f"Financial Aid Trends for {selected_program_fa} ({selected_gender}) Over the Years",
                labels={'enrollment_year': "Year", 'count': "Number of Students", 'Financial_Aid': "Financial Aid Status"},
                barmode='group')

# Display the chart
st.plotly_chart(fig_fa)

# Streamlit UI for Gender Enrollment Breakdown
st.subheader("Enrollment Breakdown by Gender")

# Program selection
selected_program_gender = st.selectbox("Select Program", df_programs['program_name'].unique(), key="gender_program")

# Term selection
selected_term_gender = st.selectbox("Select Term", df_terms['term_name'].unique(), key="gender_term")

# Filter data based on user selections
df_filtered_gender = df_enrollment_students[
    (df_enrollment_students['program_name'] == selected_program_gender) &
    (df_enrollment_students['term_name'] == selected_term_gender)
].copy()

# Count gender distribution
gender_distribution = df_filtered_gender['gender'].value_counts().reset_index()
gender_distribution.columns = ['Gender', 'Count']

# Create a Pie Chart with red colors
fig_gender_pie = px.pie(
    gender_distribution, 
    values='Count', 
    names='Gender', 
    title=f"Enrollment Breakdown by Gender for {selected_program_gender} in {selected_term_gender}",
    hole=0.4,
    color_discrete_map={"Male": "#D62728", "Female": "#FF5733"}  # Shades of red
)

# Show the chart
st.plotly_chart(fig_gender_pie)
