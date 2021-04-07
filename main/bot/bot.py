import random

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import vk_api
import pymorphy2
from main.constants.web import TOKEN, CLUB_ID


class HW:

    def __init__(self):
        self.vk_session = vk_api.VkApi(token=TOKEN)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkBotLongPoll(self.vk_session, group_id=CLUB_ID)
        self.morph = pymorphy2.MorphAnalyzer()
        self.upload = vk_api.VkUpload(self.vk_session)

    def get_subject(self, word):
        words = word.split(' ')
        res = []
        for word in words:
            normal = self.morph.parse(word)
            if normal:
                normal = normal[0]
                res.append(normal.normal_form)
                continue
        if res:
            return res
        else:
            return False

    def get_message(self, subjects):
        lx = []
        for subject in subjects:
            with open('../all/db/dz.csv', 'r', encoding='utf-8') as f:
                lr = f.read().split('\n')
                li = []
                for line in lr:
                    ln = line.split(';')
                    li.append(ln)
            for line in li:
                k = line[0].split(',')
                if subject in k:
                    lx.append((subject, line[1]))
                    break
            else:
                lx.append((subject, None))
        if lx:
            return lx
        else:
            return False

    def send_message(self, chat_id, text):
        random_id = random.randint(0, 99999999)

        params = {
            'chat_id': chat_id,
            'message': text,
            'random_id': random_id
        }
        self.vk.messages.send(**params)

    def run(self):
        print('Бот слушает')
        for event in self.longpoll.listen():
            print('Проверяю')
            if event.type == VkBotEventType.MESSAGE_NEW:
                print('Нашел')
                if event.from_chat:
                    msg = event.obj.message['text'].lower()
                    if msg:
                        if '!' == msg[0]:
                            if self.from_bl(event):
                                self.send_message(event.chat_id, 'Вы были заблокированы :(')
                                continue
                            self.admin_command(msg[1:], event)
                    if 'что по' in msg or 'задано' in msg:
                        if self.from_bl(event):
                            self.send_message(event.chat_id, 'Вы были заблокированы :(')
                            continue
                        subject = self.clean_up(msg)
                        subject = self.get_subject(subject)
                        if subject:
                            text = self.get_message(subject)
                        else:
                            self.send_message(event.chat_id, 'Я вообще не понял, про какой предмет идёт речь😥')
                            continue
                        if text is False:
                            self.send_message(event.chat_id, 'Я не понял, про какой предмет идёт речь😥')
                            continue
                        self.result(event.chat_id, text)

    def result(self, chat_id, li):
        s = ""
        for c in li:
            title, text = c
            if text is None:
                text = "Я не понял, про какой именно предмет идёт речь 😥"
            res_text = f'По запросу "{title}"\n{text}'
            s += res_text
            s += '\n'
        s = s[:-1]
        self.send_message(chat_id, s)

    def clean_up(self, msg):
        msg = msg.split()
        nmsg = []
        sw = ['что', 'по', 'задано', '?', '.', ',', '-', 'и', ""]
        for w in msg:
            if w[-1] in sw:
                w = w[:-1]
            if w not in sw:
                nmsg.append(w)
        if nmsg:
            return ' '.join(nmsg)
        else:
            return ''

    def admin_command(self, msg, event):
        comms = {
            'идея': 'ad_idea',
            'получить': 'look',
        }
        chat_id = event.chat_id
        if not msg:
            return
        if msg.split()[0] in comms.keys():
            if len(msg.split()) > 1:
                com, args = msg.split()[0], msg.split()[1:]
            else:
                com = msg
                args = []
            eval(f'self.{comms[com]}(chat_id, event, *args)')
        else:
            self.send_message(chat_id, 'Ошибка команды')

    def ad_idea(self, chat_id, event, *args):
        if args:
            with open('../all/db/idea.csv', 'a', encoding='utf-8') as f:
                f.write(f'\n{event.obj.message["from_id"]};{" ".join(args)}')
            self.send_message(chat_id, 'Предложение оставлено ;)')
            return
        self.send_message(chat_id, "Нет текста (")

    def look(self, chat_id, event, *args):
        if args:
            with open('../all/db/queue_chatid.csv', 'r', encoding='utf-8') as f:
                re = f.read()
            re = re.split('\n')
            k = -1
            is_found = False
            for line in re:
                k += 1
                lin = line.split(';')
                bid, bo = lin[0], lin[1]
                if bo == args[0]:
                    uid, o = bid, bo
                    is_found = True
                    break
            if not is_found:
                self.send_message(chat_id, 'Ошибка. Проверьте команду')
                return
            try:
                rl = re[:k]
            except IndexError:
                rl = []
            try:
                rr = re[k + 1:]
            except IndexError:
                rr = []
            re = rl + rr
            with open('../all/db/queue_chatid.csv', 'w', encoding='utf-8') as f:
                if re:
                    f.write('\n'.join(re))
            with open('../all/db/return_chatid.csv', 'a', encoding='utf-8') as f:
                f.write('\n' + str(uid) + ';' + str(chat_id))
            return
        self.send_message(chat_id, 'Нет текста(')

    def from_bl(self, event):
        with open('../all/db/blacklist.csv', 'r', encoding='utf-8') as f:
            re = f.read().split('\n')
        if str(event.obj.message['from_id']) in re:
            return True
        return False


if __name__ == '__main__':
    # while True:
    #     try:
    hw = HW()
    hw.run()
        # except BaseException as ex:
        #     print(ex)
        #     continue
