import streamlit as st
import pandas as pd
from openai import OpenAI

# Fetch the OpenAI API key from Streamlit secrets
api_key = st.secrets["openai"]["api_key"]

# Initialize the OpenAI client using the API key from Streamlit secrets
client = OpenAI(api_key=api_key)

# LOGO and Title
st.info("MULTIFACTOR AI - for NIFCO")
st.title("Warehouse Management Assistant")
st.header("Based on sales volume and provided data, where should a part be stored?")

# Step 1: Excel File Uploader
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file is not None:
    # Read the Excel file
    df = pd.read_excel(uploaded_file)
    
    # Display column names to the user
    st.write("Columns found in the Excel file:")
    st.write(", ".join(df.columns))

    # Step 2: Let user select relevant columns
    part_number_col = st.selectbox("Select the column for Part Number:", options=[''] + list(df.columns))
    customer_col = st.selectbox("Select the column for Customer:", options=[''] + list(df.columns))
    description_col = st.selectbox("Select the column for Part Description (optional):", options=['None'] + list(df.columns))
    
    # Let user select multiple columns for sales data
    sales_cols = st.multiselect("Select the columns for Sales Data:", options=list(df.columns))

    # Step 3: Text Input Fields for Parameters
    part_number = st.text_input("Enter Part Number:")
    customer = st.text_input("Enter Customer Name:")
    
    # Only show the number input if sales columns are selected
    if sales_cols:
        months = st.number_input("Number of recent columns to consider for sales volume:", 
                                 min_value=1, 
                                 max_value=len(sales_cols),
                                 value=min(3, len(sales_cols)))  # Default to 3 or the number of columns if less
    else:
        st.warning("Please select sales data columns to proceed.")
        months = 0

    # Step 4: Submit Button to trigger the OpenAI API call
    if st.button("Submit"):
        if not part_number_col or not customer_col or not sales_cols or not part_number or not customer:
            st.error("Please select all required columns and fill in all input fields before submitting.")
        else:
            try:
                # Filter data for the specific part number and customer
                filtered_df = df[(df[part_number_col] == part_number) & (df[customer_col] == customer)]
                
                if filtered_df.empty:
                    st.error(f"No data found for Part Number {part_number} and Customer {customer}")
                else:
                    # Calculate total sales volume for the specified number of columns
                    recent_sales = sales_cols[-months:]
                    total_sales = filtered_df[recent_sales].sum().sum()
                    
                    # Get part description
                    part_description = filtered_df[description_col].iloc[0] if description_col != 'None' else "Description not available"
                    
                    # Prepare data for the API request
                    data_summary = f"""
                    Part Number: {part_number}
                    Customer: {customer}
                    Description: {part_description}
                    Total Sales Volume (Last {months} columns): {total_sales}
                    """
                    
                    # Format the prompt with user data and predefined instructions
                    system_message = f"""
                    Act like an expert warehouse manager specializing in logistics and inventory management for large-scale distribution centers. You have over 15 years of experience optimizing warehouse layouts, reducing traffic congestion, and improving operational efficiency, especially for high-volume customers.

                    Objective:
                    Your task is to analyze the provided data for Part {part_number} associated with {customer}, focusing on the last {months} columns of sales volume. Based on this analysis, provide a storage recommendation within the warehouse, keeping traffic flow, shipping frequency, and container type in mind.

                    Data Summary:
                    {data_summary}

                    Warehouse Layout:
                    - The warehouse is organized into rows A to E, with each row having 36 racks.
                    - Based on the part's sales volume and description, identify the best row for placement.
                    - Prioritize rows that allow easy access for high-turnover parts while minimizing traffic congestion.

                    Storage Recommendation:
                    Provide your recommendation in the following format:
                    • Row: [Specify row letter]
                    • Rack: [Specify rack numbers]
                    • Rack Level: [Specify the level within the rack]

                    Explanation:
                    - Row: Explain why this row is optimal for the part's turnover rate and overall warehouse efficiency.
                    - Rack: Describe why these particular racks are suitable, considering shipping frequency and space requirements.
                    - Rack Level: Justify why this rack level is appropriate, focusing on ease of access for picking and efficient handling.

                    Final Output:
                    Ensure your recommendation is data-driven, using the provided sales volume and part characteristics to make the best possible storage decision. Stick to the format provided and include a clear explanation for each choice.
                    Only display [Storage Recommendation:] and [Explanation:]
                    """

                    # Make the OpenAI API request
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a warehouse layout optimization assistant."},
                            {"role": "user", "content": system_message},
                        ]
                    )

                    # Display the formatted response
                    api_response = response.choices[0].message.content
                    st.subheader("Part Location Answer:")
                    st.write(api_response)
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error("Please check your inputs and try again.")
else:
    st.warning("Please upload an Excel file to proceed.")
