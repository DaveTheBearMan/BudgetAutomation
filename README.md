# How to receipt
Delete the .txt files from each folder
Name each file after its pnc reference number

- Receipts go in Receipts folder
- Pdf forms go in forms folder
- Flattened / Seperate is automatic
- Combined pdf is produced in same directory as combine.py


# How to get attendance from an event 

Use the dquery command on OBIII. You query typically Other or General Meeting for that day, and its usable in any channel.
Sometimes it'll take a little while, but thats just OBIII being slow (running on a nanode somewhere in the cloud) 
Any event involving food requires writing about attendance, so find the attendance from that day, and use the 1010_attendance pdf rather than the regular 1010 pdf.

# PDF to Excel

In the event that the office manager does not have an excel spreadsheet of the pdf they upload, you have to make it into excel yourself
- This is the website I use [here](https://www.ilovepdf.com/pdf_to_excel)
- This will give you a bunch of different sheets
- Youre gonna have to make a new spreadsheet and just put in the lines that are in the format Post Date | Trans Date | Ref # | Trans Desc | Amt
  - Some lines have a purchase ID, do not move those over to the new spreadsheet
  - Save the new spreadsheet as a csv, you'll have to change the name in the code to be what the new name you gave it is, make sure its in the same directory as combine.py
  - This should if its working let you run combine.py and see what youre missing and what day it was
