import os
import random

from flask import Flask, redirect, render_template
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from main.all.data import db_session
from main.all.data.changes import Changes
from main.all.data.users import User
from main.constants.web import UNREAL_ID, SUBJECT_DICT, SUBJECT_DICT_REVERSE
from main.web.forms.ad_ban import BanForm
from main.web.forms.ad_send_message import SendMessageForm
from main.web.forms.ad_send_update import SendUpdateForm
from main.web.forms.ad_unban import UnbanForm
from main.web.forms.ad_update import UpdateForm
from main.web.forms.edit import EditForm
from main.web.forms.login_form import LoginForm
from main.web.forms.register_form import RegisterForm
from main.web import web_api

web_app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(web_app)
web_app.config['SECRET_KEY'] = 'regfbo83w64be8r9g4nxrkpse4sdfrnv9uehvu9456836gvKB7342BK794voPIYV82743r9g8406'


@web_app.route('/')
@web_app.route('/index')
def root():
    return redirect('/home')


@web_app.route('/home')
def home():
    return render_template('home.html', title="Домашняя страница")


@web_app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/home")
        return render_template('login.html',
                               title="Вход",
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Вход', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def send_message_to_bot(text, chat_id):
    with open('../all/db/transit', 'w', encoding='utf-8') as f:
        f.write(chat_id + '<#>\n')
        f.write(text + '\n<!>\n')


@web_app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password1.data != form.password2.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            position=form.position.data
        )
        user.set_password(form.password1.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@web_app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/home")


@web_app.route('/ban', methods=['GET', 'POST'])
def ban():
    form = BanForm()
    if form.validate_on_submit():
        block_id = form.block_id.data
        with open('../all/db/blacklist.csv', 'r', encoding='utf-8') as f:
            re = f.read().split('\n')
        if block_id in re:
            return render_template("ad_success.html", title="Блокировка",
                                   text=f"Не удалось заблокировать пользователя {form.block_id.data}",
                                   title_text="Безуспешно")
        with open('../all/db/blacklist.csv', 'a', encoding='utf-8') as f:
            f.write(f'\n{block_id}')
        return render_template("ad_success.html", title="Блокировка",
                               text=f"Успешно заблокирован пользователь {form.block_id.data}", title_text="Успешно")
    return render_template('ban.html', title='Блокировка', form=form)


@web_app.route('/unban', methods=['GET', 'POST'])
def unban():
    form = UnbanForm()
    if form.validate_on_submit():
        block_id = form.block_id.data
        with open('../all/db/blacklist.csv', 'r', encoding='utf-8') as f:
            re = f.read().split('\n')[1:]
        k = -1
        is_found = False
        for line in re:
            k += 1
            if line == block_id:
                is_found = True
                break
        if is_found:
            re = [UNREAL_ID] + re[:k] + re[k + 1:]
            with open('../all/db/blacklist.csv', 'w', encoding='utf-8') as f:
                f.write('\n'.join(re))
            return render_template("ad_success.html", title="Разлокировка",
                                   text=f"Успешно разблокирован пользователь {form.block_id.data}",
                                   title_text="Успешно")
        else:
            return render_template("ad_success.html", title="Разлокировка",
                                   text=f"Не удалось разблокировать пользователя {form.block_id.data}",
                                   title_text="Безуспешно")
    return render_template('unban.html', title='Разблокировка', form=form)


@web_app.route('/edit', methods=['GET', 'POST'])
def edit():
    form = EditForm()
    if form.validate_on_submit():
        with open('../all/db/dz.csv', 'r', encoding='utf-8') as f:
            re = f.read().split('\n')
        line = re[SUBJECT_DICT[form.subject.data]]
        title = line.split(';')[0]
        old_text = line.split(';')[1]
        newline = title + ';' + form.text.data
        re[SUBJECT_DICT[form.subject.data]] = newline
        with open('../all/db/dz.csv', 'w', encoding='utf-8') as f:
            f.write('\n'.join(re))

        db_sess = db_session.create_session()
        changes = Changes()
        changes.from_text = old_text
        changes.to_text = form.text.data
        changes.subject = form.subject.data
        current_user.changes.append(changes)
        db_sess.merge(current_user)
        db_sess.commit()
        return render_template("ad_success.html", title="Изменение", title_text='Успешно',
                               text=f"Успешно изменён текст в {form.subject.data} на {form.text.data}")
    return render_template('edit.html', title='Изменение', form=form)


@web_app.route('/idea')
def idea():
    with open('../all/db/idea.csv', 'r', encoding='utf-8') as f:
        re = f.read()
    li = []
    re = re.split('\n')
    for line in re:
        i, t = line.split(';')[0], line.split(';')[1]
        li.append((i, t))
    return render_template('idea.html', title='Идеи', idea=li)


@web_app.route('/show')
def show():
    with open('../all/db/dz.csv', 'r', encoding='utf-8') as f:
        re = f.read()
    li = []
    re = re.split('\n')
    c = -1
    for line in re:
        c += 1
        d, t = line.split(';')[0], line.split(';')[1]
        li.append((SUBJECT_DICT_REVERSE[c], t))
    return render_template('show.html', title='Предметы', li=li)


@web_app.route('/update', methods=['GET', 'POST'])
def update():
    form = UpdateForm()
    if form.validate_on_submit():
        utext = form.utext.data.replace('\r', '')
        with open('../all/db/update', 'w', encoding='utf-8') as f:
            f.write(utext)
        return render_template("ad_success.html", title="Текст обновления",
                               text="Успешно сохранено сообщение об обновление", title_text="Успешно")
    return render_template('update.html', title='Текст обновления', form=form)


@web_app.route('/send_update', methods=['GET', 'POST'])
def send_update():
    form = SendUpdateForm()
    if form.validate_on_submit():
        with open('../all/db/update', 'r', encoding='utf-8') as f:
            re = f.read()
        send_message_to_bot(re, form.chat_id.data)
        return render_template("ad_success.html", title="Отправка обновления",
                               text="Сообщение об обновление отправиться в течение 30 секунд", title_text="Успешно")
    with open('../all/db/update', 'r', encoding='utf-8') as f:
        utext = f.read().split('\n')
    return render_template('send_update.html', title='Отправка обновления', form=form, utext=utext)


@web_app.route('/send_message', methods=['GET', 'POST'])
def send_message():
    form = SendMessageForm()
    if form.validate_on_submit():
        text = form.text.data.replace('\r', '')
        send_message_to_bot(text, form.chat_id.data)
        return render_template("ad_success.html", title="Отправка сообщения",
                               text="Сообщение отправится в течение 30 секунд", title_text="Успешно")
    return render_template('send_message.html', title='Отправка сообщения', form=form)


@web_app.route('/chatid/three')
def cithree():
    with open('../all/db/return_chatid.csv', 'r', encoding='utf-8') as f:
        re = f.read().split('\n')
    k = -1
    is_found = False
    for line in re:
        k += 1
        bid, bcd = line.split(';')[0], line.split(';')[1]
        if bid == str(current_user.id):
            uid, cd = bid, bcd
            is_found = True
            break
    if is_found:
        try:
            rl = re[:k]
        except IndexError:
            rl = []
        try:
            rr = re[k + 1:]
        except IndexError:
            rr = []
        re = rl + rr
        with open('../all/db/return_chatid.csv', 'w', encoding='utf-8') as f:
            if re:
                f.write('\n'.join(re))
        return render_template('chatid3.html', title='Предметы', result=cd, found=True)
    else:
        return render_template('chatid3.html', title='Предметы', found=False)


@web_app.route('/chatid/one')
def cione():
    return render_template('chatid.html', title='Получение ID чата')


@web_app.route('/chatid/two')
def citwo():
    com_id = random.randint(1000000, 9999999)
    with open('../all/db/queue_chatid.csv', 'a', encoding='utf-8') as f:
        f.write(f'\n{current_user.id};{com_id}')
    return render_template('chatid2.html', title='Получение ID чата', com_id=com_id)


@web_app.route('/banlist')
def banlist():
    with open('../all/db/blacklist.csv', 'r', encoding='utf-8') as f:
        li = f.read().split('\n')
    return render_template('banlist.html', title='Список заблокированных', li=li[1:])


@web_app.route('/personal')
def personal():
    return render_template('personal.html', title='Личный кабинет')


@web_app.errorhandler(404)
def p404(e):
    return render_template("404.html", title='Ничего не найдено'), 404


@web_app.errorhandler(403)
def p403(e):
    return render_template("403.html", title='Отказано в доступе'), 403


@web_app.errorhandler(401)
def p401(e):
    return render_template("401.html", title='Необходимо авторизоваться'), 401


@web_app.errorhandler(410)
def p410(e):
    return render_template("410.html", title='Ресурс удалён'), 410


@web_app.errorhandler(500)
def p500(e):
    return render_template("500.html", title='Ошибка на стороне сервера'), 500


if __name__ == '__main__':
    db_session.global_init("../all/db/webot.db")
    web_app.register_blueprint(web_api.blueprint)
    port = int(os.environ.get("PORT", 5055))
    web_app.run(host='127.0.0.1', port=port)
