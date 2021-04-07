import random
from time import sleep

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import vk_api
import pymorphy2
from main.constants.web import TOKEN, CLUB_ID


class HW:

    def __init__(self):
        self.vk_session = vk_api.VkApi(token=TOKEN)
        self.vk = self.vk_session.get_api()

    def send_message(self, chat_id, text):
        random_id = random.randint(0, 99999999)

        params = {
            'chat_id': chat_id,
            'message': text,
            'random_id': random_id
        }
        self.vk.messages.send(**params)

    def run(self):
        while True:
            sleep(0.5 * 60)
            with open('../all/db/transit', 'r', encoding='utf-8') as f:
                re = f.read()
            if not re:
                continue
            re = re.split('\n<!>\n')
            for line in re:
                if line == '':
                    continue
                chat_id, text = line.split('<#>\n')[0], line.split('<#>\n')[1]
                self.send_message(chat_id, text)
            with open('../all/db/transit', 'w', encoding='utf-8') as f:
                pass


if __name__ == '__main__':
    # while True:
    #     try:
    hw = HW()
    hw.run()
        # except BaseException as ex:
        #     print(ex)
        #     continue
