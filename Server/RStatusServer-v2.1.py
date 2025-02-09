#!/usr/bin/env python3
import json
from flask import Flask, render_template_string, jsonify
from flask_cors import CORS
import socket
import threading
import logging
import os

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)  # 启用 CORS

# 存储设备信息
devices = {}
# 创建线程锁
lock = threading.Lock()

# 读取配置文件
def read_config():
    """读取配置文件 Config.json"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, 'Config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        logging.error("Config.json 文件未找到，请检查文件路径。")
        return {}
    except json.JSONDecodeError:
        logging.error("Config.json 文件格式错误，请检查文件内容。")
        return {}

config = read_config()
# 获取配置信息
avatar_url = config.get('站长头像地址', '')
nickname = config.get('站长昵称', '请更改站长昵称')
tcp_port = config.get('TCP服务器端口', 19198)
flask_port = config.get('Flask服务器端口', 5000)
background_image_url = config.get('背景图片地址', '')
site_title = config.get('站点标题', '请更改站点标题')
page_title = config.get('页面标题', '请在服务器目录下Config.json更改页面标题')
online_text = config.get('在线中状态文本', '在线中')
offline_text = config.get('下线了状态文本', '下线了')
online_status_text = config.get('在线时的状态文本', '目前在线，可以交流。')
offline_status_text = config.get('离线时的状态文本', '目前离线，有事请留言。')

# HTML模板,包含现代化CSS样式和动效以及最新更新时间
HTML_TEMPLATE = f'''
<!DOCTYPE html>
<html>

<head>
    <title>{site_title}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0"> <!-- 添加viewport元标签以适配手机端 -->
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: url('{background_image_url}') center/cover no-repeat;
            margin: 0;
            padding: 20px;
            min-height: calc(100vh - 40px);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }}

        .container,
        .copyright-container {{
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            text-align: center;
            max-width: 600px;
            width: 90%;
            transition: all 0.3s ease;
        }}

        .container:hover,
        .copyright-container:hover {{
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
        }}

        h1 {{
            color: #222;
            margin-bottom: 20px;
            position: relative;
        }}

        #window-title,
        .info-module {{
            font-size: 1.2em;
            color: #333;
            padding: 15px;
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(1px);
            border-radius: 8px;
            margin: 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255, 255, 255, 0.7);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            transition: box-shadow 0.3s ease;
        }}

        #window-title:hover,
        .info-module:hover {{
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }}

        #window-title .left-label,
        .info-module .left-label {{
            color: #222;
        }}

        #window-title .right-content,
        .info-module .right-content {{
            text-align: right;
            cursor: pointer;
        }}

        #update-time {{
            font-size: 0.9em;
            color: #555;
            margin-top: 5px;
        }}

        .pinyin {{
            font-size: 0.6em;
            position: absolute;
            top: -0.8em;
            left: 50%;
            transform: translateX(-50%);
            color: #444;
        }}

        .avatar-nickname {{
            display: flex;
            align-items: center;
            justify-content: flex-start;
            flex-grow: 1;
        }}

        .avatar {{
            width: 50px;
            height: 50px;
            border-radius: 50%;
            margin-right: 10px;
        }}

        .nickname-container {{
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            margin-left: 10px;
        }}

        .nickname {{
            font-size: 1.2em;
            color: #222;
        }}

        .sub-title {{
            font-size: 0.8em;
            color: #444;
            display: block;
        }}

        .status-indicator {{
            padding: 5px 10px;
            border-radius: 8px;
            color: black;
            background: rgba(246, 211, 101, 0.5);
            border: 2px solid transparent;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            display: flex;
            align-items: center;
            transition: box-shadow 0.3s ease;
        }}

        .status-indicator:hover {{
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }}

        .status-alive {{
            border-color: green;
        }}

        .status-offline {{
            border-color: red;
        }}

        .status-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
            display: inline-block;
        }}

        .status-dot-alive {{
            background-color: green;
        }}

        .status-dot-offline {{
            background-color: red;
        }}

        #device-container {{
            max-height: 300px;
            overflow-y: auto;
            padding: 10px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(5px);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            transition: box-shadow 0.3s ease;
        }}

        #device-container:hover {{
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }}

        #device-container::-webkit-scrollbar {{
            width: 8px;
        }}

        #device-container::-webkit-scrollbar-track {{
            background: rgba(255, 255, 255, 0.3);
            border-radius: 8px;
        }}

        #device-container::-webkit-scrollbar-thumb {{
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
        }}

        #device-container::-webkit-scrollbar-thumb:hover {{
            background: rgba(0, 0, 0, 0.3);
        }}

        .copyright-container {{
            margin-top: 20px;
        }}

        .copyright-container a {{
            color: #222;
            text-decoration: none;
        }}

        .copyright-container a:hover {{
            text-decoration: underline;
        }}

        @media (max-width: 600px) {{
            body {{
                padding: 10px;
            }}

            .container,
            .copyright-container {{
                padding: 20px;
            }}

            .info-module {{
                flex-direction: column;
            }}

            .avatar-nickname {{
                flex-direction: column;
                align-items: center;
                margin-bottom: 10px;
            }}

            .nickname-container {{
                align-items: center;
                margin-left: 0;
            }}

            .status-indicator {{
                margin-top: 10px;
            }}

            #window-title,
            .info-module {{
                flex-direction: column;
            }}

            #window-title .left-label,
            .info-module .left-label {{
                margin-bottom: 5px;
            }}

            #window-title .right-content,
            .info-module .right-content {{
                text-align: center;
            }}
        }}
    </style>
    <link rel="icon" type="image/webp" href="https://www.riseforever.cn/wp-content/uploads/2024/12/65a799ce09060f728193a3146c6d0f15.webp">
</head>

<body>
    <div class="container">
        <h1>{page_title}</h1>
        <div class="info-module">
            <div class="avatar-nickname">
                <img class="avatar" src="{avatar_url}" alt="Avatar">
                <div class="nickname-container">
                    <span class="nickname">{nickname}</span>
                    <span class="sub-title" id="sub-title">{offline_status_text}</span> <!-- 添加副标题 -->
                </div>
            </div>
            <div id="status-indicator" class="status-offline">
                <div class="status-dot status-dot-offline"></div>
                {offline_text}
            </div>
        </div>
        <div id="device-container">
            <!-- 设备模块将动态添加到这里 -->
        </div>
        <div id="update-time">更新时间：暂无</div>
    </div>
    <div class="copyright-container">
        Copyright © 2025 <a href="https://github.com/Rise-forever/RStatus/" target="_blank">RStatus</a> Made By <a href="https://www.riseforever.cn/" target="_blank">Riseforever</a>.
    </div>
<script>
    function updateDevices() {{
        fetch('/get_devices')
           .then(response => {{
                if (!response.ok) {{
                    throw new Error('Network response was not ok');
                }}
                return response.json();
            }})
           .then(data => {{
                const deviceContainer = document.getElementById('device-container');
                deviceContainer.innerHTML = '';
                for (const [deviceName, windowTitle] of Object.entries(data)) {{
                    const module = document.createElement('div');
                    module.classList.add('info-module');
                    module.innerHTML = `
                        <span class="left-label">${{deviceName}}</span>
                        <span class="right-content" onclick="showFullContent(this)" data-full-content="${{windowTitle}}">${{windowTitle.length > 20 ? windowTitle.substring(0, 20) + '...' : windowTitle}}</span>
                    `;
                    deviceContainer.appendChild(module);
                }}
                // 获取当前时间并格式化为年月日时分秒
                const now = new Date();
                const year = now.getFullYear();
                const month = String(now.getMonth() + 1).padStart(2, '0');
                const day = String(now.getDate()).padStart(2, '0');
                const hours = String(now.getHours()).padStart(2, '0');
                const minutes = String(now.getMinutes()).padStart(2, '0');
                const seconds = String(now.getSeconds()).padStart(2, '0');
                const updateTime = `${{year}}-${{month}}-${{day}} ${{hours}}:${{minutes}}:${{seconds}}`;
                document.getElementById('update-time').innerText = `更新时间：${{updateTime}}`;

                // 更新在线状态
                const statusIndicator = document.getElementById('status-indicator');
                const statusDot = document.querySelector('.status-dot');
                const subTitle = document.getElementById('sub-title');
                if (Object.keys(data).length > 0) {{
                    statusIndicator.classList.remove('status-offline');
                    statusIndicator.classList.add('status-alive');
                    statusDot.classList.remove('status-dot-offline');
                    statusDot.classList.add('status-dot-alive');
                    statusIndicator.innerHTML = '<div class="status-dot status-dot-alive"></div>{online_text}';
                    subTitle.innerText = '{online_status_text}';
                }} else {{
                    statusIndicator.classList.remove('status-alive');
                    statusIndicator.classList.add('status-offline');
                    statusDot.classList.remove('status-dot-alive');
                    statusDot.classList.add('status-dot-offline');
                    statusIndicator.innerHTML = '<div class="status-dot status-dot-offline"></div>{offline_text}';
                    subTitle.innerText = '{offline_status_text}';
                }}
            }})
           .catch(error => {{
                console.error('Error updating devices:', error);
                // 如果发生错误，确保状态显示为离线
                const statusIndicator = document.getElementById('status-indicator');
                const statusDot = document.querySelector('.status-dot');
                const subTitle = document.getElementById('sub-title');
                statusIndicator.classList.remove('status-alive');
                statusIndicator.classList.add('status-offline');
                statusDot.classList.remove('status-dot-alive');
                statusDot.classList.add('status-dot-offline');
                statusIndicator.innerHTML = '<div class="status-dot status-dot-offline"></div>{offline_text}';
                subTitle.innerText = '{offline_status_text}';
            }});
    }}

    function showFullContent(element) {{
        const fullContent = element.dataset.fullContent;
        alert(`${{fullContent}}`);
    }}

    // 每3秒更新一次
    setInterval(updateDevices, 3000);
    updateDevices();  // 立即执行一次
</script>
</body>
</html>
'''


def handle_tcp_connection():
    """处理 TCP 连接，接收特定格式的消息并更新全局变量"""
    pass  # function body is omitted


@app.route('/')
def home():
    """主页路由"""
    return HTML_TEMPLATE


@app.route('/get_devices')
def get_devices():
    """返回所有设备信息的 API"""
    pass  # function body is omitted


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(port=flask_port)