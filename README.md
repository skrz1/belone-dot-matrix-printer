# belone-dot-matrix-printer

This is a software that changes image to look like retro dot matrix print.\
Printer makes a black-white image of around 27 DPI with dot matrix at an angle of 45 degrees.\
Final printed image is a ".png" file on a A4 page with margins 5 mm on each side. DPI of this image can be changed in "printer\software\system\system.txt" under "DPI = " value. I recommend using following values: 96, 150, 220, 330, 440, 600.

Install python libraries.
```
pip install -r requirements.txt
```

How to use (subject to change):\
1 Insert file to be printed inside "printer\software\memory\buffer". Supported files are: ".txt", ".pdf", ".png", ".jpg", ".HS.txt" (HeinzoScript file - see my other project - HeinzoScript reader)\
2 Open "printer\software\system\command4initializer.txt" file and change its content as listed below.\
3 Run "printer\software\initializer.exe".\
4 Your print will be generated inside "paper_drawer" folder, located next to the "printer" folder.

Standard command for belone printer is made of 5 lines for one file. How to write commands in "command4initializer.txt":
<pre>
filename = loremipsum.txt    //This line contains file name to be printed
width = 150                  //For txt files it means the width of text column in milimetres.
rotate = 0                   //For txt files it means if the text is written from up to down, or from rigt side to left side (rotated 90 deg clockwise).
font_size = 25               //This line sets font size of txt file. Minimum is 20 points.
numbering = 1                //This line enables numbering of each line of txt file.
filename = exampleimage.png  //Notice no space left between two files.
width = 200                  //For pdf, png and jpg files it means the width of resized file. If width is greater than 200 mm, file will be printed as a poster.
rotate = 0                   //For pdf, png and jpg files it rotates the image 90 deg clockwise.
font_size = 0                //No impact for non-txt files, but leave it.
numbering = 0                //No impact for non-txt files, but leave it.
</pre>
For "HS.txt" files only "filename = " line matters, but leave other lines.
