import cv2
import os
import fitz
from fpdf import FPDF, XPos, YPos
import logging
import shutil
import sys

logging.getLogger('fpdf.output').level = logging.ERROR

#############################################
# import

application_path = os.path.dirname(sys.executable) # absolute path of exe
#application_path = os.path.dirname(__file__) # absolute path of python

# folders names
system_folder = "system"
fontpack_folder = "fontpack"

# import file data

path2HS_init = ""
path2HS_output = ""
ext_out = ""

command4HSreader_path = os.path.join(application_path, "command4HSreader.txt")
with open(command4HSreader_path, "r") as file:
    for line in file:
        # strip whitespace from the line
        line = line.strip()

        # split the line into key and value
        key, value = line.split("=")
        key = key.strip()
        value = value.strip()

        # assign memory variable
        if key == "HS_init_path":
            path2HS_init = str(value)
        elif key == "HS_output_path":
            path2HS_output = str(value)
        elif key == "HS_output_ext":
            ext_out = str(value)

file_folder = 0
filename = 0
width = 0
rotate = 0
font_size = 0
numbering = 0
numbering_font_size = 0
page_number = 0

# read HS file data
with open(str(path2HS_init), "r") as file:
    for line in file:
        # strip whitespace from the line
        line = line.strip()

        # split the line into key and value
        key, value = line.split("=")
        key = key.strip()
        value = value.strip()

        # assign memory variable
        if key == "file_folder":
            file_folder = str(value)
        elif key == "filename":
            filename = str(value)
        elif key == "width":
            width = int(value)
        elif key == "rotate":
            rotate = int(value)
        elif key == "font_size":
            font_size = int(value)
        elif key == "numbering":
            numbering = int(value)
        elif key == "numbering_font_size":
            numbering_font_size = int(value)
        elif key == "page_number":
            page_number = int(value)


#############################################
# apply HS data to file

# apply rotation to page orientation
if rotate == 1:
    orientation = "L"
    max_page_h = 200
else:
    orientation = "P"
    max_page_h = 287

# apply maximum line length
if rotate == 1:
    if width > 287:
        width = 287
    else:
        width = width
else:
    if width > 200:
        width = 200
    else:
        width = width

# pdf particulars
pdf_HS = FPDF(orientation, "mm", (200, 287))
pdf_HS.add_font("Inconsolata", style="", fname=os.path.join(application_path, system_folder, fontpack_folder, "Inconsolata_Condensed-Regular.ttf"))
pdf_HS.add_font("Inconsolata", style="B", fname=os.path.join(application_path, system_folder, fontpack_folder, "Inconsolata_Condensed-ExtraBold.ttf"))
pdf_HS.add_font("Inconsolata-LGC", style="", fname=os.path.join(application_path, system_folder, fontpack_folder, "Inconsolata-LGC.ttf"))
pdf_HS.add_font("Inconsolata-LGC", style="B", fname=os.path.join(application_path, system_folder, fontpack_folder, "Inconsolata-LGC-Bold.ttf"))
pdf_HS.add_font("Inconsolata-LGC", style="I", fname=os.path.join(application_path, system_folder, fontpack_folder, "Inconsolata-LGC-Italic.ttf"))
pdf_HS.add_font("Inconsolata-LGC", style="BI", fname=os.path.join(application_path, system_folder, fontpack_folder, "Inconsolata-LGC-BoldItalic.ttf"))
# add a page
pdf_HS.add_page()
pdf_HS.set_margin(0)
if page_number == 1:
    pdf_HS.set_auto_page_break(auto= True, margin=7)
    max_page_h = (max_page_h - 7)

# create path to main HS folder
parent_folder, tail = os.path.split(path2HS_init)
folder_dir = os.path.join(parent_folder, file_folder)

#############################################
# open HS folder

# open the text file in read mode
with open(os.path.join(folder_dir, filename), "r", encoding="UTF-8") as count_lines:
    lines_txt = count_lines.readlines()
number_of_lines_txt = int(len(lines_txt))
number_of_digits_linecount = len(str(number_of_lines_txt))

############################################# belone printer limitation
if numbering_font_size < 20:
    numbering_font_size = 20
else:
    numbering_font_size = numbering_font_size

if numbering == 1 or numbering == 2:
    line_number_width = int(round(numbering_font_size*6/15*(number_of_digits_linecount+1)*0.3528, 1))
elif numbering == 0:
    line_number_width = 0
file_txt = open(os.path.join(folder_dir, filename), "r", encoding="UTF-8")

line_number = 1
fig_number = 1

# create pdf file based on txt file
for x in file_txt:
    x_HS_marking = ""

    x_Center = 0
    x_Right = 0
    x_Number = 0
    x_Image = 0
    x_caption = 0
    x_Greek = 0
    x_Up = 0
    x_manual_size = 0
    x_size = 0

    first_letter = x[0]
    try:
        second_letter = x[1]
    except:
        second_letter = ""
    if first_letter == "<" and second_letter == "<":
        x_HS_marking = x.split("<<")
        del x_HS_marking[0]
        x_HS_marking = x_HS_marking[0].split(">")
        x_HS_marking = str(x_HS_marking[0])

    if "C" in x_HS_marking:
        x_Center = 1
    if "R" in x_HS_marking:
        x_Right = 1
    if x_Center == 1 and x_Right == 1:
        x_Center = 0
        x_Right = 0
    if "N" in x_HS_marking:
        x_Number = 1
    if "n" in x_HS_marking:
        line_number = 1
    if "I" in x_HS_marking:
        x_Image = 1
    if "c" in x_HS_marking:
        x_caption = 1
    if "G" in x_HS_marking:
        x_Greek = 1
    if "U" in x_HS_marking:
        x_Up = 1
    if "-" in x_HS_marking:
        x_manual_size = 1
        x_HS_number = x_HS_marking.split("-")
        x_size = int(x_HS_number[1])

    x_letters = []

    for i in range(len(x)):
        if len(x_HS_marking) > 0:
            if i > len(x_HS_marking) + 2:
                x_letters.append(x[i])
        else:
            x_letters.append(x[i])

    x = "".join(x_letters)
    x_letters.clear()

    # setting text editing values
    if x_Center == 1:
        line_align = "C"
    elif x_Right == 1:
        line_align = "R"
    else:
        line_align = "L"

    if x_manual_size == 1 and x_Image == 0:
        text_font_size = x_size
    else:
        text_font_size = font_size

    ############################################# belone printer limitation
    if text_font_size < 20:
        text_font_size = 20
    else:
        text_font_size = text_font_size

    if numbering == 1:
        if x_Number == 1 or x_Image == 1 or x_caption == 1 or x_Up == 1:
            line_number2print = ""
        else:
            line_number2print = str(line_number)
            line_number += 1
    elif numbering == 2:
        if x_Image == 1 or x_caption == 1 or x_Up == 1:
            line_number2print = ""
        else:
            if x_Number == 1:
                line_number2print = str(line_number)
                line_number += 1
            elif x_Number == 0:
                line_number2print = ""


    # extracting image data in case of image cell
    if x_Image == 1:
        for i in range(len(x)):
            x_letters.append(x[i])
        del x_letters[len(x)-1]
        image_cell_name = "".join(x_letters)
        x_letters.clear()

        image_path = os.path.join(folder_dir, image_cell_name)
        cell_image = cv2.imread(image_path)
        pixel_height, pixel_width, channel = cell_image.shape

        # limit width to page width
        if x_size > (width-line_number_width):
            x_size = (width-line_number_width)
        else:
            x_size = x_size
        mm_height = int(round(x_size*pixel_height/pixel_width, 1))
        if mm_height > max_page_h:
            ratio = max_page_h/mm_height
            x_size = int(round(x_size*ratio,1))
            mm_height = int(round(x_size * pixel_height / pixel_width, 1))



    # adding numeration to caption cell
    if x_caption == 1:
        x = "fig. " + str(fig_number) + ": " + str(x)
        fig_number += 1

    # adding lines if numbering lines is enabled
    if numbering == 1 or numbering == 2:
        # adding text lines
        if x_Image == 0:
            pdf_HS.set_font("Inconsolata", size=numbering_font_size)
            pdf_HS.multi_cell(line_number_width, int(round(numbering_font_size * 6 / 15, 1)), text=line_number2print, new_x=XPos.LMARGIN, new_y=YPos.LAST, align="L")
            pdf_HS.set_x(line_number_width)

            if x_Greek == 0:
                pdf_HS.set_font("Inconsolata", size=text_font_size)
            else:
                pdf_HS.set_font("Inconsolata-LGC", size=int(round(text_font_size*17/20,1)))

            if x_Up == 0:
                pdf_HS.multi_cell(width - line_number_width, int(round(text_font_size * 6 / 15, 1)), text=x, new_x=XPos.LMARGIN, new_y=YPos.LAST, align=line_align, markdown=True)
            elif x_Up == 1:
                pdf_HS.cell(width - line_number_width, int(round(text_font_size * 6 / 15, 1)), text=x, new_x=XPos.LMARGIN, new_y=YPos.LAST, align=line_align, markdown=True)

        # adding image lines
        elif x_Image == 1:
            pdf_HS.set_font("Inconsolata", size=text_font_size)
            pdf_HS.multi_cell(line_number_width, mm_height, text=line_number2print, new_x=XPos.LMARGIN, new_y=YPos.LAST, align="L")
            pdf_HS.set_x(line_number_width)

            y_image = pdf_HS.get_y()
            if line_align == "C":
                x_image = int(width - x_size)/2 + line_number_width/2
            elif line_align == "R":
                x_image = int(width - x_size)
            else:
                x_image = int(line_number_width)

            pdf_HS.multi_cell(width - line_number_width, mm_height, new_x=XPos.LMARGIN, new_y=YPos.NEXT, link=pdf_HS.image(image_path,x_image, y_image, x_size))

    # adding lines if numbering lines is disabled
    elif numbering == 0:
        # adding text lines
        if x_Image == 0:
            if x_Greek == 0:
                pdf_HS.set_font("Inconsolata", size=font_size)
            else:
                pdf_HS.set_font("Inconsolata-LGC", size=int(round(font_size*17/20,1)))
            if x_Up == 0:
                pdf_HS.multi_cell(width, int(round(font_size * 6 / 15, 1)), text=x, new_x=XPos.LMARGIN, new_y=YPos.LAST, align=line_align, markdown=True)
            elif x_Up == 1:
                pdf_HS.cell(width, int(round(font_size * 6 / 15, 1)), text=x, new_x=XPos.LMARGIN, new_y=YPos.LAST, align=line_align, markdown=True)

        # adding image lines
        elif x_Image == 1:
            y_image = pdf_HS.get_y()
            if line_align == "C":
                x_image = int(width - x_size)/2
            elif line_align == "R":
                x_image = int(width - x_size)
            else:
                x_image = int(0)

            pdf_HS.multi_cell(width, mm_height, new_x=XPos.LMARGIN, new_y=YPos.NEXT, border=1, link=pdf_HS.image(image_path,x_image, y_image, x_size))

file_txt.close()

def add_page_numbers(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = str(page_num + 1) + "-" + str(len(doc))

        # Define position (bottom center)
        if orientation == "P":
            rect = fitz.Rect(0, 790, 567, 813)
        elif orientation == "L":
            rect = fitz.Rect(0, 544, 813, 567)

        # Use insert_textbox with a custom font
        page.insert_textbox(rect, text, fontsize=18, fontname="Inconsolata", fontfile=os.path.join(application_path, system_folder, fontpack_folder, "Inconsolata_Condensed-Regular.ttf"), align=1)

    doc.save(output_pdf)
    doc.close()


#############################################
# generate pdf file
# create path to output folder

if page_number == 1:
    pdf_HS.output(os.path.join(f"{path2HS_output + "2137" + ext_out}"))
    add_page_numbers(os.path.join(f"{path2HS_output + "2137" + ext_out}"), os.path.join(f"{path2HS_output + ext_out}"))
    os.remove(path2HS_output + "2137" + ext_out)
else:
    pdf_HS.output(os.path.join(f"{path2HS_output + ext_out}"))

os.remove(path2HS_init)
shutil.rmtree(folder_dir)
