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

        info, = self.handler.method('users.get',
                            {'user_id': user_id,
                            'fields': 'city,bdate,sex,relation,home_town' 
                            }
                            )
        user_info = {'name': info['first_name'] + ' '+ info['last_name'],
                     'id':  info['id'],
                     'bdate': info['bdate'] if 'bdate' in info else None,
                     'home_town': info['home_town'],
                     'sex': info['sex'] if 'sex' in info else None,
                     'city': info['city']['id']
                     }
        return user_info
    
    def search_users(self, params, offset):

        sex = 1 if params['sex'] == 2 else 2
        city = params['city']
        curent_year = datetime.now().year
        user_year = int(params['bdate'].split('.')[2])
        age = curent_year - user_year
        age_from = age - 3
        age_to = age + 3

        users = self.handler.method('users.search',
                                {'count': 10,
                                 'offset': offset,
                                 'age_from': age_from,
                                 'age_to': age_to,
                                 'sex': sex,
                                 'city': city,
                                 'status': 6,
                                 'is_closed': False
                                }
                            )
        try:
            users = users['items']
        except KeyError:
            return []
        
        res = []

        for user in users:
            if user['is_closed'] == False:
                res.append({'id' : user['id'],
                            'name': user['first_name'] + ' ' + user['last_name']
                           }
                           )
        
        return res
     
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


     