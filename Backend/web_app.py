"""
Web UI 应用 - LF精炼炉加热模型监控和管理界面
Flask-based Web UI for LF Refining Furnace Heating Model
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from flasgger import Swagger, swag_from
from flask_socketio import SocketIO, emit
import logging
import os
import sys
import json
from datetime import datetime, timedelta
from threading import Thread

# 添加Backend目录到sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.session import init_database
from db.models import InputBuffer, OutputBuffer, HeatHistory, HeatConfig
from daemon import PollingDaemon
from config_manager import get_config
from sqlalchemy import desc

logger = logging.getLogger(__name__)

app = Flask(__name__,
            template_folder='web_ui/templates',
            static_folder='web_ui/static')
CORS(app, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Swagger configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}
swagger_template = {
    "info": {
        "title": "LF精炼炉加热模型API",
        "description": "LF Refining Furnace Heating Model API Documentation",
        "version": "1.0.0"
    }
}
swagger = Swagger(app, config=swagger_config, template=swagger_template)

# 全局变量
daemon_instance = None
db_factory = None


def init_app(config_manager):
    """初始化Flask应用"""
    app.config['SECRET_KEY'] = config_manager.get('web_ui.secret_key', 'dev-secret-key')
    app.config['JSON_AS_ASCII'] = False

    global db_factory
    db_config = config_manager.get('database')
    db_factory = init_database(**db_config)

    logger.info("Flask app initialized")


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/status')
def api_status():
    """系统状态API"""
    try:
        session = db_factory.get_session()

        # 统计信息
        total_tasks = session.query(InputBuffer).count()
        pending_tasks = session.query(InputBuffer).filter_by(Start_Flag=1).count()
        completed_tasks = session.query(OutputBuffer).filter_by(Finish_Flag=1).count()
        error_tasks = session.query(OutputBuffer).filter(OutputBuffer.Error_Code > 0).count()

        # 守护进程状态
        daemon_status = {
            'running': daemon_instance.running if daemon_instance else False,
            'stats': daemon_instance.stats if daemon_instance else {}
        }

        session.close()

        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'statistics': {
                'total_tasks': total_tasks,
                'pending_tasks': pending_tasks,
                'completed_tasks': completed_tasks,
                'error_tasks': error_tasks
            },
            'daemon': daemon_status
        })

    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/tasks')
def api_tasks():
    """获取任务列表"""
    try:
        session = db_factory.get_session()
        limit = int(request.args.get('limit', 50))
        status_filter = request.args.get('status', 'all')

        # 查询任务
        query = session.query(InputBuffer).order_by(desc(InputBuffer.Updated_At))

        if status_filter == 'pending':
            query = query.filter_by(Start_Flag=1)
        elif status_filter == 'completed':
            query = query.join(OutputBuffer).filter(OutputBuffer.Finish_Flag == 1)

        tasks = query.limit(limit).all()

        result = []
        for task in tasks:
            output = session.query(OutputBuffer).filter_by(Task_ID=task.Task_ID).first()

            task_data = {
                'task_id': task.Task_ID,
                'steel_grade': task.Steel_Grade,
                'heat_stage': task.Heat_Stage,
                'current_temp': float(task.Current_Temp) if task.Current_Temp else None,
                'target_temp': float(task.Target_Temp),
                'data_ready': task.Data_Ready,
                'start_flag': task.Start_Flag,
                'created_at': task.Created_At.isoformat() if task.Created_At else None,
                'output': None
            }

            if output:
                task_data['output'] = {
                    'heat_level': output.Heat_Level,
                    'heat_duration': float(output.Heat_Duration) if output.Heat_Duration else None,
                    'algorithm_used': output.Algorithm_Used,
                    'finish_flag': output.Finish_Flag,
                    'error_code': output.Error_Code,
                    'error_message': output.Error_Message,
                    'process_time': float(output.Process_Time) if output.Process_Time else None
                }

            result.append(task_data)

        session.close()
        return jsonify({'status': 'ok', 'tasks': result, 'count': len(result)})

    except Exception as e:
        logger.error(f"Failed to get tasks: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/history')
def api_history():
    """获取历史数据"""
    try:
        session = db_factory.get_session()
        limit = int(request.args.get('limit', 100))
        steel_grade = request.args.get('steel_grade')
        heat_stage = request.args.get('heat_stage')

        query = session.query(HeatHistory).order_by(desc(HeatHistory.Timestamp))

        if steel_grade:
            query = query.filter_by(Steel_Grade=steel_grade)
        if heat_stage:
            query = query.filter_by(Heat_Stage=heat_stage)

        records = query.limit(limit).all()

        result = []
        for record in records:
            result.append({
                'id': record.ID,
                'task_id': record.Task_ID,
                'steel_grade': record.Steel_Grade,
                'heat_stage': record.Heat_Stage,
                'start_temp': float(record.Start_Temp) if record.Start_Temp else None,
                'end_temp': float(record.End_Temp) if record.End_Temp else None,
                'heat_level': record.Heat_Level,
                'heat_duration': float(record.Heat_Duration) if record.Heat_Duration else None,
                'success': record.Success,
                'timestamp': record.Timestamp.isoformat() if record.Timestamp else None
            })

        session.close()
        return jsonify({'status': 'ok', 'history': result, 'count': len(result)})

    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """配置管理API"""
    try:
        session = db_factory.get_session()

        if request.method == 'GET':
            # 获取所有配置
            configs = session.query(HeatConfig).all()
            result = []
            for config in configs:
                result.append({
                    'id': config.ID,
                    'key': config.Config_Key,
                    'value': config.Config_Value,
                    'description': config.Description,
                    'type': config.Config_Type
                })

            session.close()
            return jsonify({'status': 'ok', 'configs': result})

        elif request.method == 'POST':
            # 更新配置
            data = request.json
            config_key = data.get('key')
            config_value = data.get('value')

            config = session.query(HeatConfig).filter_by(Config_Key=config_key).first()
            if config:
                config.Config_Value = config_value
                config.Updated_At = datetime.now()
                session.commit()
                session.close()
                return jsonify({'status': 'ok', 'message': 'Configuration updated'})
            else:
                session.close()
                return jsonify({'status': 'error', 'message': 'Configuration not found'}), 404

    except Exception as e:
        logger.error(f"Failed to manage config: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/algorithms')
def api_algorithms():
    """获取算法列表"""
    config = get_config()
    algorithms = config.get('algorithms', {})

    return jsonify({
        'status': 'ok',
        'algorithms': {
            'default': algorithms.get('default', 'Algorithm1'),
            'enabled': algorithms.get('enabled', ['Algorithm1', 'Algorithm2']),
            'algorithm1': algorithms.get('algorithm1', {}),
            'algorithm2': algorithms.get('algorithm2', {})
        }
    })


@app.route('/api/logs')
def api_logs():
    """获取日志"""
    try:
        log_file = get_config().get('logging.file_path', 'logs/heat_model.log')
        lines = int(request.args.get('lines', 100))

        if not os.path.exists(log_file):
            return jsonify({'status': 'ok', 'logs': []})

        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:]

        return jsonify({'status': 'ok', 'logs': recent_lines, 'count': len(recent_lines)})

    except Exception as e:
        logger.error(f"Failed to get logs: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/statistics')
def api_statistics():
    """获取统计数据"""
    try:
        session = db_factory.get_session()
        days = int(request.args.get('days', 7))

        # 最近N天的统计
        since = datetime.now() - timedelta(days=days)

        # 按钢种统计
        steel_grades = session.query(
            HeatHistory.Steel_Grade,
            HeatHistory.Success
        ).filter(HeatHistory.Timestamp >= since).all()

        steel_grade_stats = {}
        for grade, success in steel_grades:
            if grade not in steel_grade_stats:
                steel_grade_stats[grade] = {'total': 0, 'success': 0}
            steel_grade_stats[grade]['total'] += 1
            if success:
                steel_grade_stats[grade]['success'] += 1

        # 按加热阶段统计
        heat_stages = session.query(
            HeatHistory.Heat_Stage,
            HeatHistory.Success
        ).filter(HeatHistory.Timestamp >= since).all()

        heat_stage_stats = {}
        for stage, success in heat_stages:
            if stage not in heat_stage_stats:
                heat_stage_stats[stage] = {'total': 0, 'success': 0}
            heat_stage_stats[stage]['total'] += 1
            if success:
                heat_stage_stats[stage]['success'] += 1

        session.close()

        return jsonify({
            'status': 'ok',
            'period_days': days,
            'steel_grades': steel_grade_stats,
            'heat_stages': heat_stage_stats
        })

    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# WebSocket事件处理
@socketio.on('connect')
def handle_connect():
    """WebSocket连接"""
    logger.info(f"Client connected")
    emit('connected', {'message': 'Connected to server'})


@socketio.on('disconnect')
def handle_disconnect():
    """WebSocket断开"""
    logger.info(f"Client disconnected")


@socketio.on('subscribe_updates')
def handle_subscribe():
    """订阅实时更新"""
    logger.info("Client subscribed to updates")
    emit('subscribed', {'message': 'Subscribed to real-time updates'})


def start_daemon_thread(db_factory, config):
    """在后台线程启动守护进程"""
    global daemon_instance

    polling_interval = config.get('daemon.polling_interval', 2)
    daemon_instance = PollingDaemon(
        db_factory=db_factory,
        polling_interval=polling_interval
    )

    daemon_thread = Thread(target=daemon_instance.start, daemon=True)
    daemon_thread.start()
    logger.info("Daemon started in background thread")


def run_web_ui(config_manager, start_daemon=True):
    """启动Web UI"""
    init_app(config_manager)

    # 启动守护进程
    if start_daemon:
        start_daemon_thread(db_factory, config_manager)

    # 启动Flask应用
    host = config_manager.get('web_ui.host', '0.0.0.0')
    port = config_manager.get('web_ui.port', 5000)
    debug = config_manager.get('web_ui.debug', False)

    logger.info(f"Starting Web UI on http://{host}:{port}")
    logger.info(f"API Documentation available at http://{host}:{port}/api/docs")
    socketio.run(app, host=host, port=port, debug=debug, use_reloader=False, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    from config_manager import init_config
    import logging.config

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 加载配置
    config = init_config()

    # 启动Web UI
    run_web_ui(config, start_daemon=True)
