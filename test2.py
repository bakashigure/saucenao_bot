from saucenao_api import SauceNao
from saucenao_api.params import DB, Hide, BgColor
import secret
import cv2
from io import BytesIO

sauce = SauceNao(api_key=secret.APIKEY,          # Optional[str] 
                 testmode=0,            # int
                 dbmask=None,           # Optional[int]
                 dbmaski=None,          # Optional[int]
                 db=DB.Twitter,             # int
                 numres=6,              # int
                 frame=1,               # int
                 hide=Hide.NONE,        # int
                 bgcolor=BgColor.NONE,  # int
)
result=''
img_url=r'C:\Users\bakashigure\Desktop\dk.jpg'
with open(img_url,'rb') as f:
    img=f.read()
    bi=BytesIO(img)
    result=sauce.from_file(bi)
    print(result)
