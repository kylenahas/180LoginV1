import barcode
from PIL import Image
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


# f = open('./generated-barcode.png', 'wb')
# from barcode import generate