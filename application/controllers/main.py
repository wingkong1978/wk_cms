from flask import Blueprint, render_template, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """首页路由"""
    return render_template('index.html', title='Flask-CMS')

@main_bp.route('/api/health')
def health_check():
    """健康检查API"""
    return jsonify({
        'status': 'ok',
        'message': 'Flask-CMS is running'
    }) 