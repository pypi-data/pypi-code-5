from django.conf import settings
import os

import qrcode


class QRMixin(object):
    qr_image_field = "qr_image"
    qr_box_size = 2
    qr_border_size = 0
    qr_code_field = "code"

    def get_qr_code(self):
        return getattr(self, self.qr_code_field)

    def generate_qr(self):
        qr_code = self.get_qr_code()
        code_image = qrcode.make(
            qr_code,
            box_size=self.qr_box_size,
            border=self.qr_border_size
        )
        filename = "qr_{code}.png".format(code=qr_code)
        image_field = getattr(self, self.qr_image_field)
        rel_filename = image_field.field.generate_filename(self, filename)
        filename = os.path.join(
            settings.MEDIA_ROOT,
            rel_filename
        )
        try:
            dirname = os.path.dirname(filename)
            os.makedirs(dirname)
        except OSError:
            pass
        code_image.save(filename, "png")
        image_field = rel_filename

        print rel_filename

        return filename