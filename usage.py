#-*- coding:utf-8 -*-
import asyncio
import json
import saucenao

api=saucenao.Saucenao()
async def test():
    a=await api.saucenao_search(r"C:\Users\bakashigure\Desktop\ss.jpg")
    a=eval(a)
    if(a['type']=='success'):
        _rate=a['rate']
        _index=a['index']
        _text="Found! %s\n"%_rate
        for k,v in a['data'][_index].items():
            _text+="%s: %s\n"%(k,v)
        print(_text)
    elif(a['type']=='warn'):
        _rate=a['rate']
        _text="Not Found. %s\n"%_rate
        _text+=a['message']
        print(_text)
    elif(a['type']=='error'):
        _text="Error\n"+a['message']
        print(_text)          



asyncio.run(test())

