import PIL
from PIL import Image
from pyzbar.pyzbar import decode
from pathlib import Path
import re
import cv2

def parseSingleQR(file : Path) -> tuple[str, bool]:
    """ based on a file, determine if whether the file contains a valid QR Code 
        and return the corresponding URL, if any, defanged. """
    
    try:
        fileExif = decode(Image.open(file))
    except PIL.UnidentifiedImageError:
        return "File supplied is not a valid image or QR Code.", False
    else:
        # print(fileExif)
        if fileExif == []:
            img = cv2.imread(str(file.resolve()))
            opencvQRDetect = cv2.QRCodeDetector()
            retVal, decodedInfo, _ , _ = opencvQRDetect.detectAndDecodeMulti(img)

            # QR Code not present in image
            if not retVal:
                # print('cv2 decoded: ', retVal, decodedInfo)
                return "File either is not or does not contain valid a QR Code.", False
            else:
                # print('cv2 decoded: ', retVal, decodedInfo[0])
                uri_pattern = r"^(?:https?|hxxps?):\/\/(?:\[\.\]|\[\.\]\[\.\]|[^\[\]])+|(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?)(?:$|\s)"
                if re.match(uri_pattern, decodedInfo[0]): # not sure if need change index
                    return defangURL(decodedInfo[0]), True
                return "No url detected in QR Code.", False

        # check type of image and if data field exists
        if fileExif[0].type == "QRCODE" and fileExif[0].data:
            rawData = fileExif[0].data.decode()
            uri_pattern = r"^(?:https?|hxxps?):\/\/(?:\[\.\]|\[\.\]\[\.\]|[^\[\]])+|(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?)(?:$|\s)"
            if re.match(uri_pattern, rawData):
                return defangURL(rawData), True
            return "No url detected in QR Code.", False
        return "File either is not or does not contain valid a QR Code.", False
    

# utility function
def defangURL(rawUrl : str) -> str:
    return rawUrl.replace(".", "[.]").replace("http", "hxxp")

if __name__ == "__main__":
    parseSingleQR()