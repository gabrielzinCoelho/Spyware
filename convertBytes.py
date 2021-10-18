import io
import json

class ConvertBytes:

    #Images should be objects Image of library PILLOW
    def encodeImage(self, img):
        imgByteArr = io.BytesIO()
        img.save(imgByteArr, format='JPEG')
        return imgByteArr.getvalue()

    def saveImage(self, imgBytes, path):
        f = open(path, 'wb')
        f.write(bytearray(imgBytes))
        f.close()
        return "Imagem salva com sucesso"

    def encodeJson(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def decodeJson(self, objBytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(objBytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj