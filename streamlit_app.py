import streamlit as st
import pandas as pd
from openai import OpenAI
from PIL import Image

# Fetch the OpenAI API key from Streamlit secrets
api_key = st.secrets["openai"]["api_key"]

# Initialize the OpenAI client using the API key from Streamlit secrets
client = OpenAI(api_key=api_key)

# LOGO
st.info("MULTIFACTOR AI - for NIFCO")

# Title of the Streamlit app
st.title("Warehouse Management Assistant")
st.header("Based on shipping volume -and all the data provided-, where should a part be stored")

# Load and display the image (if available)
# image = Image.open("warehouse_image.jpg")  # Uncomment if using an image
# st.image(image, caption="Warehouse Management", use_column_width=True)

# Initialize session state for storing combined Excel data
if "combined_data" not in st.session_state:
    st.session_state.combined_data = None  # Initialize it to None

# Step 1: Excel File Uploader
uploaded_files = st.file_uploader("Upload Excel files", type=["xlsx"], accept_multiple_files=True)

# Step 2: Text Input Fields for Parameters
part_number = st.text_input("Enter Part Number:")
customer = st.text_input("Enter Customer Name:")
months = st.number_input("Enter Number of Months of Shipping Volume:", min_value=1, value=3, step=1)

# Step 3: Submit Button to trigger the OpenAI API call
if st.button("Submit"):
    if not uploaded_files or not part_number or not customer:
        st.error("Please upload the Excel files and fill in all input fields before submitting.")
    else:
        try:
            # Process the uploaded Excel files
            excel_data = []
            for file in uploaded_files:
                df = pd.read_excel(file)
                excel_data.append(df)
            combined_data = pd.concat(excel_data, ignore_index=True)

            # Step 5: Format the prompt with user data and predefined instructions
            system_message = f"""
            Analyze the provided Excel data for Part {part_number} belonging to {customer}, focusing on the last {months} months of shipping volume. 
            Consider the following warehouse layout and guidelines:
            - The warehouse is divided into rows (A to E), with each row having 36 racks.
            - Layout should be organized by top customers based on volume, keeping them separated to prevent traffic congestion.
            - Parts should be grouped by container type for better stacking on skids.
            
            Based on this analysis, provide a storage recommendation in the following format:
            Shipping volume for {customer}
            •   Row: [Specify row letter]
            
            •   Rack: [Specify rack numbers]
            
            •   Rack Level: [Specify the level within the rack]

            [Explain breifly why this row is suitable for the part's turnover rate and warehouse efficiency]
            [Explain breifly why these racks are appropriate based on shipping frequency and space requirements]
            [Explain breifly why this level is suitable for accessibility and efficient picking]

            Ensure your response is data-driven and follows this exact structure, providing specific recommendations and explanations for each point after displaying the short answer.
            """


            # Step 6: Make the OpenAI API request
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Make sure to use a valid model
                messages=[
                    {"role": "system", "content": "You are a warehouse layout optimization assistant."},
                    {"role": "user", "content": system_message},
                ]
            )

            # Step 7: Display the formatted response
            api_response = response.choices[0].message.content
            st.subheader("Part Location Answer:")
            st.write(api_response)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Add a chat box at the bottom for additional questions
st.subheader("Ask additional questions about the data")

"""
# Chat box input
additional_question = st.text_input("Ask additional questions about the data:")

# Submit button for the chat box
if st.button("Submit Question"):
    if additional_question:
        try:
            # Check if Excel data is available
            if st.session_state.combined_data is not None:
                # Include a summary of the Excel data in the prompt for the chat question
                excel_summary = st.session_state.combined_data.head().to_string()  # You can summarize or clean the data as necessary

                # Format the prompt for the chat question including the Excel data summary
                system_message_chat = f"""
                You are provided with the following warehouse data and asked to help with warehouse management:

                {excel_summary}

                Now answer the following question:
                {additional_question}
                """    
            # Format the prompt for the chat question
            chat_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a warehouse management assistant."},
                    {"role": "user", "content": additional_question}
                ],
                max_tokens=500
            )
            
            # Display the response from the chat box
            chat_api_response = chat_response.choices[0].message.content
            st.subheader("Response to Your Question:")
            st.write(chat_api_response)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.error("Please ask a question before submitting.") 
"""
