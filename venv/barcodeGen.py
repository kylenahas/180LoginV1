import barcode
from PIL import Image, ImageDraw, ImageFont
from barcode.writer import ImageWriter
import subprocess, os, platform
from zebra import zebra

import config

# import win32print

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
        if not config.zebra_print_enabled:
            if platform.system() == "Windows":
                os.system("start " + fn)
            elif platform.system() == "Darwin":
                os.system("open " + fn)
        else:
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


    def print_zebra(self, member_id, name_str="Member Name", member_type_str="Member_type", dry_run=False):

        printer = zebra()

        z_design =  """CT~~CD,~CC^~CT~
        ^XA~TA000~JSN^LT0^MNW^MTD^PON^PMN^LH0,0^JMA^PR6,6~SD15^JUS^LRN^CI0^XZ
        ^XA
        ^MMT
        ^PW406
        ^LL0203
        ^LS0
        ^BY3,3,107^FT20,121^BCN,,Y,N
        ^FD>;""" + str(member_id) + """^FS
        ^FT8,187^A0N,28,28^FH\^FD""" + name_str[0:20] + """^FS
        ^FT262,187^A0N,28,28^FH\^FD""" + member_type_str[0:12] + """^FS
        ^PQ1,0,1,Y^XZ
        """

        if dry_run:
            print('Printer queues found:', printer.getqueues())
            print("ZPL Doc: ")
            print(z_design)
        else:
            printer.setqueue(config.zebra_printer_name)
            printer.setup(direct_thermal=True, label_height=(203, 32), label_width=406)  # 2" x 1" direct thermal label
            printer.output(z_design)




# f = open('./generated-barcode.png', 'wb')
# from barcode import generate

if __name__ == "__main__":
    bc = Barcoder()
    # bc.create_sticker_image(member_id="3229308233395595", name_str="Kyle Nahas", member_type_str="Volunteer")
    # bc.openAsDoc()
    # bc.print_zebra(member_id=6027415425816323)
    bc.print_zebra(member_id=6027415425816323, name_str="John Has A Really Long Name", member_type_str="Organization")