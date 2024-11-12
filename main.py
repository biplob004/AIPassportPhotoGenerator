# !wget https://github.com/camenduru/BRIA-RMBG-1.4-hf/raw/main/briarmbg.py -O briarmbg.py
# !wget https://github.com/camenduru/BRIA-RMBG-1.4-hf/raw/main/input.jpg -O input.jpg
# Reference code: https://colab.research.google.com/github/camenduru/bria-rmbg-jupyter/blob/main/bria_rmbg_jupyter.ipynb

import numpy as np
import torch
import torch.nn.functional as F
from torchvision.transforms.functional import normalize
from huggingface_hub import hf_hub_download
import gradio as gr
from briarmbg import BriaRMBG
import cv2
from PIL import Image
from typing import Tuple
import time 
from crop_portrait import crop_portrait

net=BriaRMBG()
model_path = hf_hub_download("briaai/RMBG-1.4", 'model.pth')

if torch.cuda.is_available():
    net.load_state_dict(torch.load(model_path))
    net=net.cuda()
else:
    net.load_state_dict(torch.load(model_path,map_location="cpu"))
net.eval() 
    
def resize_image(image):
    image = image.convert('RGB')
    model_input_size = (1024, 1024)
    image = image.resize(model_input_size, Image.BILINEAR)
    return image

def remove_bg(input_image, background_color=(255, 255, 255)):
    w,h = orig_im_size = input_image.size
    image = resize_image(input_image)
    im_np = np.array(image)
    im_tensor = torch.tensor(im_np, dtype=torch.float32).permute(2,0,1)
    im_tensor = torch.unsqueeze(im_tensor,0)
    im_tensor = torch.divide(im_tensor,255.0)
    im_tensor = normalize(im_tensor,[0.5,0.5,0.5],[1.0,1.0,1.0])
    if torch.cuda.is_available():
        im_tensor=im_tensor.cuda()

    result=net(im_tensor)
    result = torch.squeeze(F.interpolate(result[0][0], size=(h,w), mode='bilinear') ,0)
    ma = torch.max(result)
    mi = torch.min(result)
    result = (result-mi)/(ma-mi)    
    im_array = (result*255).cpu().data.numpy().astype(np.uint8)
    pil_im = Image.fromarray(np.squeeze(im_array))

    new_im = Image.new("RGBA", pil_im.size, (* background_color, 0))
    new_im.paste(input_image, mask=pil_im)

    filled_image = Image.new("RGB", new_im.size, background_color)
    filled_image.paste(new_im, (0, 0), new_im) 

    return filled_image


# ------------------------ Edit input file name here ----------------
img_file = 'imgs/4.jpg'
cropped_img = crop_portrait(cv2.imread(img_file))
output = remove_bg(cropped_img, background_color=(0, 255, 0))

output_fname = img_file.split('/')[-1].replace('.png', '').replace('.jpg', '').replace('.jpeg', '')
output.save(f'outputs/{output_fname}.png')


