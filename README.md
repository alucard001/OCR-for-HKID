# OCR for HKID using Python 3 and OpenCV 3 / 基於Python3及OpenCV3 - 香港身份證OCR

## What is it?
This project is mainly used to demonstrate how I think about using OCR on a HKID.

## Points to note

- I am not perfect, neither is my code.
- Using this code at your own risk, there is **NO** absolute guarantee that the HKID will be able to scan whatever image you passed.
- In other words, it can only be used in a **reasonable** way.  For example, if you pass in an image with mainly the HKID and a little extra space around the border, that's OK.
However, if your image that your HKID is in the corner of the whole image while 80% of the image contains other stuff, this script will not work.
- The key to successful text recognition is clear image.  If your image is **NOT** clear, like the text is not easily and reasonably identified, this script may give strange result.
- The Google Key has been deactivated.  Please replace it with your own KEY.
- Yes you can use Facebook OCR, you are not limited to that.  You can also use [tesseract](https://github.com/tesseract-ocr/tesseract), which I also highly recommended.
Actually if you look at my code, I include (but commented) [pytesseract](https://github.com/madmaze/pytesseract).

## How to use? / 如何使用?

`python hkid.py -i <image_path> [-d/--debug]`

e.g. `python hkid.py -i hkid_sample-no-sample.jpg`

It will return a JSON string, like below.

`{'result': ['李智能', 'LEE, Chi Nan', '2621 2535 5174', '出生日期Date of Birth', '女F', '01-01-1968', 'k AZ', '簽發日期Date of Issue', '(01-79)']}`

### Sample output - How image is splitted when using -d/--debug
![OCR separate image output](https://github.com/alucard001/OCR-for-HKID/raw/master/hkid-output.png)

