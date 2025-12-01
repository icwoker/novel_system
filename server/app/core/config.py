"""
1、用于读取env中的数据
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME:str
    DATABASE_URL:str
    #以后添加配置，在这里加
    
    class Config:
        eve_file = ".env"#读取根目录下的.env文件

#实例化，导出setting对象
settings = Settings()