
'''
This is our OCR (Optical Character Recognition) utility script for extracting text from images.
We used EasyOCR which is a Python library that can read text from images with high accuracy.
This script is particularly useful for processing images that contain text data that we want to include in our Ghana chatbot database.

Our script handles SSL certificate verification issues that sometimes occur when downloading models or processing images from various sources.
'''



#All Imports

import easyocr
import ssl




#We disabled SSL verification to handle certificate issues when EasyOCR downloads its models or processes images
ssl._create_default_https_context = ssl._create_unverified_context


def extract_text_from_image(image_path):
    
    #We initialized the EasyOCR reader with English to support reading English text from images
    reader = easyocr.Reader(['en'])
    
    #We read the text from the image and this returns a list of detections with coordinates and text
    result = reader.readtext(image_path)
    
    #We created an empty list to store all the text we extract from the image
    text_list = []
    
    #We iterated through each text detection found in the image
    for detection in result:
        
        #Each detection came with a tuple in the format (coordinates, text, confidence)
        #We extracted only the text part (index 1) from each detection
        
        text_found = detection[1]
        text_list.append(text_found)

    #We joined all the extracted text pieces into one complete string separated by spaces
    full_text = ' '.join(text_list)
    
    return full_text