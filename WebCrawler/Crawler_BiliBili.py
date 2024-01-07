import gzip
import os
import json
import pprint
import zlib

import requests
import subprocess
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

# 你的视频URL
url = "https://www.bilibili.com/video/BV1dp4y1d7tf/?vd_source=b909f776d8a643c942d3780809fe5f3a"

# headers 是用来设置请求头信息的。通过设置请求头，可以模拟浏览器行为，伪装成浏览器发出的请求，避免被服务器识别为爬虫并屏蔽或限制访问
# 添加 User-Agent 字段，模拟不同浏览器的请求头信息，使爬虫请求看起来更像正常的浏览器请求。还可以模拟 cookie、referer、accept 等字段
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.bilibili.com/video/BV1dp4y1d7tf/?vd_source=b909f776d8a643c942d3780809fe5f3a',
    'Accept-Language': 'en-US,en;q=0.9',
}

try:
    # 通过requests模块发送请求，并携带headers伪装
    response = requests.get(url=url, headers=headers)
    response.raise_for_status()  # 检查请求是否成功
    play_info = response.text
    print(play_info)

    # # 通过 urllib 模块发送请求，并携带 headers 伪装
    # request = urllib.request.Request(url=url, headers=headers)
    # with urllib.request.urlopen(request) as response:
    #     # B站的html貌似是被压缩过的，所以需要使用gzip.decompress解压之后再decode
    #     play_info = gzip.decompress(response.read()).decode('utf-8')
    #     print(play_info)

    soup = BeautifulSoup(play_info, 'html.parser')

    video_link = soup.find('video')['src']
    audio_link = soup.find('audio')['src']

    video_content = requests.get(video_link).content
    audio_content = requests.get(audio_link).content

    title = "当你想卡点毕业却卡了个寄。。。？"  # 替换为实际的视频标题

    # 检查目录是否存在，不存在则创建
    video_directory = 'video'
    if not os.path.exists(video_directory):
        os.makedirs(video_directory)

    # 将音频和视频保存到文件
    with open(os.path.join(video_directory, f'{title}.mp4'), mode="wb") as f:
        f.write(video_content)
    with open(os.path.join(video_directory, f'{title}.mp3'), mode="wb") as f:
        f.write(audio_content)

    print('Audio and video saved successfully!')

    # 使用ffmpeg合并音频和视频
    output_file = os.path.join(video_directory, f'{title}output.mp4')
    command = f'ffmpeg -i {video_directory}/{title}.mp4 -i {video_directory}/{title}.mp3 -c:v copy -c:a aac -strict experimental {output_file}'
    subprocess.run(command, shell=True)
    print('Video merged successfully!')

except requests.RequestException as e:
    print(f"Error in requests: {e}")

except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")

except Exception as e:
    print(f"An error occurred: {e}")
