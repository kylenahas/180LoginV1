import barcode
from PIL import Image, ImageDraw, ImageFont
from barcode.writer import ImageWriter
import subprocess, os, platform

# code128 = barcode.get_barcode_class("code128")

# bc = code128(u'3229308233395595')
# bc = code128(u'3229308233395595', writer=ImageWriter())

# print(code128.save(bc, filename='ean13_barcode'))

class Barcoder:
    def create_barcode(self, member_id, fn="member_barcode"):
        code128 = barcode.get_barcode_class("code128")
        bc = code128(str(member_id), writer=ImageWriter())
        code128.save(bc, filename=fn)

    def open_barcode(self, fn="member_barcode.png"):
        if platform.system() == "Windows":
            os.system("start " + fn)
        elif platform.system() == "Darwin":
            os.system("open " + fn)
        pass

    def create_sticker_image(self, member_id, name_str="Member Name", member_type_str="Member_type", fn="member_sticker"):
        code128 = barcode.get_barcode_class("code128")
        bc = code128(str(member_id), writer=ImageWriter())
        code128.save(bc, filename="exported_barcodes/"+fn+"_barcode")

        bc_img = Image.open("exported_barcodes/"+fn+"_barcode.png")

        dpi = 300
        size = (2 * dpi, 2 * dpi)

        resized = bc_img.resize((2*dpi, dpi))

        sticker = Image.new("RGB", size, color="white")
        fnt = ImageFont.truetype('OpenSans-Semibold.ttf', 50)

        d = ImageDraw.Draw(sticker)

        text_size = fnt.getsize(name_str)
        x_offset = int((size[0] - text_size[0]) / 2)
        d.text((x_offset, int(dpi / 5)), name_str, font=fnt, fill="black")

        sticker.paste(resized, (0, int(dpi * 0.6)))

        text_size = fnt.getsize(member_type_str)
        x_offset = int((size[0] - text_size[0]) / 2)
        d.text((x_offset, (2*dpi - dpi/3)), member_type_str, font=fnt, fill="black")



        sticker.save(fp="exported_stickers/"+fn+".png", dpi=(dpi, dpi))


# f = open('./generated-barcode.png', 'wb')
# from barcode import generate

if __name__ == "__main__":
    bc = Barcoder()
    bc.create_sticker_image(member_id="3229308233395595", name_str="Kyle Nahas", member_type_str="Volunteer")