import os
import random
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, List, Dict, Tuple, Optional
from pathlib import Path
from datetime import datetime, timedelta
import re
import threading
import socket
import requests

import pytz
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.log import logger
from app.plugins import _PluginBase

# 集成网络图片自动识别
from .network_image_provider import get_network_image_url, count_network_images

# ====== 统计相关全局变量和锁（插入到 import 之后，class 之前）======
visit_lock = threading.Lock()
today_visit_count = 0
today_date = datetime.now().date()
# =========================================================

class ImageHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global today_visit_count, today_date
        # ====== 1. 处理 /stats 路由 ======
        if self.path.startswith('/stats'):
            self._handle_stats_request()
            return
        # ====== 2. 统计 /random 访问量 ======
        if self.path.startswith('/random'):
            with visit_lock:
                now = datetime.now().date()
                if now != today_date:
                    today_visit_count = 0
                    today_date = now
                today_visit_count += 1
        try:
            # logger.info(f"收到请求: {self.path}")
            
            if self.path == '/':
                self.send_error(404, 'Not Found')
                return
            
            # 只处理/random请求
            if not self.path.startswith('/random'):
                self.send_error(404, 'Not Found')
                return

            # ===== 新增：优先处理横/竖屏网络图片地址 =====
            # 获取type参数
            type_param = None
            if '?' in self.path:
                type_param = re.search(r'type=(\w+)', self.path)
                if type_param:
                    type_param = type_param.group(1)
            # 判断设备类型
            ua = self.headers.get('User-Agent', '')
            is_mobile = bool(re.search(r'(phone|pad|pod|iPhone|iPod|ios|iPad|Android|Mobile|BlackBerry|IEMobile|MQQBrowser|JUC|Fennec|wOSBrowser|BrowserNG|WebOS|Symbian|Windows Phone)', ua, re.I))
            # 横屏/竖屏分流
            if type_param == 'mobile' or (not type_param and is_mobile):
                network_url = getattr(self.server, 'network_image_url_mobile', None) or \
                              getattr(self.server, 'network_image_url', None)
            else:
                network_url = getattr(self.server, 'network_image_url_pc', None) or \
                              getattr(self.server, 'network_image_url', None)
            if network_url:
                img_url = get_network_image_url(network_url)
                if img_url:
                    self.send_response(302)
                    self.send_header('Location', img_url)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Cache-Control', 'no-store')
                    self.end_headers()
                    return
            # ===== 原有本地目录逻辑 =====
                
            # 获取type参数
            type_param = None
            if '?' in self.path:
                type_param = re.search(r'type=(\w+)', self.path)
                if type_param:
                    type_param = type_param.group(1)
                    
            # 判断设备类型
            ua = self.headers.get('User-Agent', '')
            is_mobile = bool(re.search(r'(phone|pad|pod|iPhone|iPod|ios|iPad|Android|Mobile|BlackBerry|IEMobile|MQQBrowser|JUC|Fennec|wOSBrowser|BrowserNG|WebOS|Symbian|Windows Phone)', ua, re.I))
            
            # logger.info(f"设备类型: {'移动端' if is_mobile else 'PC端'}")
            
            # 根据条件选择目录
            if type_param == 'mobile' or (not type_param and is_mobile):
                image_dir = self.server.mobile_path
                # logger.info(f"使用竖屏图片目录: {image_dir}")
            else:
                image_dir = self.server.pc_path
                # logger.info(f"使用横屏图片目录: {image_dir}")
                
            # 获取随机图片
            image_files = []
            for ext in ('*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp'):
                image_files.extend(Path(image_dir).glob(ext))
                
            if not image_files:
                logger.error(f"目录中没有找到图片: {image_dir}")
                self.send_error(404, 'No images found')
                return
                
            image_path = str(random.choice(image_files))
            # logger.info(f"选择的图片: {image_path}")
            
            try:
                # 获取文件类型和大小
                content_type, _ = mimetypes.guess_type(image_path)
                file_size = os.path.getsize(image_path)
                
                if not content_type or not content_type.startswith('image/'):
                    logger.error(f"不支持的文件类型: {content_type}")
                    self.send_error(415, 'Unsupported Media Type')
                    return
                    
                # 发送响应头
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(file_size))
                self.send_header('Access-Control-Allow-Origin', '*')
                # 添加缓存控制
                self.send_header('Cache-Control', 'no-store') #禁止缓存
                self.end_headers()
                
                # 分块发送图片内容
                with open(image_path, 'rb') as f:
                    while True:
                        chunk = f.read(65536)  # 增大读取缓冲区到64KB
                        if not chunk:
                            break
                        try:
                            self.wfile.write(chunk)
                        except (BrokenPipeError, ConnectionResetError) as e:
                            logger.warning(f"客户端断开连接: {str(e)}")
                            return
                            
                logger.info(f"图片发送成功: {image_path}")
                    
            except Exception as e:
                logger.error(f'发送图片失败: {str(e)}')
                self.send_error(500, 'Internal Server Error')
                
        except Exception as e:
            logger.error(f'处理请求失败: {str(e)}')
            try:
                self.send_error(500, 'Internal Server Error')
            except:
                pass

    def log_message(self, format, *args):
        """重写日志方法,避免重复输出访问日志"""
        return

    def _extract_image_urls_from_json(self, data):
        """递归查找 json 任意层级的所有图片链接"""
        urls = []
        if isinstance(data, dict):
            for v in data.values():
                urls.extend(self._extract_image_urls_from_json(v))
        elif isinstance(data, list):
            for v in data:
                urls.extend(self._extract_image_urls_from_json(v))
        elif isinstance(data, str):
            # 宽松判断：有 http/https 且可能是图片
            if data.startswith('http'): 
                # 先判断后缀
                if data.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                    urls.append(data)
                else:
                    # 尝试 HEAD 请求 Content-Type
                    try:
                        resp = requests.head(data, timeout=2, allow_redirects=True)
                        ct = resp.headers.get('Content-Type', '')
                        if ct.startswith('image/'):
                            urls.append(data)
                    except Exception:
                        pass
        return urls

    def _handle_stats_request(self):
        """处理统计数据请求，返回图片数量和今日访问量"""
        try:
            pc_path = self.server.pc_path
            mobile_path = self.server.mobile_path
            network_image_url_pc = getattr(self.server, 'network_image_url_pc', None)
            network_image_url_mobile = getattr(self.server, 'network_image_url_mobile', None)
            # 本地图片
            pc_local = sum(1 for ext in ('*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp') for _ in Path(pc_path).glob(ext)) if pc_path and os.path.exists(pc_path) else 0
            mobile_local = sum(1 for ext in ('*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp') for _ in Path(mobile_path).glob(ext)) if mobile_path and os.path.exists(mobile_path) else 0
            # 网络图片
            net_pc = count_network_images(network_image_url_pc) if network_image_url_pc else 0
            net_mobile = count_network_images(network_image_url_mobile) if network_image_url_mobile else 0
            # 处理未知
            pc_total = pc_local + (net_pc if isinstance(net_pc, int) else 0)
            mobile_total = mobile_local + (net_mobile if isinstance(net_mobile, int) else 0)
            total = pc_total + mobile_total
            with visit_lock:
                today = today_visit_count
            import json
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "total": total,
                "pc": pc_total,
                "mobile": mobile_total,
                "today": today,
                "detail": {
                    "local": {"pc": pc_local, "mobile": mobile_local},
                    "network": {
                        "pc": net_pc if net_pc is not None else "未知",
                        "mobile": net_mobile if net_mobile is not None else "未知"
                    }
                }
            }).encode('utf-8'))
        except Exception as e:
            logger.error(f"统计接口异常: {str(e)}")
            try:
                self.send_error(500, 'Internal Server Error')
            except:
                pass


class RandomPic(_PluginBase):
    # 插件名称
    plugin_name = "随机图库"
    # 插件描述
    plugin_desc = "随机图片API服务,支持b di横屏/竖屏图片分类"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/xijin285/MoviePilot-Plugins/refs/heads/main/icons/randompic.png"
    # 插件版本
    plugin_version = "2.0"
    # 插件作者
    plugin_author = "M.Jinxi"
    # 作者主页
    author_url = "https://github.com/xijin285"
    # 插件配置项ID前缀
    plugin_config_prefix = "randompic_"
    # 加载顺序
    plugin_order = 15
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _scheduler = None
    _server = None
    _server_thread = None
    _enable = False
    _port = None
    _pc_path = None
    _mobile_path = None
    _listen_ip = None
    _network_image_url_pc = None
    _network_image_url_mobile = None
    _network_image_url = None  # 兼容老配置

    def init_plugin(self, config: dict = None):
        if config:
            self._enable = config.get("enable")
            self._port = config.get("port")
            self._pc_path = config.get("pc_path")
            self._mobile_path = config.get("mobile_path")
            self._network_image_url_pc = config.get("network_image_url_pc")
            self._network_image_url_mobile = config.get("network_image_url_mobile")
            self._network_image_url = config.get("network_image_url")  # 兼容老配置

        self.stop_service()

        if self._enable:
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)
            # logger.info("随机图库服务启动中...")
            self._scheduler.add_job(
                func=self.__run_service,
                trigger="date",
                run_date=datetime.now(tz=pytz.timezone(settings.TZ))
                + timedelta(seconds=2),
                name="随机图库启动服务",
            )

            if self._scheduler.get_jobs():
                self._scheduler.print_jobs()
                self._scheduler.start()

    def get_state(self) -> bool:
        return self._enable

    def get_render_mode(self) -> Tuple[str, Optional[str]]:
        """返回Vue渲染模式和组件路径"""
        return "vue", "dist/assets"

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        return []

    def get_api(self) -> List[Dict[str, Any]]:
        """注册插件API"""
        return [
            {
                "path": "/config",
                "endpoint": self._get_config,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "获取配置"
            },
            {
                "path": "/config",
                "endpoint": self._save_config,
                "methods": ["POST"],
                "auth": "bear",
                "summary": "保存配置"
            },
            {
                "path": "/status",
                "endpoint": self._get_status,
                "methods": ["GET"],
                "auth": "bear",
                "summary": "获取状态"
            }
        ]

    def _get_config(self) -> Dict[str, Any]:
        """API处理函数：返回插件配置"""
        return {
            "enable": self._enable,
            "port": self._port,
            "pc_path": self._pc_path,
            "mobile_path": self._mobile_path,
            "network_image_url_pc": self._network_image_url_pc,
            "network_image_url_mobile": self._network_image_url_mobile,
            "network_image_url": self._network_image_url,  # 兼容老配置
        }

    def _save_config(self, data: dict) -> dict:
        """ API处理函数 """
        try:
            enable = data.get("enable")
            port = data.get("port")
            pc_path = data.get("pc_path")
            mobile_path = data.get("mobile_path")
            network_image_url_pc = data.get("network_image_url_pc")
            network_image_url_mobile = data.get("network_image_url_mobile")
            network_image_url = data.get("network_image_url")  # 兼容老配置

            # 参数校验
            if not port or not pc_path or not mobile_path:
                return {"success": False, "msg": "端口和图片目录不能为空"}

            self._enable = enable
            self._port = port
            self._pc_path = pc_path
            self._mobile_path = mobile_path
            self._network_image_url_pc = network_image_url_pc
            self._network_image_url_mobile = network_image_url_mobile
            self._network_image_url = network_image_url  # 兼容老配置

            # 持久化配置
            self.update_config({
                "enable": self._enable,
                "port": self._port,
                "pc_path": self._pc_path,
                "mobile_path": self._mobile_path,
                "network_image_url_pc": self._network_image_url_pc,
                "network_image_url_mobile": self._network_image_url_mobile,
                "network_image_url": self._network_image_url,  # 兼容老配置
            })

            # 重启服务
            self.stop_service()
            self.init_plugin(self.get_config())

            return {"success": True, "msg": "配置保存成功"}
        except Exception as e:
            logger.error(f"保存配置失败: {str(e)}")
            return {"success": False, "msg": f"保存配置失败: {str(e)}"}

    def _get_status(self) -> Dict[str, Any]:
        """API处理函数：返回插件状态"""
        # 统计图片数量
        pc_count = 0
        mobile_count = 0
        if self._pc_path and os.path.exists(self._pc_path):
            for ext in ('*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp'):
                pc_count += len(list(Path(self._pc_path).glob(ext)))
        if self._mobile_path and os.path.exists(self._mobile_path):
            for ext in ('*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp'):
                mobile_count += len(list(Path(self._mobile_path).glob(ext)))

        return {
            "enable": self._enable,
            "port": self._port,
            "pc_path": self._pc_path,
            "mobile_path": self._mobile_path,
            "network_image_url_pc": self._network_image_url_pc,
            "network_image_url_mobile": self._network_image_url_mobile,
            "network_image_url": self._network_image_url,  # 兼容老配置
            "pc_count": pc_count,
            "mobile_count": mobile_count,
            "total_count": pc_count + mobile_count,
            "today_visits": today_visit_count,
            "server_status": "running" if (self._server and self._server_thread and self._server_thread.is_alive()) else "stopped",
            "last_error": "",
            "listen_ip": self._listen_ip,
        }

    def get_form(self) -> Tuple[Optional[List[dict]], Dict[str, Any]]:
        """
        【重要】为Vue模式提供配置页面的定义。
        即使使用Vue模式，这个方法也必须实现，否则将导致插件加载失败。
        Vue模式下，第一个参数返回None，第二个参数返回初始配置数据。
        """
        return None, {
            "enable": self._enable,
            "port": self._port,
            "pc_path": self._pc_path,
            "mobile_path": self._mobile_path,
            "network_image_url_pc": self._network_image_url_pc,
            "network_image_url_mobile": self._network_image_url_mobile,
            "network_image_url": self._network_image_url,  # 兼容老配置
        }

    def get_page(self) -> List[dict]:
        """
        【重要】为Vuetify模式提供数据页面的定义。
        即使使用Vue模式，这个方法也必须实现，否则将导致插件加载失败。
        Vue模式下，返回一个空列表即可。
        """
        return []

    def get_dashboard_meta(self) -> Optional[List[Dict[str, str]]]:
        """获取插件仪表盘元信息"""
        return [
            {
                "key": "main_dashboard",
                "name": "随机图库状态"
            }
        ]

    def get_dashboard(self, key: str, **kwargs) -> Optional[
        Tuple[Dict[str, Any], Dict[str, Any], Optional[List[dict]]]]:
        """获取插件仪表盘页面"""
        if key == "main_dashboard":
            # Vue组件模式（返回None作为第三个参数）
            return {
                "cols": 12,
                "md": 6
            }, {
                "refresh": 30,
                "border": True,
                "title": "随机图库状态",
                "subtitle": "图片统计和访问数据"
            }, None
        return None

    def __run_service(self):
        """
        运行服务
        """
        if not self._port:
            logger.error("未配置端口，无法启动服务")
            return

        if not (self._pc_path or self._network_image_url_pc):
            logger.error("未配置横屏图片目录或网络图片地址，无法启动服务")
            return
        if not (self._mobile_path or self._network_image_url_mobile):
            logger.error("未配置竖屏图片目录或网络图片地址，无法启动服务")
            return

        # 转换为绝对路径
        pc_path = os.path.abspath(self._pc_path) if self._pc_path else None
        mobile_path = os.path.abspath(self._mobile_path) if self._mobile_path else None
        
        # logger.info(f"横屏图片目录: {pc_path}")
        # logger.info(f"竖屏图片目录: {mobile_path}")

        if pc_path and not os.path.exists(pc_path):
            logger.error(f"横屏图片目录不存在: {pc_path}")
            return

        if mobile_path and not os.path.exists(mobile_path):
            logger.error(f"竖屏图片目录不存在: {mobile_path}")
            return

        try:
            port = int(self._port)
            # logger.info(f"尝试启动HTTP服务器在端口: {port}")
            
            # 检查端口是否被占用
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            if result == 0:
                logger.error(f"端口 {port} 已被占用")
                return
            sock.close()
            
            # 创建HTTP服务器
            listen_ip = '0.0.0.0'
            class CustomHTTPServer(HTTPServer):
                pass
            self._server = CustomHTTPServer((listen_ip, port), ImageHandler)
            self._server.pc_path = self._pc_path
            self._server.mobile_path = self._mobile_path
            self._server.network_image_url_pc = self._network_image_url_pc
            self._server.network_image_url_mobile = self._network_image_url_mobile
            self._server.network_image_url = self._network_image_url  # 兼容老配置
            
            # 在新线程中启动服务器
            self._server_thread = threading.Thread(target=self._server.serve_forever)
            self._server_thread.daemon = True
            self._server_thread.start()
            
            # 获取本机IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(('8.8.8.8', 80))
                ip = s.getsockname()[0]
            except:
                ip = '127.0.0.1'
            finally:
                s.close()
            self._listen_ip = ip
            # 启动服务器
            logger.info(f"随机图库服务启动成功! 访问地址: http://{ip}:{port}/random")
        except Exception as e:
            logger.error(f"启动服务失败: {str(e)}")
            logger.error(f"请检查端口 {port} 是否被占用")

    def stop_service(self):
        """
        停止服务
        """
        try:
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._scheduler.shutdown()
                self._scheduler = None
            if self._server:
                self._server.shutdown()
                self._server = None
            if self._server_thread:
                self._server_thread.join()
                self._server_thread = None
        except Exception as e:
            logger.error(f"停止服务失败: {str(e)}") 