# movie_recommendation
## 项目简介
这是兰庆秋、秦霄潇、李思颀、周飞燕、章俊文在专业设计小学期中实现的一个电影推荐网站。

本项目建立了一个电影评分网站，模仿了MovieLens网站并使用**Movie Lens数据集**（ml-latest.zip, 264M）作为网站的初始数据进行电影展示和推荐。网站采用多种推荐算法，包括非个性化推荐和个性化推荐，为用户提供多种维度的电影推荐。网站拓展了个人主页模块，提供包括个人影评与电影评分在内的展示页面。

本项目前端基于主要基于 vue 和 element-ui实现。同时也使用了最新的前端技术栈，技术栈基于 ES2015+、vue、vuex、vue-router 、vue-cli 、axios 和 element-u。

本项目的后端主要基于python和fastapi，推荐算法共有5种：高分电影推荐、热门电影推荐、基于标签推荐、基于流派推荐、协同过滤推荐。用到的主要python库有，pyspark、pandas、numpy、gensim、pymongo等。

本项目的数据存储采用mongodb数据库，但由于文件大小限制，这里没有上传。

项目环境基于docker搭建了可以连接mongodb的spark集群，后端未部署服务器，运行在组内电脑上通过花生壳暴露给另一台电脑上的前端访问。

## 目录说明
```
-back_end(存放后端部分的代码)
    |----code(完整的网页后端代码)
    |     |----api(后端接口函数)
    |     |     |----rec.py: 5种推荐算法的接口
    |     |     |----user.py: 其他功能的接口
    |     |----rec_model_save(本地存放的模型)
    |     |----static(fastapi需要的资源)
    |     |----main.py: 后端入口函数
    |----lsq(李思颀同学的代码)
    |     |----cal_trend.py: 热门电影离线训练
    |     |----get_trend.py: 热门电影在线推荐
    |     |----cal_genre.py: 基于流派推荐离线训练
    |     |----get_user_genre.py: 基于流派推荐在线推荐
    |----zjw(章俊文同学的代码)
    |     |----gen_top250.py: 高分电影离线训练
    |     |----get_top.py: 高分电影在线推荐
    |     |----prepare_data.py: 标签推荐数据准备
    |     |----gen_movie_rec_by_tag.ipynb: 基于标签推荐离线训练并保存模型
    |     |----get_movie_rec_by_tag.py: 基于标签的推荐
    |     |----TagRec.model: 基于标签推荐在本地保存的模型 
-front_end(存放前端代码,可以用H-builder打开)
-第九组专业设计报告.doc: 项目报告
```
## 前端展示
![image](https://user-images.githubusercontent.com/72862074/211006397-90372ad8-7432-4950-93b5-b7ee31d5b87d.png)

![image](https://user-images.githubusercontent.com/72862074/211006459-7cb28d7c-9533-44ec-b5a0-cc957406e9ee.png)

![image](https://user-images.githubusercontent.com/72862074/211006482-4189489d-bc58-4d3f-8b2b-50e866fac7f8.png)

![image](https://user-images.githubusercontent.com/72862074/211006518-9e67394e-cbde-4c6a-b4fa-01ab2117c31f.png)

![image](https://user-images.githubusercontent.com/72862074/211006546-1a902d42-7501-48f1-97a5-dc0ec9905f1c.png)

![image](https://user-images.githubusercontent.com/72862074/211006575-15e165c6-eb8a-4610-a3bb-495e105cebea.png)


