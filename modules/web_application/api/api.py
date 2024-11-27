from flask import Blueprint, session
from modules.web_application.models.models import db, User, ScrapedData
from flask import request, jsonify
from modules.web_application.models.models import PromptLog, db
from datetime import datetime


api = Blueprint('api', __name__)

@api.route('/scraped_data', methods=['POST'])
def api_create_scraped_data():
    """Создать новую запись scraped_data."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401


    data = request.json
    if not data or 'url' not in data or 'content' not in data:
        return jsonify({'error': 'Invalid payload'}), 400

    user_id = session['user_id']

    new_data = ScrapedData(
        url=data['url'],
        content=data['content'],
        scraped_metadata=data.get('scraped_metadata', {}),
        created_by_user_id=user_id,
        created_at=datetime.utcnow()
    )
    db.session.add(new_data)
    db.session.commit()

    return jsonify({'message': 'Scraped data created', 'data': new_data.to_dict()}), 201


@api.route('/prompts', methods=['POST'])
def api_create_prompt():
    """Создать новую запись prompt."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    if not data or 'prompt_text' not in data or 'generated_output' not in data:
        return jsonify({'error': 'Invalid payload'}), 400

    user_id = session['user_id']

    new_prompt = PromptLog(
        prompt_text=data['prompt_text'],
        generated_output=data['generated_output'],
        tokens_used=data.get('tokens_used', 0),
        created_by_user_id=user_id,
        created_at=datetime.utcnow()
    )
    db.session.add(new_prompt)
    db.session.commit()

    return jsonify({'message': 'Prompt created', 'data': new_prompt.to_dict()}), 201


@api.route('/scraped_data', methods=['GET'])
def api_get_scraped_data():
    """Получить все записи scraped_data в формате JSON."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    data = ScrapedData.query.filter_by(created_by_user_id=user_id).all()
    return jsonify([d.to_dict() for d in data]), 200


@api.route('/scraped_data/<int:data_id>', methods=['GET'])
def api_get_scraped_data_by_id(data_id):
    """Получить конкретную запись scraped_data по ID."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = ScrapedData.query.get(data_id)
    if not data or data.created_by_user_id != session['user_id']:
        return jsonify({'error': 'Data not found or unauthorized'}), 404

    return jsonify(data.to_dict()), 200


@api.route('/prompts', methods=['GET'])
def api_get_prompts():
    """Получить все записи prompts в формате JSON."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    prompts = PromptLog.query.filter_by(created_by_user_id=user_id).all()
    return jsonify([p.to_dict() for p in prompts]), 200


@api.route('/prompts/<int:prompt_id>', methods=['GET'])
def api_get_prompt_by_id(prompt_id):
    """Получить конкретную запись prompt по ID."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    prompt = PromptLog.query.get(prompt_id)
    if not prompt or prompt.created_by_user_id != session['user_id']:
        return jsonify({'error': 'Prompt not found or unauthorized'}), 404

    return jsonify(prompt.to_dict()), 200