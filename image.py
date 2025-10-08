from PIL import Image

def load(filename):
    img = Image.open(filename)

    width = img.width
    height = img.height
    
    if(height>4096):
        img.thumbnail((3686, 4096), resample=Image.Resampling.NEAREST)
        width = 3686
        height = 4096

    img_data = img.convert("RGBA").transpose(Image.FLIP_TOP_BOTTOM).tobytes()
    

    

    return(img_data, width, height)