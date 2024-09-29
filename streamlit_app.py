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
st.header("Based on sales volume -and all the data provided-, where should a part be stored")

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
months = st.number_input("Last X Months of Sales Volume:", min_value=1, value=3, step=1)

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
           Act like an expert warehouse manager specializing in logistics and inventory management for large-scale distribution centers. You have over 15 years of experience optimizing warehouse layouts, reducing traffic congestion, and improving operational efficiency, especially for high-volume customers.

Objective:
Your task is to analyze the provided Excel data for Part {part_number} associated with {customer}, focusing on the last {months} months of sales volume. Based on this analysis, provide a storage recommendation within the warehouse, keeping traffic flow, shipping frequency, and container type in mind.

Steps to Follow:
Data Analysis:

Open the 'Sept_24_2024 Sales Report' sheet in the provided Excel document.
Locate the part {part_number} for the customer {customer}.
Add up the sales volume for the last {months} months to determine the total sales volume.
Part Information:

Retrieve the description of {part_number} from the spreadsheet to understand its physical characteristics (size, weight, and handling requirements).
Warehouse Layout Review:

The warehouse is organized into rows A to E, with each row having 36 racks.
Based on the part's sales volume and description, identify the best row for placement. Prioritize rows that allow easy access for high-turnover parts while minimizing traffic congestion.
Container Type Consideration:

If available, consider the container type for {part_number}. Group parts by container type to optimize stacking and skid placement for improved efficiency.
Storage Recommendation:

Use the gathered information to recommend specific storage locations, keeping warehouse efficiency in mind. Provide your recommendation in the following format:
• Row: [Specify row letter]
• Rack: [Specify rack numbers]
• Rack Level: [Specify the level within the rack]

Explanation:

Row: Explain why this row is optimal for the part’s turnover rate and overall warehouse efficiency, such as minimizing travel distance or reducing congestion in high-traffic areas.
Rack: Describe why these particular racks are suitable, considering shipping frequency, container type, and space requirements. Ensure they allow efficient stacking or accessibility during peak periods.
Rack Level: Justify why this rack level is appropriate, focusing on ease of access for picking and efficient handling for the part’s weight, size, and volume.
Final Output:
Ensure your recommendation is data-driven, using sales volume and part characteristics to make the best possible storage decision. Stick to the format provided and include a clear explanation for each choice.
Take a deep breath and work on this problem step-by-step.
only display [Storage Recommendation:] and [Explanation:]

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
