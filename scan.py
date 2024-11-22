import os
import chardet
import shutil
import threading
import re

# Function to read files and detect encoding
def read_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
        with open(file_path, 'r', encoding=encoding, errors='ignore') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

# Function to generate a new file name with a serial number
def get_unique_filename(destination_folder, file_name):
    base_name, extension = os.path.splitext(file_name)
    counter = 1
    new_file_name = f"{base_name}{extension}"
    while os.path.exists(os.path.join(destination_folder, new_file_name)):
        new_file_name = f"{base_name}_{counter}{extension}"
        counter += 1
    return new_file_name

# Function to search within the content and extract specific information like URL, USER, PASS
def extract_information(content, keywords):
    extracted_data = []
    for keyword in keywords:
        if keyword.lower() in content.lower():
            # Using regular expressions to extract URL, USER, PASS
            urls = re.findall(r'(https?://[^\s]+)', content)
            users = re.findall(r'USER:\s*([^\s]+)', content)
            passwords = re.findall(r'PASS:\s*([^\s]+)', content)
            
            extracted_data.extend([(url, user, password) for url, user, password in zip(urls, users, passwords)])
    
    return extracted_data

# Function to search in files within folders
def search_in_file(file_path, search_terms, min_matches, output_file, destination_folder, successful_file):
    content = read_file(file_path)
    if content:
        extracted_data = extract_information(content, search_terms)
        if len(extracted_data) >= min_matches:
            # Writing results to the report (results.csv)
            with open(output_file, 'a', encoding='utf-8') as report:
                report.write(f"File Path: {file_path}\n")
                for data in extracted_data:
                    report.write(f"URL: {data[0]}, USER: {data[1]}, PASS: {data[2]}\n")
                report.write("\n")
            
            # Writing results to the successful file (i_successful.txt)
            with open(successful_file, 'a', encoding='utf-8') as success_report:
                success_report.write(f"File Path: {file_path}\n")
                for data in extracted_data:
                    success_report.write(f"URL: {data[0]}, USER: {data[1]}, PASS: {data[2]}\n")
                success_report.write("\n")
            
            # Copying the file to the destination folder with a new name if it's duplicated
            try:
                if not os.path.exists(destination_folder):
                    os.makedirs(destination_folder)
                
                file_name = os.path.basename(file_path)
                new_file_name = get_unique_filename(destination_folder, file_name)
                
                shutil.copy(file_path, os.path.join(destination_folder, new_file_name))
            except Exception as e:
                print(f"Error copying file {file_path}: {e}")

# Function to search through all files in subfolders
def search_files_in_folders(directory, search_terms, min_matches=1, output_file='results.csv', destination_folder='Filtered_Files', successful_file='i_successful.txt'):
    # Write header in the report when starting the search
    with open(output_file, 'w', encoding='utf-8') as report:
        report.write("File Path, URL, USER, PASS\n")
    
    # Create or clear the content of the i_successful.txt file
    with open(successful_file, 'w', encoding='utf-8') as success_report:
        success_report.write("Search Results:\n\n")

    threads = []
    
    # Traverse through all folders and files
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == "All Passwords.txt":  # Filter target files
                file_path = os.path.join(root, file)
                thread = threading.Thread(target=search_in_file, args=(file_path, search_terms, min_matches, output_file, destination_folder, successful_file))
                threads.append(thread)
                thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    print(f"Results saved in {output_file}")
    print(f"Successful results saved in {successful_file}")
    print(f"Copied matching files to the folder: {destination_folder}")

# Running the script
if __name__ == "__main__":
    # Set values directly
    directory = r"C:/Users/HP/Downloads/Telegram Desktop/00"  # Directory path
    min_matches = 1  # Minimum matches
    output_file = "results.csv"  # Report file name
    destination_folder = "Filtered_Files"  # Folder name to store filtered files
    successful_file = "i_successful.txt"  # Successful file name

    # Keywords to search
    search_terms = ["shodan", "wp-login.php", "potal", "admin"]  # Keywords to search in files

    # Call the main function
    search_files_in_folders(directory, search_terms, min_matches, output_file, destination_folder, successful_file)
