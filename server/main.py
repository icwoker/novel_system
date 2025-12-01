from fastapi import FastAPI

#1、创建应用实例
app = FastAPI()

#2、定义访问根路径

@app.get('/')
async def root():
    return {"message":"hello world","status":"ok"}

# 3、定义一个带参数的路径
@app.get('/items/{item_id}')
async def read_item(item_id:int):
    return {"item_id":item_id,"name":"测试商品"}


