import json
import os
import re
import sys
import PIL.Image as pil
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()

if len(sys.argv) != 3:
    sys.exit(1)
    
filenm = sys.argv[1]
obj = sys.argv[2]

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(model_name='gemini-1.5-flash')

imgobj = pil.open(filenm)
width, height = imgobj.size
if imgobj.format == "JPEG":
    postfix = "jpg"
elif imgobj.format == "PNG":
    postfix = "png"
elif imgobj.format == "GIF":
    postfix = "gif"
elif imgobj.format == "BMP":
    postfix = "bmp"
else:
    postfix = ""
    
prompt = f"Return bounding boxes around every {obj}, " \
         "for each one return [ymin, xmin, ymax, xmax]"
response = model.generate_content([imgobj, prompt])
print(response.text)

def extract_bounding_boxes(text):
    # Regular expression to match numbers inside square brackets
    pattern = r"\[?\d+[, ]+\d+[, ]+\d+[, ]+\d+\]?"
    matches = re.findall(pattern, text)
    #print(matches)
    
    bounding_boxes = []
    for match in matches:
        if match.find(',') == -1:
            match = match.replace(' ', ',')
        if match[0] == '[' and match[-1] == ']':
            bounding_boxes.append(json.loads(match))
        else:
            bounding_boxes.append(json.loads(f"[{match}]"))

    return bounding_boxes


try:
    boundings = extract_bounding_boxes(response.text)
    print(boundings)

    index = 1
    
    for item in boundings:
        right = (item[3] / 1000) * width
        lower = (item[2] / 1000) * height
        left = (item[1] / 1000) * width
        upper = (item[0] / 1000) * height
        cropped_img = imgobj.crop((left, upper, right, lower))
        with open(f'./{obj}-{index}.{postfix}', 'wb') as fp:
            cropped_img.save(fp)
        index += 1

except Exception as ex:
    print(response.text)
    print(str(ex))
    pass

