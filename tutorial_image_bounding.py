import json
import os
import re
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(model_name='gemini-1.5-flash')

import PIL.Image as pil
goats = pil.open("./cats.png")
width, height = goats.size

prompt = "Return bounding boxes around every goat, " \
         "for each one return [ymin, xmin, ymax, xmax]"
response = model.generate_content([goats, prompt])
print(response.text)

def extract_bounding_boxes(text):
    # Regular expression to match numbers inside square brackets
    pattern = r"\[?\d+[,][ ]?\d+[,][ ]?\d+[,][ ]?\d+\]?"
    matches = re.findall(pattern, text)
    #print(matches)
    
    bounding_boxes = []
    for match in matches:
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
        cropped_img = goats.crop((left, upper, right, lower))
        with open(f'./cat-{index}.png', 'wb') as fp:
            cropped_img.save(fp)
        index += 1

except Exception as ex:
    print(response.text)
    print(str(ex))
    pass

