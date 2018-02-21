import eel
import base64
from io import BytesIO
from PIL import Image, ImageDraw
import numpy as np
from tqdm import tqdm

eel.init('web')

def clear_filter(img, w, h):
  # STEP1
  k1 = 2.0
  k2 = -0.5
  image_pixcels = np.array([[img.getpixel((x,y)) for x in range(w)] for y in range(h)])
  filtered_img = Image.new('RGB', (w, h))
  # STEP2
  for x in tqdm(range(w)):
    for y in range(h):
      r, g, b = image_pixcels[y][x]
      fr = int(min(255, max(0, r * k1 + g * k2 + b * k2)))
      fg = int(min(255, max(0, r * k2 + g * k1 + b * k2)))
      fb = int(min(255, max(0, r * k2 + g * k2 + b * k1)))
      filtered_img.putpixel((x,y), (fr, fg, fb))
  return filtered_img

def filter_size(w, h, x, y):
  size = 0
  if y < h * 2 / 3 or y > h * 10 / 11:
    size = 1
  if y < h / 2:
    size = 2
  if y < h / 3:
    size = 3
  return size

def unclear_filter(img, w, h):
  # STEP1
  image_pixcels = np.array([[img.getpixel((x,y)) for x in range(w)] for y in range(h)])
  filtered_img = Image.new('RGB', (w, h))
  # STEP2
  for x in tqdm(range(w)):
    for y in range(h):
      # STEP2-1
      s = filter_size(w, h, x, y)
      # STEP2-2
      if s != 0:
        x1 = max(0    , x - s)
        x2 = min(x + s, w - 1)
        y1 = max(0    , y - s)
        y2 = min(y + s, h - 1)
        x_size = x2 - x1 + 1
        y_size = y2 - y1 + 1
        mean_r, mean_g, mean_b = image_pixcels[y1:y2 + 1, x1:x2 + 1].reshape(x_size * y_size, 3).mean(axis = 0)
      else:
        mean_r, mean_g, mean_b = image_pixcels[y][x]
      filtered_img.putpixel((x,y), (int(mean_r), int(mean_g), int(mean_b)))
  return filtered_img

# javascript used
@eel.expose
def convert_img(img): 

    # image decode
    im = Image.open(BytesIO(base64.b64decode(img.split(",")[1])))

    # image convert
    w, h = im.size
    clear_img = clear_filter(im, w, h)
    unclear_img = unclear_filter(clear_img, w, h)

    # image base64 convert
    buffered = BytesIO()
    unclear_img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())

    # return js
    return 'data:image/jpeg;base64,' + str(img_str)[2:len(str(img_str))-1]

# ell start
eel.start('convert.html', size=(800, 600))