#!/usr/bin/env python3
from flask import Flask, render_template, jsonify, request
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

@app.route('/')
def home():
    custom_css = load_custom_css(config.get("custom_css_file", ""))
    custom_javascript = load_custom_javascript(config.get("custom_javascript_file", ""))
    custom_html = load_custom_html(config.get("custom_html_file", ""))
    return render_template(
        'index.html',
        site_title=config['site_title'],
        page_title=config['page_title'],
        avatar_url=config['avatar_url'],
        nick_name=config['nick_name'],
        background_image=config['background_image'],
        favicon_url=config['favicon_url'],
        offline_text=config['offline_text'],
        offline_status=config['offline_status'],
        online_text=config['online_text'],
        online_status=config['online_status'],
        custom_css=custom_css,
        custom_javascript=custom_javascript,
        custom_html=custom_html,
    )

 

 

 

@app.route('/get_devices')
def get_devices():
    with lock:
        return jsonify(devices)

@app.route('/api/status')
def api_status():
    # 返回 { devices, status, updateTime }
    with lock:
        device_list = []
        for display_name, window_title in devices.items():
            # 解析设备类型与纯设备名
            if display_name.startswith('📱'):
                device_type = 'mobile'
                device_name = display_name[1:]
            elif display_name.startswith('💻'):
                device_type = 'pc'
                device_name = display_name[1:]
            else:
                device_type = 'unknown'
                device_name = display_name

            device_list.append({
                'name': device_name,
                'type': device_type,
                'windowTitle': window_title,
            })

    overall_status = 'online' if len(device_list) > 0 else 'offline'
    update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    return jsonify({
        'devices': device_list,
        'status': overall_status,
        'updateTime': update_time,
    })

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