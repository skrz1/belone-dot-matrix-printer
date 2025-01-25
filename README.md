# belone-dot-matrix-printer

This is a software that changes image to look like retro dot matrix print.
Printer makes a black-white image of around 27 DPI with dot matrix at an angle of 45 degrees.
Final printed image is a ".png" file of 600 PPI on a A4 page with margins 5 mm on each side.

How to use (subject to change):
1 Insert image to be printed inside "printer\software\buffer folder".
2 Open "printer\software\system\command.txt" file and change its content to "filename = yourfile.extension", eg "filename = bebok.jpg".
3 Run "printer\software\printing software.py".
4 Your print will be generated at "paper drawer" folder.

Supported image to be printed is ".jpg" portrait mode 4724x6780 px (200x287 mm at 600 ppi)
