import os
import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id
from dotenv import load_dotenv
from database import Database
from keybuttons import create_keyboard
from handler import VkTools

 
load_dotenv()

log_dir = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

 
class BotInterface():
    
    def __init__(self):
        self.group = vk_api.VkApi(token=os.getenv('comunity_token'))
        self.handler = VkTools(token=os.getenv('acces_token'))
        self.longpoll = VkLongPoll(self.group)
        self.keyboard = create_keyboard()
        self.database = Database(dbname=os.getenv('db_name'), 
                                 user=os.getenv('user'), 
                                 password=os.getenv('password'), 
                                 host=os.getenv('host'), 
                                 port=os.getenv('password')) 
        self.offset = 0     
        self.users = []
        self.params = {}


    def write_message(self, user_id, message, keyboard=None, attachment=None):
        try:
            keyboard_data = keyboard.get_keyboard()
        except AttributeError:
            keyboard_data = None
        self.group.method('messages.send',
                               {'user_id': user_id, 
                                'message': message, 
                                'random_id': get_random_id(),
                                'keyboard': keyboard_data, 
                                'attachment': attachment})
    
    def check_exit(self):
        
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                answer = event.text.lower()
                return answer
             
     
    def check_users(self, sender, users):
         
        user = users.pop()
        vk_id = user['id']
        vk_url = f'https://vk.com/{user["id"]}'
                         
        if self.database.check_usersvk(vk_id):return
        photos = self.handler.get_top_photos(user)
            
        message = (f'Встречайте, это - {user["name"]}!\nВот ссылка на страницу: {vk_url}\n'
                   f'Вот лучшие фото со страницы:')
        self.write_message(sender, message, self.keyboard)
                
        attachment = []
        for photo in photos:
            attachment.append(f"photo{photo['owner_id']}_{photo['id']}")
        self.write_message(sender, '', self.keyboard, attachment=','.join(attachment))
        self.database.save_usersvk(vk_id, vk_url)
        self.write_message(sender, f'пользователь {vk_url} сохранен')


    def start(self):
        
        self.database.create_table()
        for event in self.longpoll.listen():
            
            
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                command = event.text.lower()
                sender = event.user_id
                 
                if command == 'привет':
                    
                    self.params = self.handler.get_profile_info(sender)
                        
                    if self.params["sex"] is None:
                        self.write_message(sender, f'привет, {self.params["name"]}\n'
                                           f'для продолжения уточните Ваш пол.\n'
                                           f'введите: "муж" или "жен"')
                        command = self.check_exit()
                        if command == 'муж': 
                            self.params["sex"] = 2
                        else:
                            self.params["sex"] = 1
                    
                    if self.params["bdate"] is None:
                        self.write_message(sender, f'привет, {self.params["name"]}\n'
                                           f'для продолжения укажите дату Вашего рождения в формате DD.MM.YYYY')
                        command = self.check_exit()
                        self.params["bdate"] = command
                    else:
                        self.write_message(sender, f'привет, {self.params["name"]}')
                                            
                    self.write_message(sender,f'я - бот знакомств в ВК.\n'
                                          f'стартуем!?\n мне нужна команда "поиск", увидешь первый результат', self.keyboard)        
 
                elif command in ('поиск'):
                    if not self.params:
                        self.write_message(sender, f'сначала поздоровайся - напиши "привет"')
                        
                    elif self.users:

                        self.check_users(sender, self.users)
                         
                    
                    else:
                        self.users = self.handler.search_users(self.params, self.offset)
                         
                        self.check_users(sender, self.users)
                        
                        self.offset += 10

                elif command in ('пока'):
                    self.write_message(sender, 'жаль прощаться, результаты поиска будут очищены , до новых встреч!')
                    self.database.delete_table() 
                    break

                else:
                    self.write_message(sender, 'команда не опознана')                       
                          
        self.database.disconnect()     

if __name__ == '__main__':
     bot = BotInterface()
     bot.start()
      
       
