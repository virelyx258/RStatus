#!/usr/bin/env python3
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import threading
import logging
import json
import os
import time

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 默认配置
DEFAULT_CONFIG = {
    "avatar_url": "https://example.com/avatar.jpg",
    "nick_name": "Custom Nickname",
    "flask_port": 5000,
    "background_image": "https://example.com/bg.jpg",
    "site_title": "RStatus Server",
    "page_title": "设备状态监控",
    "online_status": "在线",
    "offline_status": "离线",
    "online_text": "设备在线",
    "offline_text": "设备离线",
    "favicon_url": "https://example.com/favicon.webp"
}

# 尝试加载配置文件
config = DEFAULT_CONFIG.copy()
try:
    config_path = os.path.join(os.path.dirname(__file__), 'Config.json')
    with open(config_path, 'r', encoding='utf-8') as config_file:
        user_config = json.load(config_file)
        config.update(user_config)
except Exception as e:
    logging.warning(f"加载配置文件失败，使用默认配置: {str(e)}")

# 加载自定义CSS
def load_custom_css(file_name):
    try:
        css_path = os.path.join(os.path.dirname(__file__), file_name)
        with open(css_path, 'r', encoding='utf-8') as css_file:
            return css_file.read()
    except Exception as e:
        logging.warning(f"加载自定义CSS文件失败: {str(e)}")
        return ""

# 加载自定义JavaScript
def load_custom_javascript(file_name):
    try:
        js_path = os.path.join(os.path.dirname(__file__), file_name)
        with open(js_path, 'r', encoding='utf-8') as js_file:
            return js_file.read()
    except Exception as e:
        logging.warning(f"加载自定义JavaScript文件失败: {str(e)}")
        return ""

# 加载自定义HTML
def load_custom_html(file_name):
    try:
        html_path = os.path.join(os.path.dirname(__file__), file_name)
        with open(html_path, 'r', encoding='utf-8') as html_file:
            return html_file.read()
    except Exception as e:
        logging.warning(f"加载自定义HTML文件失败: {str(e)}")
        return ""

app = Flask(__name__)
CORS(app)

# 存储设备信息和设备对应的IP
devices = {}
device_ips = {}
lock = threading.Lock()

# HTML模板（修改后的版本）
def generate_html_template():
    # 扩展代码加载动态内容
    custom_css = load_custom_css(config.get("custom_css_file", ""))
    custom_javascript = load_custom_javascript(config.get("custom_javascript_file", ""))
    custom_html = load_custom_html(config.get("custom_html_file", ""))
    
    # HTML模板
    HTML_TEMPLATE = f'''
<!DOCTYPE html>
<html>
<head>
    <title>{config['site_title']}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: url('{config['background_image']}') center/cover no-repeat;
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
            display: flex;
            align-items: center;
            gap: 10px;  /* 添加间距 */
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
        {custom_css}
    </style>
    <link rel="icon" type="image/webp" href="{config['favicon_url']}">
</head>
<body>
    <div class="container">
        <h1>{config['page_title']}</h1>
        <div class="info-module">
            <div class="avatar-nickname">
                <img class="avatar" src="{config['avatar_url']}" alt="Avatar">
                <div class="nickname-container">
                    <span class="nickname">{config['nick_name']}</span>
                    <span class="sub-title" id="sub-title">{config['offline_text']}</span>
                </div>
            </div>
            <div id="status-indicator" class="status-offline">
                <div class="status-dot status-dot-offline"></div>
                {config['offline_status']}
            </div>
        </div>
        <div id="device-container"></div>
        <div id="update-time">更新时间：暂无</div>
    </div>
    <div class="copyright-container">{custom_html}
        Copyright © 2025 <a href="https://github.com/virelyx258/RStatus/" target="_blank">RStatus</a> Made By <a href="https://www.riseforever.cn/" target="_blank">RiseForever</a>.
    </div>
<script>
    function updateDevices() {{
        fetch('/get_devices')
           .then(response => {{
                if (!response.ok) throw new Error('Network error');
                return response.json();
            }})
           .then(data => {{
                const deviceContainer = document.getElementById('device-container');
                deviceContainer.innerHTML = '';
                for (const [deviceName, windowTitle] of Object.entries(data)) {{
                    const module = document.createElement('div');
                    module.classList.add('info-module');
                    module.innerHTML = `<span class="left-label">${{deviceName}}</span>
                        <div class="right-content">
                            <span onclick=\"showFullContent(this)\" 
                                data-full-content=\"${{windowTitle}}\">${{windowTitle.length > 20 ? windowTitle.substring(0,20)+'...' : windowTitle}}</span>
                        </div>`;
                    deviceContainer.appendChild(module);
                }}

                // 更新时间处理
                const now = new Date();
                document.getElementById('update-time').innerText = `更新时间：${{now.toLocaleString('zh-CN')}}`;

                // 状态更新逻辑
                const statusIndicator = document.getElementById('status-indicator');
                const statusDot = document.querySelector('.status-dot');
                const subTitle = document.getElementById('sub-title');
                if (Object.keys(data).length > 0) {{
                    statusIndicator.className = 'status-indicator status-alive';
                    statusDot.className = 'status-dot status-dot-alive';
                    statusIndicator.innerHTML = `<div class="status-dot status-dot-alive"></div>{config['online_status']}`;
                    subTitle.innerText = '{config['online_text']}';
                }} else {{
                    statusIndicator.className = 'status-indicator status-offline';
                    statusDot.className = 'status-dot status-dot-offline';
                    statusIndicator.innerHTML = `<div class="status-dot status-dot-offline"></div>{config['offline_status']}`;
                    subTitle.innerText = '{config['offline_text']}';
                }}
            }})
           .catch(error => {{
                console.error('Error:', error);
                document.getElementById('status-indicator').innerHTML = `<div class="status-dot status-dot-offline"></div>{config['offline_status']}`;
                document.getElementById('sub-title').innerText = '{config['offline_text']}';
            }});
    }}

    function showFullContent(element) {{
        alert(element.dataset.fullContent);
    }}

    

    setInterval(updateDevices, 3000);
    updateDevices();
    // 自定义Javascript
    {custom_javascript}
</script>
    
</body>
</html>
    '''
    return HTML_TEMPLATE

 

 

@app.route('/')
def home():
    return render_template_string(generate_html_template())

@app.route('/get_devices')
def get_devices():
    with lock:
        return jsonify(devices)

@app.after_request
def add_no_cache_headers(response):
	# 禁用浏览器缓存，确保前端轮询获取最新数据
	response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '0'
	return response

@app.route('/report', methods=['POST'])
def report():
	try:
		data = request.get_json(silent=True, force=True) or {}
		device_type = str(data.get('device_type', '')).strip()
		device_name = str(data.get('device_name', '')).strip()
		# 兼容字段拼写：优先 window_tittle，其次 window_title
		window_title = data.get('window_tittle')
		if window_title is None:
			window_title = data.get('window_title')

		if not device_type or not device_name or window_title is None:
			return jsonify({ 'success': False, 'error': '参数不完整' }), 400

		# 保留原有特殊请求处理：设备下线
		if window_title == "设备已下线":
			with lock:
				for key in [k for k in devices if device_name in k]:
					logging.info(f"设备离线: {key} (IP: {device_ips.get(key, ('-', '-'))[0]}:{device_ips.get(key, ('-', '-'))[1]})")
					if key in devices:
						del devices[key]
					if key in device_ips:
						del device_ips[key]
				# 无TCP模式，无需处理连接表
			return jsonify({ 'success': True })

		# 设备类型->表情符号映射（与TCP逻辑一致）
		emoji = '📱' if device_type == '1' else '💻' if device_type == '2' else None
		if not emoji:
			return jsonify({ 'success': False, 'error': '不支持的设备类型' }), 400

		display_name = f'{emoji}{device_name}'
		client_ip = request.remote_addr or '-'
		with lock:
			# 名称冲突处理：当同名但不同设备类型时迁移
			existing = next((k for k in devices if device_name in k), None)
			if existing and existing[0] != emoji:
				devices[display_name] = devices.pop(existing)
				if existing in device_ips:
					device_ips[display_name] = device_ips.pop(existing)
				# 无TCP模式，无需迁移连接表
			# 更新最新状态
			devices[display_name] = str(window_title)
			# POST模式下无持久TCP连接，这里仅记录来源IP
			device_ips[display_name] = (client_ip, 0)
			logging.info(f"设备上报: {display_name} (IP: {client_ip}) -> {window_title}")

		return jsonify({ 'success': True })
	except Exception as e:
		logging.error(f'/report 处理错误: {str(e)}')
		return jsonify({ 'success': False, 'error': str(e) }), 500

if __name__ == '__main__':
	# 改为通过HTTP POST接收客户端上报，不再默认启动TCP接收线程
	app.run(host='0.0.0.0', port=config['flask_port'], debug=False)