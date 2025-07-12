import requests
import sys
import json
import os
import traceback

def delete_template_image(base_url, filename, filetype, api_token=None):
    url = f"{base_url.rstrip('/')}/api/v1/plugin/ProxmoxVEBackup/delete_template_image"
    headers = {
        "Content-Type": "application/json"
    }
    if api_token:
        headers["Authorization"] = f"Bearer {api_token}"
    data = {
        "filename": filename,
        "filetype": filetype
    }
    print(f"\n请求: {url}")
    print(f"参数: {json.dumps(data, ensure_ascii=False)}")
    print(f"请求头: {headers}")
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=20)
        print(f"HTTP状态码: {resp.status_code}")
        print("响应内容:")
        print(resp.text)
        if resp.status_code == 200:
            try:
                result = resp.json()
                if result.get("success"):
                    print("✅ 删除成功！")
                else:
                    print("❌ 删除失败，错误信息：", result.get("error"))
            except Exception as e:
                print("❌ 响应不是有效JSON，解析失败：", str(e))
        else:
            print("❌ 请求失败，状态码：", resp.status_code)
    except Exception as e:
        print("请求异常：")
        traceback.print_exc()

def main():
    if len(sys.argv) < 4:
        print("用法: python 1.py <后端地址> <类型> <文件名1> [<文件名2> ...] [--token=API_TOKEN]")
        print("例如: python 1.py http://192.168.8.253:3000 iso iKuai8_x64_3.7.20_Build202506041743.iso")
        sys.exit(1)

    base_url = sys.argv[1]
    filetype = sys.argv[2]
    api_token = None

    # 支持 --token=xxx 作为最后一个参数
    filenames = []
    for arg in sys.argv[3:]:
        if arg.startswith('--token='):
            api_token = arg.split('=', 1)[1]
        else:
            filenames.append(arg)

    # 也支持从环境变量读取API_TOKEN
    if not api_token:
        api_token = os.environ.get('API_TOKEN')

    for filename in filenames:
        delete_template_image(base_url, filename, filetype, api_token)

if __name__ == "__main__":
    main()
