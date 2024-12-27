在 src/spiders.py 下，注册爬虫，按照 ucr 的格式进行注册。

在 src/schools/下创建学校简称对应的文件夹，在里面存放对应学校的爬虫代码。

在 src/models.py 里，新建对应学校课程爬取后储存的表，模仿 ucr，记得继承 BaseDB。

你的代码爬取完成后，应该类似于 ucr.server.main 函数一样，返回一个 List[BaseDB]，并且在返回前，调用 src.process.post_process，进行后处理，进行 embedding 和 id 等添加。
