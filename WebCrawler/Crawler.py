import os
import urllib.request
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# Requests: 用于发送HTTP请求的库，简化了与Web服务的通信。
# Beautiful Soup: 用于从HTML或XML中提取数据的库，提供了方便的方法来浏览文档、搜索特定标签或提取信息。
# Scrapy: 一个开源的、基于Python的爬虫框架，用于快速高效地提取数据。
# Selenium: 用于自动化浏览器操作的库，适用于需要JavaScript渲染的网页爬取。
# Lxml: 用于处理XML和HTML的库，通常与Beautiful Soup一起使用，以提供更快的解析速度。

url = "https://blog.csdn.net/awofe/article/details/128478906"


def get_image(http_url):
    # 目标网站的URL

    # 发送HTTP GET请求获取网页内容（urllib/requests/httplib2/http.client/Treq）
    # urllib 库：用 urllib.request.urlopen 发送简单的 HTTP 请求。使用 urllib.request.Request 构建更复杂的请求。
    # Requests 库：requests 是一个流行的第三方库，提供了更简洁和友好的 API，支持多种 HTTP 方法。
    # httplib2 库：httplib2 是另一个支持 HTTP 请求的库，支持缓存等功能。
    # http.client 模块：http.client 是 Python 标准库中的模块，用于处理 HTTP 请求。
    # Treq 库：treq 是基于 Twisted 的库，提供异步的 HTTP 请求。

    # 1. 使用requests库发送URL请求
    # response = requests.get(http_url)
    # if response.status_code == 200:
    #     html_content = response.text

    # 2. 使用urllib库发送URL请求，应对一些试用requests库的请求无法访问的情况
    response = urllib.request.urlopen(http_url)
    if response.status == 200:
        html_content = response.read().decode("utf-8")
        print(html_content)

        # 创建一个BeautifulSoup对象解析网页
        soup = BeautifulSoup(html_content, "html.parser")

        # 选择图片标签，通常是 <img> 标签
        img_tags = soup.find_all("img")

        # 本地保存图片的文件夹路径
        save_folder = "images"

        # 创建文件夹（如果不存在）
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        # 遍历所有图片标签并下载图片
        for img_tag in img_tags:
            # 获取图片的URL
            # img_url = img_tag.get("src")
            img_url = img_tag.get("src")

            # 使用urljoin函数来构建完整的图片URL
            img_url = urljoin(url, img_url)

            # 发送HTTP GET请求下载图片
            img_response = requests.get(img_url)

            if img_response.status_code == 200:
                # 获取文件名（通常从URL中提取）
                img_filename = os.path.join(save_folder, os.path.basename(img_url))

                # 保存图片到本地文件夹
                with open(img_filename, "wb") as img_file:
                    img_file.write(img_response.content)
                    print(f"已下载图片: {img_filename}")
            else:
                print(f"无法下载图片: {img_url}")
    else:
        print("无法访问网站")


if __name__ == '__main__':
    get_image(url)
