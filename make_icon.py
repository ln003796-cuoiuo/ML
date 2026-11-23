from PIL import Image, ImageDraw

# Recreate the supplied monochrome square-face mark as a crisp multi-size Windows icon.
S = 512
im = Image.new("RGB", (S, S), "black")
d = ImageDraw.Draw(im)

# White outer frame
d.rectangle((70, 70, 469, 469), outline="white", width=15)
# Eyes
d.rectangle((129, 159, 221, 238), fill="white")
d.rectangle((317, 159, 412, 238), fill="white")
# Geometric lower face
d.rectangle((223, 239, 317, 279), fill="white")
d.rectangle((176, 279, 365, 398), fill="white")
# Mouth / lower notch
d.rectangle((225, 358, 318, 399), fill="black")

im.save("assets/logo.ico", format="ICO", sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])
