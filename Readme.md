# Leads Dashboard
Leads Dashboard is a streamlit app that provides various analytics on registered leads in Germany. It offers visual insights into key metrics such as lead source, conversion rate, and geographical distribution, helping businesses track and manage their leads more effectively.

## Prerequisites
**Python 3.12 is required.** Make sure you have Python 3.12 installed on your system. You can download and install it from the official [Python website](https://www.python.org/downloads/).

### Setup and Installation

1. Navigate to the project directory: After extracting the files, open your terminal and move into the project directory:
    ```shell
    cd Leads-Dashboard/
    ```
2. (Optional) Create a virtual environment: It is recommended to use a virtual environment for project isolation.
    ```shell
    # For Linux/macOS
    python3 -m venv venv
    source venv/bin/activate
    
    # For Windows
    python -m venv venv
    venv\Scripts\activate
   ```
3. Once the virtual environment is activated, install the required Python packages by running:
    ```shell
    pip install -r requirements.txt
    ```
4. Configure Google Sheets as a Data Source: Follow these steps to set it up:
    - Follow the instructions in the [Streamlit Guide for Google Sheets Integration](https://docs.streamlit.io/develop/tutorials/databases/private-gsheet).
    - After completing the setup and obtaining the credentials, update the `secrets.toml` file located in the `.streamlit/` folder with your Google Sheets credentials:
      ```shell
      [connections.gsheets]
      ... <keys params from json file obtained from GCP>
      ```
6. Run the app:
    ```shell
    streamlit run app.py
    ```

---
