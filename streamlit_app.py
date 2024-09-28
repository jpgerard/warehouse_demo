import streamlit as st
import pandas as pd
from openai import OpenAI

# Set your OpenAI API key directly (replace with your actual key)
client = OpenAI(
    # This is the default and can be omitted
    api_key = "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"

# Title of the Streamlit app
st.title("Warehouse Management Assistant")

# Step 1: Excel File Uploader
uploaded_files = st.file_uploader("Upload Excel files", type=["xlsx"], accept_multiple_files=True)

# Step 2: Text Input Fields for Parameters
part_number = st.text_input("Enter Part Number:")
customer = st.text_input("Enter Customer Name:")
months = st.text_input("Enter Number of Months of Shipping Volume:", value="6")

# Display the dynamic prompt being generated
prompt_template = (
    "Based on all the data provided, where should part <{part}> belonging to <{customer}> be stored "
    "based on the last <{months}> months of shipping volume? "
)
full_prompt = prompt_template.format(part=part_number, customer=customer, months=months)
st.write(f"Generated Prompt: {full_prompt}")

# Step 3: Submit Button to trigger the OpenAI API call
if st.button("Submit"):
    # Check if files are uploaded and inputs are provided
    if not uploaded_files or not part_number or not customer or not months:
        st.error("Please upload the Excel files and fill in all input fields before submitting.")
    else:
        try:
            # Step 4: Process the uploaded Excel files (you can read and analyze the data here)
            excel_data = []
            for file in uploaded_files:
                df = pd.read_excel(file)
                excel_data.append(df)
            # Combine the Excel data if needed or perform some initial analysis
            combined_data = pd.concat(excel_data, ignore_index=True)
            
            # Step 5: Format the prompt with user data and predefined instructions
            system_message = (
                f"We want to layout by the top customers based on volume. "
                f"Keep these top customers separated in separate areas, this will prevent traffic congestion in the warehouse. "
                f"Layout by container type, keeping the same containers together so they stack better on skids. "
                f"In the current layout, the warehouse is divided into rows (A to E), with each row having 36 racks. "
                f"Use all the data provided, to determine where Part {part_number} belonging to {customer} should be stored "
                f"based on the last {months} months of shipping volume."
            )
            
            # Step 6: Make the OpenAI API request using ChatCompletion
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use the correct model, e.g., 'gpt-3.5-turbo' or 'gpt-4'
                messages=[
                    {"role": "system", "content": "You are a warehouse management assistant."},
                    {"role": "user", "content": system_message}
                ],
                max_tokens=500  # Set appropriate token limits
            )
            
            # Step 7: Display the formatted response
            api_response = response['choices'][0]['message']['content']
            st.subheader("API Response:")
            st.write(api_response)
        except Exception as e:
            # Handle errors such as API connection issues
            st.error(f"An error occurred: {str(e)}")

# Step 8: Instructions for deployment
st.info("This app can be deployed on Streamlit Cloud or any other hosting service. "
        "Make sure to set the OPENAI_API_KEY in your environment for secure API access.")
