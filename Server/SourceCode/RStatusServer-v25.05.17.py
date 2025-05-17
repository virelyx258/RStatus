#!/usr/bin/env python3
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import socket
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
    "tcp_port": 8080,
    "flask_port": 5000,
    "background_image": "https://example.com/bg.jpg",
    "enable_harassment": False,  # 新增配置项，用于控制是否开启在线骚扰功能
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

# 存储设备信息和设备对应的IP和端口
devices = {}
device_ips = {}
active_connections = {}  # 新增：存储活动连接
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

        /* 添加消息发送按钮样式 */
        .message-btn {{
            background: none;
            border: 1px solid transparent;
            cursor: pointer;
            padding: 8px;
            margin-left: 10px;
            color: #666;
            transition: all 0.2s ease;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 36px;
            height: 36px;
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.8);
        }}

        .message-btn:hover {{
            color: #333;
            background: rgba(255, 255, 255, 0.95);
            border-color: #4CAF50;
        }}

        .message-btn:active {{
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.15);
            transform: translateY(1px);
            border-color: #45a049;
        }}

        /* 消息发送弹窗样式 */
        .message-modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
        }}

        .message-modal-content {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 20px;
            border-radius: 10px;
            width: 80%;
            max-width: 500px;
            box-sizing: border-box;
        }}

        .message-modal input,
        .message-modal textarea {{
            width: calc(100% - 20px);
            padding: 8px 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }}

        .message-modal textarea {{
            height: 100px;
            resize: vertical;
        }}

        .message-modal-buttons {{
            text-align: right;
            margin-top: 15px;
            padding-right: 10px;
        }}

        .message-modal-buttons button {{
            padding: 8px 15px;
            margin-left: 10px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }}

        .send-btn {{
            background: #4CAF50;
            color: white;
        }}

        .cancel-btn {{
            background: #f44336;
            color: white;
        }}

        /* 添加成功提示弹窗样式 */
        .success-modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
        }}

        .success-modal-content {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 30px;
            border-radius: 15px;
            width: 300px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            animation: successPopup 0.3s ease-out;
        }}

        @keyframes successPopup {{
            0% {{
                transform: translate(-50%, -50%) scale(0.8);
                opacity: 0;
            }}
            100% {{
                transform: translate(-50%, -50%) scale(1);
                opacity: 1;
            }}
        }}

        .success-icon {{
            font-size: 48px;
            color: #4CAF50;
            margin-bottom: 15px;
        }}

        .success-message {{
            font-size: 18px;
            color: #333;
            margin-bottom: 20px;
        }}

        .success-modal-buttons {{
            text-align: center;
        }}

        .success-modal-buttons button {{
            padding: 8px 20px;
            border: none;
            border-radius: 5px;
            background: #4CAF50;
            color: white;
            cursor: pointer;
            transition: background 0.3s ease;
        }}

        .success-modal-buttons button:hover {{
            background: #45a049;
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
        Copyright © 2025 <a href="https://github.com/Rise-forever/RStatus/" target="_blank">RStatus</a> Made By <a href="https://www.riseforever.cn/" target="_blank">Riseforever</a>.
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
                            <span onclick="showFullContent(this)" 
                                data-full-content="${{windowTitle}}">${{windowTitle.length > 20 ? windowTitle.substring(0,20)+'...' : windowTitle}}</span>
                            <button class="message-btn" onclick="showMessageModal('${{deviceName}}')" title="发送消息">
                                📢
                            </button>
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

    // 添加消息发送相关函数
    function showMessageModal(deviceName) {{
        const modal = document.getElementById('messageModal');
        const title = document.getElementById('messageModalTitle');
        title.textContent = `向${{deviceName}}发送消息`;
        modal.style.display = 'block';
        modal.dataset.deviceName = deviceName;
    }}

    function closeMessageModal() {{
        const modal = document.getElementById('messageModal');
        modal.style.display = 'none';
    }}

    function sendMessage() {{
        const modal = document.getElementById('messageModal');
        const deviceName = modal.dataset.deviceName;
        const senderName = document.getElementById('senderName');
        const messageContent = document.getElementById('messageContent');

        if (!senderName.value || !messageContent.value) {{
            alert('请填写完整信息！');
            return;
        }}

        fetch('/send_message', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json',
            }},
            body: JSON.stringify({{
                device_name: deviceName,
                sender_name: senderName.value,
                message: messageContent.value
            }})
        }})
        .then(response => response.json())
        .then(data => {{
            if (data.success) {{
                // 清空输入框
                senderName.value = '';
                messageContent.value = '';
                closeMessageModal();
                showSuccessModal();
            }} else {{
                alert('消息发送失败：' + data.error);
            }}
        }})
        .catch(error => {{
            alert('发送失败：' + error);
        }});
    }}

    function showSuccessModal() {{
        const successModal = document.getElementById('successModal');
        successModal.style.display = 'block';
        setTimeout(() => {{
            successModal.style.display = 'none';
        }}, 2000);
    }}

    setInterval(updateDevices, 3000);
    updateDevices();
    // 自定义Javascript
    {custom_javascript}
</script>
<!-- 添加消息发送弹窗 -->
<div id="messageModal" class="message-modal">
    <div class="message-modal-content">
        <h2 id="messageModalTitle">发送消息</h2>
        <input type="text" id="senderName" placeholder="请输入您的昵称">
        <textarea id="messageContent" placeholder="请输入消息内容"></textarea>
        <div class="message-modal-buttons">
            <button class="cancel-btn" onclick="closeMessageModal()">取消</button>
            <button class="send-btn" onclick="sendMessage()">发送</button>
        </div>
    </div>
</div>
<!-- 添加成功提示弹窗 -->
<div id="successModal" class="success-modal">
    <div class="success-modal-content">
        <div class="success-icon">✓</div>
        <div class="success-message">消息发送成功！</div>
        <div class="success-modal-buttons">
            <button onclick="document.getElementById('successModal').style.display='none'">确定</button>
        </div>
    </div>
</div>
</body>
</html>
    '''
    return HTML_TEMPLATE

def handle_tcp_connection():
    global devices, device_ips, active_connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', config['tcp_port']))
    server_socket.listen(5)  # 允许最多5个等待连接
    logging.info(f'TCP服务启动于端口 {config["tcp_port"]}')
    
    def handle_client(conn, addr):
        try:
            while True:
                data = conn.recv(1024).decode('utf-8')
                if not data: 
                    logging.info(f"连接断开: {addr[0]}:{addr[1]}")
                    break
                logging.info(f"收到数据: {data}")
                
                if data.startswith('NewForm{}'):
                    parts = data.split('{}')
                    if len(parts) == 4:
                        device_type, device_name, window_title = parts[1], parts[2], parts[3]
                        
                        if window_title == "设备已下线":
                            with lock:
                                for key in [k for k in devices if device_name in k]:
                                    logging.info(f"设备离线: {key} (IP: {device_ips[key][0]}:{device_ips[key][1]})")
                                    del devices[key]
                                    if key in device_ips:
                                        del device_ips[key]
                                    if key in active_connections:
                                        del active_connections[key]
                            continue
                            
                        emoji = '📱' if device_type == '1' else '💻' if device_type == '2' else None
                        if not emoji: continue
                            
                        display_name = f'{emoji}{device_name}'
                        with lock:
                            # 处理设备名称冲突
                            existing = next((k for k in devices if device_name in k), None)
                            if existing and existing[0] != emoji:
                                devices[display_name] = devices.pop(existing)
                                if existing in device_ips:
                                    device_ips[display_name] = device_ips.pop(existing)
                                if existing in active_connections:
                                    active_connections[display_name] = active_connections.pop(existing)
                            devices[display_name] = window_title
                            device_ips[display_name] = addr
                            active_connections[display_name] = conn  # 存储活动连接
                            logging.info(f"设备上线: {display_name} (IP: {addr[0]}:{addr[1]})")
        except Exception as e:
            logging.error(f'连接处理错误: {str(e)}')
        finally:
            # 断开时清理
            with lock:
                for key, c in list(active_connections.items()):
                    if c == conn:
                        del active_connections[key]
                        if key in devices:
                            del devices[key]
                        if key in device_ips:
                            del device_ips[key]
            conn.close()
            logging.info(f"连接关闭: {addr[0]}:{addr[1]}")
    
    while True:
        try:
            conn, addr = server_socket.accept()
            logging.info(f'新连接: {addr[0]}:{addr[1]}')
            # 为每个新连接创建一个新线程
            client_thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            client_thread.start()
        except Exception as e:
            logging.error(f'接受连接错误: {str(e)}')
            continue

@app.route('/send_message', methods=['POST'])
def send_message():
    if not config.get('enable_harassment', False):
        return jsonify({'success': False, 'error': '在线骚扰功能未启用'})
        
    data = request.get_json()
    device_name = data.get('device_name')
    sender_name = data.get('sender_name')
    message = data.get('message')
    
    if not all([device_name, sender_name, message]):
        return jsonify({'success': False, 'error': '参数不完整'})
    
    with lock:
        if device_name not in devices:
            return jsonify({'success': False, 'error': '设备未连接'})
        
        try:
            if device_name not in active_connections:
                return jsonify({'success': False, 'error': '设备连接已断开'})
            
            conn = active_connections[device_name]
            message_data = f'NewMessage{{RST}}{sender_name}{{RST}}{message}'
            
            try:
                conn.send(message_data.encode('utf-8'))
                logging.info(f"消息发送成功")
                return jsonify({'success': True})
            except Exception as e:
                logging.error(f"发送消息失败: {str(e)}")
                # 如果发送失败，清理连接
                if device_name in devices:
                    del devices[device_name]
                if device_name in device_ips:
                    del device_ips[device_name]
                if device_name in active_connections:
                    del active_connections[device_name]
                return jsonify({'success': False, 'error': f'发送失败: {str(e)}'})
            
        except Exception as e:
            logging.error(f'发送消息失败: {str(e)}')
            return jsonify({'success': False, 'error': str(e)})

@app.route('/')
def home():
    return render_template_string(generate_html_template())

@app.route('/get_devices')
def get_devices():
    with lock:
        return jsonify(devices)

if __name__ == '__main__':
    tcp_thread = threading.Thread(target=handle_tcp_connection, daemon=True)
    tcp_thread.start()
    app.run(host='0.0.0.0', port=config['flask_port'], debug=False)