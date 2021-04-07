import flask
from flask import jsonify, make_response, request

from main.all.data import db_session
from main.all.data.users import User
from main.web.run import send_message_to_bot

blueprint = flask.Blueprint(
    'web_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/version')
def get_version():
    return jsonify({
        "version": "1.0.0"
    })


@blueprint.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@blueprint.route('/api/message')
def send_message():
    if not request:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['email', 'password', 'chat_id', 'message']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == request.json['email']).first()
    if user and user.check_password(request.json['password']):
        send_message_to_bot(request.json['message'], request.json['chat_id'])
        return jsonify({"status": "Message will be sent within 90 seconds"})
    else:
        return jsonify({'error': 'Bad email or password'})
