import cv2
import os
import fitz
import numpy as np
from fpdf import FPDF, XPos, YPos
import logging
import subprocess
import sys
import math

logging.getLogger('fpdf.output').level = logging.ERROR

#############################################
# import

application_path = os.path.dirname(sys.executable) # absolute path of exe
#application_path = os.path.dirname(__file__) # absolute path of python

# folders names
paper_drawer_folder = "paper_drawer"
system_folder = "system"
fontpack_folder = "fontpack"
memory_folder = "memory"
buffer_folder = "buffer"


# create paper drawer if it does not exist
printer_folder, tail = os.path.split(application_path)
main_folder, tail = os.path.split(printer_folder)
path2paper_drawer = os.path.join(main_folder, paper_drawer_folder)


if not os.path.exists(path2paper_drawer):
    os.makedirs(path2paper_drawer)

# import system data

# default system values
power = 1
busy = 1

# read txt system memory
system_txt_path = os.path.join(application_path, system_folder, "system.txt")
with open(system_txt_path, "r") as file:
    for line in file:
        # strip whitespace from the line
        line = line.strip()

        # split the line into key and value
        key, value = line.split("=")
        key = key.strip()
        value = value.strip()

        # assign memory variable
        if key == "power":
            power = int(value)

if power != 1:
    exit()

# import file data
queue = []

filename = 0
width = 0
rotate = 0
font_size = 0
numbering = 0

# read txt file data and append to queue
command4initializer_txt_path = os.path.join(application_path, system_folder, "command4initializer.txt")
with open(command4initializer_txt_path, "r") as file:
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
        elif key == "width":
            width = float(value)
        elif key == "rotate":
            rotate = int(value)
        elif key == "font_size":
            font_size = int(value)
        elif key == "numbering":
            numbering = int(value)
            queue.append([filename, width, rotate, font_size, numbering])


#############################################
# creating queue for printing_software

queue_printing_software = []

# files in queue processing
for i in range(len(queue)):
    filename = queue[i][0]
    width = queue[i][1]
    rotate = queue[i][2]
    font_size = queue[i][3]
    numbering = queue[i][4]

    name, ext = os.path.splitext(filename)

    # convert txt to pdf
    if ext == ".txt":

        # HeinzoScript
        HS_init_name, HS_ext = os.path.splitext(name)
        if HS_ext == ".HS":
            command4HSreader_txt_path = os.path.join(application_path, "command4HSreader.txt")
            init_path_path = os.path.join(application_path, memory_folder, buffer_folder, f"{name + ext}")
            output_path_path = os.path.join(application_path, memory_folder, buffer_folder, name)

            with open(command4HSreader_txt_path, "w") as file:
                file.write("HS_init_path = " + init_path_path)
                file.write("\n")
                file.write("HS_output_path = " + output_path_path)
                file.write("\n")
                file.write("HS_output_ext = .pdf")
                file.close()

            HS_reader_exe_path = os.path.join(application_path, "HeinzoScript_reader_belone.exe")
            HS_reader_exe = subprocess.run([HS_reader_exe_path])

            pdf_document_HS_path = os.path.join(application_path, memory_folder, buffer_folder, f"{name + ".pdf"}")
            pdf_document_HS = fitz.open(pdf_document_HS_path)
            for page_num in range(len(pdf_document_HS)):
                unique_filename_raster = name + "_" + str(page_num+1) + "-" + str(len(pdf_document_HS)) + ".png"
                page = pdf_document_HS[page_num]
                pix = page.get_pixmap(dpi=600)
                output_path_path = os.path.join(application_path, memory_folder, buffer_folder, unique_filename_raster)
                output_path = str(output_path_path)

                if pix.width > pix.height:
                    pix = page.get_pixmap(pix = page.get_pixmap(matrix=fitz.Matrix(1,1).prerotate(90).prescale(600/72, 600/72), clip=True))
                    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, -1)
                    cv2.imwrite(str(output_path), img)
                else:
                    pix.save(output_path)
                queue_printing_software.append(output_path)
            pdf_document_HS.close()
            os.remove(os.path.join(application_path, memory_folder, buffer_folder, f"{name + ".pdf"}"))

        # normal txt file
        else:
            # apply data to file
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
            pdf_txt = FPDF(orientation, "mm", (200, 287))
            pdf_txt.add_font("Inconsolata", style="", fname=os.path.join(application_path, system_folder, fontpack_folder, "Inconsolata_Condensed-Regular.ttf"))
            pdf_txt.add_font("Inconsolata", style="B", fname=os.path.join(application_path, system_folder, fontpack_folder, "Inconsolata_Condensed-ExtraBold.ttf"))
            # add a page
            pdf_txt.add_page()
            pdf_txt.set_margin(0)



            #############################################
            # open HS folder

            # open the text file in read mode
            with open(os.path.join(application_path, memory_folder, buffer_folder, filename), "r", encoding="UTF-8") as count_lines:
                lines_txt = count_lines.readlines()
            number_of_lines_txt = int(len(lines_txt))
            number_of_digits_linecount = len(str(number_of_lines_txt))

            ############################################# belone printer limitation
            if font_size < 20:
                font_size = 20
            else:
                font_size = font_size
            pdf_txt.set_font("Inconsolata", size=font_size)

            if numbering == 1:
                line_number_width = int(round(font_size*6/15*(number_of_digits_linecount+1)*0.3528, 1))
            else:
                line_number_width = 0
            file_txt = open(os.path.join(application_path, memory_folder, buffer_folder, filename), "r", encoding="UTF-8")
            line_number = 1

            for x in file_txt:
                # adding lines if numbering lines is enabled
                if numbering == 1:
                    # adding text lines
                    pdf_txt.multi_cell(line_number_width, int(round(font_size * 6 / 15, 1)), text=str(line_number), new_x=XPos.LMARGIN, new_y=YPos.LAST, align="L")
                    pdf_txt.set_x(line_number_width)

                    pdf_txt.multi_cell(width - line_number_width, int(round(font_size * 6 / 15, 1)), text=x, new_x=XPos.LMARGIN, new_y=YPos.LAST, align="L", markdown=True)
                    line_number += 1
                # adding lines if numbering lines is disabled
                elif numbering == 0:
                    pdf_txt.multi_cell(width, int(round(font_size * 6 / 15, 1)), text=x, new_x=XPos.LMARGIN, new_y=YPos.LAST, align="L", markdown=True)
            file_txt.close()

            pdf_txt.output(os.path.join(application_path, memory_folder, buffer_folder, f"{filename+".pdf"}"))
            os.remove(os.path.join(application_path, memory_folder, buffer_folder, filename))

            pdf_document_txt = fitz.open(os.path.join(application_path, memory_folder, buffer_folder, f"{filename+".pdf"}"))
            for page_num in range(len(pdf_document_txt)):
                unique_filename_raster = filename + "_" + str(page_num+1) + "-" + str(len(pdf_document_txt)) + ".png"
                page = pdf_document_txt[page_num]
                pix = page.get_pixmap(dpi=600)
                output_path = os.path.join(application_path, memory_folder, buffer_folder, unique_filename_raster)

                if pix.width > pix.height:
                    pix = page.get_pixmap(dpi=600, clip=True)
                    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, -1)
                    rotated_img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                    cv2.imwrite(str(output_path), rotated_img)
                else:
                    pix.save(output_path)
                queue_printing_software.append(output_path)
            pdf_document_txt.close()
            os.remove(os.path.join(application_path, memory_folder, buffer_folder, f"{filename+".pdf"}"))

    elif ext == ".pdf":
        pdf_document = fitz.open(os.path.join(application_path, memory_folder, buffer_folder, filename))
        for page_num in range(len(pdf_document)):
            unique_filename_raster = name + "_" + str(page_num + 1) + "-" + str(len(pdf_document)) + ".png"
            page = pdf_document[page_num]

            # resizing image
            if rotate == 1:
                pix = page.get_pixmap(matrix=fitz.Matrix(1,1).prerotate(90).prescale(600/72, 600/72))
                factor = width/(pix.width/600*25.4)
                pix = page.get_pixmap(matrix=fitz.Matrix(1,1).prerotate(90).prescale(600/72*factor, 600/72*factor))
            else:
                pix = page.get_pixmap(matrix=fitz.Matrix(1,1).prescale(600/72, 600/72))
                factor = width / (pix.width / 600 * 25.4)
                pix = page.get_pixmap(matrix=fitz.Matrix(1, 1).prescale(600 / 72 * factor, 600 / 72 * factor))

            # define cells of poster
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, -1)
            cells_width = math.ceil(pix.width/4725)
            cells_height = math.ceil(pix.height/6780)
            number_of_cells = cells_width * cells_height

            # define white background for images smaller than page
            bg_width, bg_height = 4724, 6780

            # create cells of poster
            l = 1
            for j in range(cells_height):
                for k in range(cells_width):
                    unique_filename_raster = filename + "_" + str(l) + "-" + str(number_of_cells) + ".png"
                    output_path = os.path.join(application_path, memory_folder, buffer_folder, unique_filename_raster)
                    cell = img[j*6780:(j+1)*6780, k*4724:(k+1)*4724]
                    cell_height, cell_width, channel = cell.shape
                    background = np.ones((bg_height, bg_width, 3), dtype=np.uint8) * 255
                    background[0:cell_height, 0:cell_width] = cell
                    cv2.imwrite(str(output_path), background)
                    queue_printing_software.append(output_path)
                    l += 1
        pdf_document.close()
        os.remove(os.path.join(application_path, memory_folder, buffer_folder, filename))

    elif ext == ".png" or ext == ".jpg" or ext == ".jpeg":
        # read image
        image = cv2.imread(os.path.join(application_path, memory_folder, buffer_folder, filename))
        if rotate == 1:
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

        # resize image
        image_height, image_width, channel = image.shape
        new_pixel_width = 4724*width/200
        ratio = new_pixel_width/image_width
        image = cv2.resize(image, (0,0), fx=ratio, fy=ratio)
        image_height, image_width, channel = image.shape

        # define cells of poster
        cells_width = math.ceil(image_width / 4725)
        cells_height = math.ceil(image_height / 6780)
        number_of_cells = cells_width * cells_height

        # define white background for images smaller than page
        bg_width, bg_height = 4724, 6780

        # create cells of poster
        l = 1
        for j in range(cells_height):
            for k in range(cells_width):
                unique_filename_raster = filename + "_" + str(l) + "-" + str(number_of_cells) + ".png"
                output_path = os.path.join(application_path, memory_folder, buffer_folder, unique_filename_raster)
                cell = image[j * 6780:(j + 1) * 6780, k * 4724:(k + 1) * 4724]
                cell_height, cell_width, channel = cell.shape
                background = np.ones((bg_height, bg_width, 3), dtype=np.uint8) * 255
                background[0:cell_height, 0:cell_width] = cell
                cv2.imwrite(str(output_path), background)
                queue_printing_software.append(output_path)
                l += 1
        os.remove(os.path.join(application_path, memory_folder, buffer_folder, filename))


command_path = os.path.join(application_path, system_folder, "command.txt")
for i in range(len(queue_printing_software)):
    with open(command_path, "w") as file:
        path_file2print, name_file2print = os.path.split(queue_printing_software[i])
        file.write("filename = " + name_file2print)
        file.close()
        printing_software_path = os.path.join(application_path, "printing_software.exe")
        printing_software_exe = subprocess.run([printing_software_path])
