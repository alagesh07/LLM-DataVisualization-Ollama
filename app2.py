import pandas as pd
import ollama
import re
import subprocess

# Function to interact with the model and save responses
def interact_with_model(prompt, output_file, dataset_name):
    # Stream the response from the model
    stream = ollama.chat(
        model='llama3',
        messages=[{'role': 'user', 'content': prompt}],
        stream=True
    )

    # Initialize variable to store model's response
    response = ""
    for chunk in stream:
        response += chunk['message']['content']
        print(chunk['message']['content'], end='', flush=True)

    # Patterns to match Python code in Markdown format
    python_code_pattern_specific = r"```Python\s*(.*?)\s*```"  # Specific for Python code
    python_code_pattern_specific1 = r"```python\s*(.*?)\s*```"  # Specific for Python code
    python_code_pattern_general = r"```\s*(.*?)\s*```"         # General for any code

    # Try to match specific pattern first
    match = re.search(python_code_pattern_specific, response, re.DOTALL)
    if not match:  # If no match, try the general pattern
        match = re.search(python_code_pattern_general, response, re.DOTALL)
    if not match:  # If no match, try the general pattern
        match = re.search(python_code_pattern_specific1, response, re.DOTALL)

    if match:
        python_code = match.group(1).strip()
    else:
        python_code = "# No valid Python code found in the response."

    # Add import statements and dataset information
    imports_and_data_info = f"""\
# Dataset used: {dataset_name}

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

"""

    # Combine imports and dataset information with the extracted code
    final_python_code = imports_and_data_info + python_code

    # Save the final Python code to the specified file
    with open(output_file, 'w') as file:
        file.write(final_python_code + '\n\n')

    print(f"\nPython code extracted from the query saved to '{output_file}'")
    return output_file

# Function to load CSV files with error handling
def load_csv_with_error_handling(file_path):
    try:
        return pd.read_csv(file_path)
    except pd.errors.ParserError as e:
        print(f"Error parsing {file_path}: {e}")
        # Attempt to load with different options
        try:
            return pd.read_csv(file_path, error_bad_lines=False, warn_bad_lines=True)
        except pd.errors.ParserError as e:
            print(f"Error parsing {file_path} with fallback options: {e}")
            return pd.DataFrame()  # Return an empty DataFrame if parsing fails

# Load and merge data from three CSV files
df1 = load_csv_with_error_handling("data1.csv")
df2 = load_csv_with_error_handling("data2.csv")
df3 = load_csv_with_error_handling("data3.csv")
merged_df = pd.concat([df1, df2, df3], ignore_index=True)

# Save the merged DataFrame to a new CSV file
merged_df.to_csv("merged_data.csv", index=False)

# User query
user_query = input("Please enter your query: ")

# Determine the nature of the query
if "chart" in user_query.lower() or "plot" in user_query.lower() or "graph" in user_query.lower():
    task_type = "chart preparation"
else:
    task_type = "answer only"

# Prepare the prompt for the model
if task_type == "chart preparation":
    prompt = f"Analyze the uploaded merged_data.csv file and generate Python code to prepare the appropriate chart based on the user query. Here is the data set: 'merged_data.csv'.\n{merged_df}\n\nUser query: {user_query}\n\n"
    
    # Define file path to save the Python code output
    output_python_file = "output_code.py"

    # Call function to interact with the model and save extracted Python code response
    output_file_path = interact_with_model(prompt, output_python_file, "merged_data.csv")

    # Function to execute Python file
    def execute_python_file(file_path, retries=3):
        for attempt in range(retries):
            try:
                result = subprocess.run(['python', file_path], capture_output=True, text=True, check=True)
                print("\nOutput of executed Python file:")
                print(result.stdout)
                break  # Exit the loop if the execution is successful
            except subprocess.CalledProcessError as e:
                print(f"\nError executing Python file (Attempt {attempt + 1}/{retries}): {e}")
                if attempt == retries - 1:
                    print("Maximum retry limit reached. Execution failed.")

    # Automatically execute saved Python code
    print("\nExecuting saved Python code...\n")
    execute_python_file(output_file_path)

else:
    prompt = f"Analyze the uploaded merged_data.csv file and provide a direct answer to the user query without any comments or extra statements. Here is the data set: 'merged_data.csv'.\n{merged_df}\n\nUser query: {user_query}\n\n"

    # Define file path to save the Python code output
    output_python_file = "output_code.py"

    # Call function to interact with the model and save extracted Python code response
    output_file_path = interact_with_model(prompt, output_python_file, "merged_data.csv")

    # Function to execute Python file
    def execute_python_file(file_path, retries=3):
        for attempt in range(retries):
            try:
                result = subprocess.run(['python', file_path], capture_output=True, text=True, check=True)
                print(result.stdout)
                break  # Exit the loop if the execution is successful
            except subprocess.CalledProcessError as e:
                print(f"\nError executing Python file (Attempt {attempt + 1}/{retries}): {e}")
                if attempt == retries - 1:
                    print("Maximum retry limit reached. Execution failed.")
