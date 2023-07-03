from datetime import datetime 
import vk_api
import os
from dotenv import load_dotenv
 
load_dotenv()



class VkTools():
    def __init__(self, token):
       self.token = os.getenv('acces_token')
       self.handler = vk_api.VkApi(token=self.token)

    def get_profile_info(self, user_id):
        info = self.handler.method('users.get', {'user_ids': user_id, 'fields': 'first_name,last_name,sex,city,bdate'})
        user_info = {
                        'id': info[0]['id'],
                        'first_name': info[0]['first_name'],
                        'last_name': info[0]['last_name'],
                        'sex': info[0]['sex'],
                        'city': info[0]['city'],
                        'bdate': info[0]['bdate'],
                    }
        
        return user_info
      
    def search_users(self, user_id, offset):
        search_params = {'user_ids': user_id, 'fields': 'bdate, sex, city'}
        user_info = self.handler.method('users.get', search_params)
        user_info = user_info[0]
        user_age = self.calculate_age(user_info['bdate'])
        user_sex = user_info['sex']
        user_city = user_info['city']['id']

        users = self.handler.method(
                'users.search',
                {'count': 10,
                'city': user_city,
                'sex': 1 if user_sex == 2 else 2,
                'status': 0,
                'status_list': [1, 6],
                'age_from': user_age - 3,
                'age_to': user_age + 3,
                'has_photo': 1,
                'fields': 'photo_max_orig, screen_name',
                'offset': offset})

        return users
         
    def calculate_age(self, bdate):
        if bdate:
            curent_year = datetime.now().year
            user_year = int(bdate.split('.')[2])
            age = curent_year - user_year
            return age
     
    def get_top_photos(self, user):
        photos_user = self.handler.method('photos.get', {'owner_id': user['id'], 'album_id': 'profile', 'rev': 1,
                                                               'count': 3, 'extended': 1, 'photo_sizes': 1})
        photos_data = []
        for photo in photos_user['items']:
            sizes = photo['sizes']
            likes = photo['likes']['count']
            comments = photo['comments']['count']
            photo_data = {'sizes': sizes, 'likes': likes, 'comments': comments, 'owner_id': photo['owner_id'],
                          'id': photo['id']}
            photos_data.append(photo_data)
        photos_data = sorted(photos_data, key=lambda x: (x['likes'], x['comments']), reverse=True)[:3]
        return photos_data


     