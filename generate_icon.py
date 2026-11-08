from PIL import Image, ImageDraw

def create_icon():
    # 256x256 हाई-क्वालिटी कैनवास
    size = (256, 256)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. गोल कोनों वाला डार्क-ब्लू ग्लास बैकग्राउंड कार्ड
    draw.rounded_rectangle([10, 10, 246, 246], radius=45, fill=(11, 15, 25, 240), outline=(0, 242, 254, 200), width=6)

    # 2. नियॉन सायन कैमरा अपर्चर रिंग
    draw.ellipse([50, 50, 206, 206], outline=(0, 242, 254, 255), width=10)
    draw.ellipse([80, 80, 176, 176], fill=(17, 24, 39, 255), outline=(255, 255, 255, 220), width=4)
    draw.ellipse([110, 110, 146, 146], fill=(0, 242, 254, 255))

    # 3. पिक्चर मैनेजर क्रॉप सिंबल
    draw.rectangle([40, 30, 110, 42], fill=(0, 242, 254, 255))
    draw.rectangle([30, 40, 42, 110], fill=(0, 242, 254, 255))
    draw.rectangle([146, 214, 216, 226], fill=(0, 242, 254, 255))
    draw.rectangle([214, 146, 226, 216], fill=(0, 242, 254, 255))

    # सेव करें Title bar के लिए PNG और Windows Exe के लिए ICO
    img.save("app_icon.png", format="PNG")
    img.save("app_icon.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print("Icon generated successfully!")

if __name__ == '__main__':
    create_icon()
