import cv2
import numpy as np
from fpdf import FPDF
import os
import fitz
from pathlib import Path


print("import")
#############################################
# import
# import system data

# default system values
contrast = 0
brightness = 0
invert = 0
power = 1
filename = 0

# read txt system memory
with open("system/system.txt", "r") as file:
    for line in file:
        # strip whitespace from the line
        line = line.strip()

        # split the line into key and value
        key, value = line.split("=")
        key = key.strip()
        value = value.strip()

        # assign memory variable
        if key == "contrast":
            contrast = int(value)
        elif key == "brightness":
            brightness = int(value)
        elif key == "invert":
            invert = int(value)
        elif key == "power":
            power = int(value)


if power != 1:
    exit()

# import image data
with open("system/command.txt", "r") as file:
    for line in file:
        # strip whitespace from the line
        line = line.strip()

        # split the line into key and value
        key, value = line.split("=")
        key = key.strip()
        value = value.strip()

        # assign memory variable
        if key == "filename":
            filename = str(value)

image_path = cv2.imread("buffer/" + str(filename))
grayImage = cv2.cvtColor(image_path, cv2.COLOR_BGR2GRAY)

#############################################
# image processing
mm_width = 200

# image dimensions
pixel_height, pixel_width = grayImage.shape # [px]
mm2px_ratio = pixel_width / mm_width # mm to px conversion ratio
mm_height = pixel_height / mm2px_ratio

# dot data
dot_fi = 0.636 # [mm]
dot_shift = 0.9 # [mm] from left edge 1 to left edge 2 & up edge 1 to up edge 2 of two same rows
dot_shift_rows = 0.45 # [mm] from left edge 1 to left edge 2 & up edge 1 to up edge 2 of two diff rows

dots_count_even_hor = 1 + int((mm_width - dot_fi)/dot_shift) # number of dots in one even row
dots_count_odd_hor = int(mm_width/dot_shift) # number of dots in one odd row
dots_count_even_ver = 1 + int((mm_height - dot_fi)/dot_shift) # number of dots in one even column
dots_count_odd_ver = int(mm_height/dot_shift) # number of dots in one odd column


#############################################
# matrix of needles

def grayscale2needle(grayscale):
    if invert == 1:
        blackscale = float(grayscale)
        corr_blackscale = blackscale ** 0.6  # gamma correction
        corr_blackscale = corr_blackscale * (255 / (255 ** 0.6))
    else:
        blackscale = 1-grayscale/255
        corr_blackscale = blackscale ** 0.6  # gamma correction


        #blackscale = float(255-grayscale)
        #corr_blackscale = blackscale**0.6 # gamma correction
        #corr_blackscale = corr_blackscale * (255/(255**0.6))

    formula = corr_blackscale * 8
    #formula = corr_blackscale/31.875
    needle_numb = int(round(formula))
    return needle_numb

# needles matrix even
grayscale_matrix_even = []
i = 0

for i in range(dots_count_even_ver):
    j = 0
    grayscale_matrix_row_even = []
    for j in range(dots_count_even_hor):
        dot_y_up_px = int((0 + i*dot_shift)*mm2px_ratio)
        dot_y_bott_px = int((dot_fi + i*dot_shift)*mm2px_ratio)
        dot_x_left_px = int((0 + j*dot_shift)*mm2px_ratio)
        dot_x_right_px = int((dot_fi + j*dot_shift)*mm2px_ratio)

        dot_colour = np.mean(grayImage[dot_y_up_px:dot_y_bott_px, dot_x_left_px:dot_x_right_px])
        grayscale_matrix_row_even.append(grayscale2needle(dot_colour))
        j += 1

    grayscale_matrix_even.append(grayscale_matrix_row_even)
    i += 1

# needles matrix odd
grayscale_matrix_odd = []
i = 0

for i in range(dots_count_odd_ver):
    j = 0
    grayscale_matrix_row_odd = []
    for j in range(dots_count_odd_hor):
        dot_y_up_px = int((dot_shift_rows + i*dot_shift)*mm2px_ratio)
        dot_y_bott_px = int((dot_shift_rows + dot_fi + i*dot_shift)*mm2px_ratio)
        dot_x_left_px = int((dot_shift_rows + j*dot_shift)*mm2px_ratio)
        dot_x_right_px = int((dot_shift_rows + dot_fi + j*dot_shift)*mm2px_ratio)

        dot_colour = np.mean(grayImage[dot_y_up_px:dot_y_bott_px, dot_x_left_px:dot_x_right_px])
        grayscale_matrix_row_odd.append(grayscale2needle(dot_colour))
        j += 1

    grayscale_matrix_odd.append(grayscale_matrix_row_odd)
    i += 1


#############################################
# printing

def needle_radius(needle_numb):
    radius_needle = (0.8 * needle_numb/8)/2
    return radius_needle


pdf = FPDF(orientation="P", unit="mm", format="A4")
pdf.add_page()
pdf.set_fill_color(0)

# needles matrix even
i = 0
dot_y_mid_mm = 5 + dot_fi/2


for sublist in grayscale_matrix_even:
    j = 0
    for number in sublist:
        radius = float(needle_radius(number))
        dot_x_mid_mm = 5 + dot_fi/2 + j*dot_shift
        if radius != 0:
            pdf.circle(x=dot_x_mid_mm, y=dot_y_mid_mm, radius=radius, style="F")
        j += 1
    i += 1
    dot_y_mid_mm = 5 + dot_fi/2 + i*dot_shift


# needles matrix odd
i = 0
dot_y_mid_mm = 5 + dot_shift_rows + dot_fi/2


for sublist in grayscale_matrix_odd:
    j = 0
    for number in sublist:
        radius = float(needle_radius(number))
        dot_x_mid_mm = 5 + dot_shift_rows + dot_fi/2 + j*dot_shift
        if radius != 0:
            pdf.circle(x=dot_x_mid_mm, y=dot_y_mid_mm, radius=radius, style="F")
        j += 1
    i += 1
    dot_y_mid_mm = 5 + dot_shift_rows + dot_fi/2 + i*dot_shift


############################################
# tossing to drawer

def get_unique_filename(folder_path, choosen_filename):
    name, ext = os.path.splitext(choosen_filename)
    counter = 1
    unique_filename = choosen_filename
    while os.path.exists(os.path.join(folder_path, unique_filename)):
        unique_filename = f"{name}{counter}{ext}"
        counter += 1
    return unique_filename

pdf.output("buffer/buffer.pdf") # creating pdf buffer file


drawer_path = str("../../paper_drawer/")
unique_filename = get_unique_filename(drawer_path, str(filename) + ".png")
print(unique_filename)
file_path = str("../../paper_drawer/" + unique_filename)

# export pdf to png
pdf_path = str("buffer/buffer.pdf")
pdf_document = fitz.open(pdf_path)

for page_num in range(len(pdf_document)):
    page = pdf_document[page_num]
    pix = page.get_pixmap(dpi=600)
    output_path = file_path
    pix.save(output_path)

pdf_document.close()
print("zapisanie")
os.remove("buffer/buffer.pdf")
#os.remove("buffer/" + str(filename))
