import requests
import json
import re
import os


def get_video_info(bvid):
    """获取视频信息"""
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.bilibili.com/"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = json.loads(response.text)

        if data['code'] != 0:
            print("获取视频信息失败:", data['message'])
            return None

        return data['data']
    except Exception as e:
        print("发生错误:", str(e))
        return None


def get_video_url(cid, bvid, quality=112):
    """获取视频下载地址"""
    url = f"https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&qn={quality}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.bilibili.com/"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = json.loads(response.text)

        if data['code'] != 0:
            print("获取下载地址失败:", data['message'])
            return None

        return data['data']['durl'][0]['url']  # 取第一个分片
    except Exception as e:
        print("发生错误:", str(e))
        return None


def download_video(url, title, output_dir="downloads"):
    """下载视频"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 清理非法文件名字符
    title = re.sub(r'[\\/:*?"<>|]', '', title)
    file_path = os.path.join(output_dir, f"{title}.flv")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.bilibili.com/"
    }

    try:
        with requests.get(url, headers=headers, stream=True) as response:
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))

            with open(file_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        print(f"下载进度: {downloaded / total_size * 100:.2f}%", end='\r')
                print("\n下载完成！")
        return file_path
    except Exception as e:
        print("下载失败:", str(e))
        return None


def main():
    # 输入B站视频BV号（例如：BV1wx411d7Fy）
    bvid = input("请输入B站视频BV号：").strip()

    # 获取视频信息
    video_info = get_video_info(bvid)
    if not video_info:
        return

    print(f"标题: {video_info['title']}")
    print(f"作者: {video_info['owner']['name']}")
    print(f"分P数量: {video_info['videos']}")

    # 选择分P（默认第一个）
    cid = video_info['pages'][0]['cid']

    # 获取下载地址（默认画质80：1080P）
    video_url = get_video_url(cid, bvid)
    if not video_url:
        return

    # 开始下载
    print("开始下载视频...")
    download_video(video_url, video_info['title'])


if __name__ == "__main__":
    main()