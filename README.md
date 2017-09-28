# OCR for HKID using Python 3 and OpenCV 3 / 基於Python3及OpenCV3 - 香港身份證OCR

OCR for HKID - 香港身份證OCR

Description will be provided later.

## How to use? / 如何使用?

`python hkid.py -i <image_path> [-d/--debug]`

It will return a JSON string.

### Sample output - Text

`{'result': ['李智能', 'LEE, Chi Nan', '2621 2535 5174', '出生日期Date of Birth', '女F', '01-01-1968', 'k AZ', '簽發日期Date of Issue', '(01-79)']}`

![Sample text output](https://github.com/alucard001/OCR-for-HKID/raw/master/hkid-ocr-output.png)

### Sample output - How image is splitted
![OCR separate image output](https://github.com/alucard001/OCR-for-HKID/raw/master/hkid-output.png)
