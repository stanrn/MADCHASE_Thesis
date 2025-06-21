import os
import datetime
import cairosvg
import shutil
import zipfile

image_folder = ""

"""
This module handles file system operations related to measurement storage and result processing
for the distributed channel sounding system.

Key functionalities:
- Creating structured folders for measurement data using timestamps and titles.
- Converting generated SVG plots into PNG format using CairoSVG.
- Organizing raw SVG and PNG files into subfolders for easy access and separation.
- Packaging all measurement results into a ZIP archive for download/export.
- Managing and returning the most recent image folder path for frontend access.
- Verifying file/folder permissions for robust error handling.

This utility module is used by the server backend to process and archive measurement results.
"""

# Making folders and returning path
def handle_files(measurement_name):
    # Create the top-level measurements folder if it doesn't exist
    measurements_folder = "measurements"
    os.makedirs(measurements_folder, exist_ok=True)

    # Create a parent folder for the measurements based on the measurement title
    series_folder = os.path.join(measurements_folder, measurement_name)
    os.makedirs(series_folder, exist_ok=True)

    # Get the absolute path for the series folder
    series_folder = os.path.abspath(series_folder)

    # Create a timestamped folder for the measurement
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamped_folder = os.path.join(series_folder, f"measurement_{timestamp}")
    os.makedirs(timestamped_folder, exist_ok=True)

    # Get the absolute path of the timestamped folder
    timestamped_folder = os.path.abspath(timestamped_folder)

    data_file_path = os.path.join(timestamped_folder, f"data_measurement_1.json")
    print(f"Data folder has been made: {data_file_path}")
    return data_file_path,timestamped_folder

# Converting svg file to png
def convert_svg_png(timestamped_folder):
    global image_folder
    # Get folder file paths
    svg_folder = os.path.join(timestamped_folder, 'svg')
    png_folder = os.path.join(timestamped_folder, 'png')
    image_folder = png_folder

    # Make folders for png's and svg's
    os.makedirs(svg_folder, exist_ok=True)
    os.makedirs(png_folder, exist_ok=True)
    # Converting SVG to PNG
    for filename in os.listdir(timestamped_folder):
        if filename.endswith('.svg'):
            svg_path = os.path.join(timestamped_folder, filename)
            png_filename = filename.replace('.svg', '.png')
            png_path = os.path.join(png_folder, png_filename)
            cairosvg.svg2png(url=svg_path, write_to=png_path)
            new_svg_path = os.path.join(svg_folder, filename)
            shutil.move(svg_path,new_svg_path)

# Making a zip file from the given folder path
def make_zip(path):
    output_path = os.path.join(path,'results.zip')
    # Making zip file to put the files in
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                
                # Skip the zip file itself
                if os.path.abspath(full_path) == os.path.abspath(output_path):
                    continue

                # Write file with relative path to preserve folder structure
                arcname = os.path.relpath(full_path, start=path)
                zipf.write(full_path, arcname)

# Retunr the image folder
def get_image_folder():
    global image_folder
    return image_folder

# Check permissions to a given folder
def check_permissions(file_path):
    try:
        # Check if the file/folder exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The path '{file_path}' does not exist.")

        # Check for read permission
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"Permission denied: Cannot read the file or folder '{file_path}'.")

        print(f"File '{file_path}' is accessible with read permission.")
        return True

    except FileNotFoundError as fnf_error:
        print(fnf_error)
        return False
    except PermissionError as perm_error:
        print(perm_error)
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False