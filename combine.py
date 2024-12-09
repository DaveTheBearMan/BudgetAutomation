import os
import time
import csv
from pypdf import PdfWriter, PdfReader
import pypdftk
# Create a pdf to write too

# Define directories
FLATTENED_DIR = "/Flattened"
FORMS_DIR = "/Forms"
IMAGES_DIR = "/Receipts"
SEPARATE_DIR = "/Separate"

# Define PNC code order list
OLD_PNC_CODE_ORDER = [
    "",
]

# Initialize variables
pnc_code_order = []
who_is = []
dates = []
missing_files = []

# Helper function to read CSV and populate lists
def load_csv_data(file_path):
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            pnc_code_order.append(row[2])
            who_is.append(row[3])
            dates.append(row[1])

# Helper function to check if files exist in directories
def check_file_existence(pdf_file_name, image_file_cache, receipt_file_cache):
    if pdf_file_name not in image_file_cache or pdf_file_name not in receipt_file_cache:
        return False
    return True

def check_file_image_existence(pdf_file_name, image_file_cache, receipt_File_cache):
    if (f'{pdf_file_name.split(".")[0]}.png' in image_file_cache or f'{pdf_file_name.split(".")[0]}.jpg' in image_file_cache) and pdf_file_name in receipt_file_cache:
        return True
    return False

enabled = False
def printif(*args):
    if enabled:
        print(args)

def resize_pdf_to_a4(input_pdf_path, output_pdf_path):
    # A4 size in points (8.27 x 11.69 inches)
    a4_width, a4_height = 595, 842

    # Read the original PDF
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # Iterate through all pages and resize them to A4, maintaining aspect ratio
    for page in reader.pages:
        # Get the current page dimensions
        page_width = float(page.mediabox[2])  # width of the current page
        page_height = float(page.mediabox[3])  # height of the current page
        
        # Calculate the scaling factor based on the smaller dimension (width or height)
        scale_x = a4_width / page_width
        scale_y = a4_height / page_height
        
        # Use the smaller scale factor to maintain aspect ratio and fit content within A4
        scale_factor = min(scale_x, scale_y)
        
        # Scale the page using the calculated factor
        page.scale_by(scale_factor)

        # Center the content if there is remaining space (this happens when content is smaller than A4)
        if scale_factor < 1.0:
            # Calculate the new width and height after scaling
            new_width = page_width * scale_factor
            new_height = page_height * scale_factor

            # Calculate margins to center the content
            margin_x = (a4_width - new_width) / 2
            margin_y = (a4_height - new_height) / 2

            # Move the page content to the center
            page.mediabox.lower_left = (margin_x, margin_y)
            page.mediabox.upper_right = (margin_x + new_width, margin_y + new_height)
        
        # Add the resized page to the writer object
        writer.add_page(page)

    # Write the resized PDF to the output file
    with open(output_pdf_path, "wb") as output_pdf:
        writer.write(output_pdf)

    printif(f"  ↪ Resized PDF with white background saved to {output_pdf_path}")

# Load the CSV data
load_csv_data("september.csv")

# Check if PNC codes match
for i in range(len(OLD_PNC_CODE_ORDER)):
    if OLD_PNC_CODE_ORDER[i] != pnc_code_order[i]:
        print(f"Expected: {OLD_PNC_CODE_ORDER[i]}, Got: {pnc_code_order[i]}")

# Cache receipt and image files
receipt_file_cache = os.listdir(os.getcwd() + FORMS_DIR)
image_file_cache = os.listdir(os.getcwd() + IMAGES_DIR)
pnc_reference_cache = [x.split(".")[0] for x in image_file_cache]
extension_cache = [x.split(".")[1] for x in image_file_cache]

# Process each PDF file
merger = PdfWriter()
for index, pdf_file_name in enumerate(pnc_code_order):
    # Append .pdf file extension
    original_name = pdf_file_name
    pdf_file_name = f"{pdf_file_name}.pdf"

    if not check_file_existence(pdf_file_name, image_file_cache, receipt_file_cache) and not check_file_image_existence(pdf_file_name, image_file_cache, receipt_file_cache) :
        print(f"X {pdf_file_name} {who_is[index]}")
        missing_files.append(f"{dates[index]} {pdf_file_name} {who_is[index]}")
        continue
    else:
        printif(f"  {pdf_file_name} {who_is[index]}")

    # Fill out the form
    printif(f"  ↪ Processing PDF: {pdf_file_name}")
    try:
        pypdftk.fill_form(fr"./{FORMS_DIR}/{pdf_file_name}", out_file=fr"./{FLATTENED_DIR}/{pdf_file_name}", flatten=True)
    except Exception as e:
        printif(f"  ↪ Error filling form for {pdf_file_name}: {str(e)}")

    # pypdftk.fill_form(fr"./{FORMS_DIR}/{pdf_file_name}", out_file=fr"./{FLATTENED_DIR}/{pdf_file_name}", flatten=True)
    printif("  ↪ Appending to merger")

    merger.append(fr"{os.getcwd()}/{FLATTENED_DIR}/{pdf_file_name}")
    # Get the transaction number (PNC code)
    pnc_code = pdf_file_name.split(".")[0]

    # Check if there is a corresponding receipt in the image folder
    if pnc_code in pnc_reference_cache:
        receipt_index = pnc_reference_cache.index(pnc_code)
        extension = extension_cache[receipt_index]

        # If it's already a PDF, append it directly
        if extension == "pdf":
            printif("  ↪ Adding receipt")
            resize_pdf_to_a4(os.getcwd() + IMAGES_DIR + f"/{image_file_cache[receipt_index]}", f"{os.getcwd()}/temp.pdf")
            merger.append(os.getcwd() + "/temp.pdf")
        else:
            printif("  ↪ Adding image receipt")
            # Convert image to PDF
            os.popen(f'img2pdf "{os.getcwd()}{IMAGES_DIR}/{image_file_cache[receipt_index]}" --output temp.pdf --pagesize A4')
            time.sleep(3)  # Wait for the conversion
            merger.append(os.getcwd() + "/temp.pdf")

        printif(f"  ↪ Wrote {pdf_file_name} to combined pdf.")
    else:
        print(f"File {pdf_file_name} not found in images folder! Did you add the receipt yet?")

# Write the merged PDF
merger.write(os.getcwd() + f"/total.pdf")
merger.close()

# Print missing files
# for line in missing_files:
#     print(line)
