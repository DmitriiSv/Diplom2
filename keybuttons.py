from vk_api.keyboard import VkKeyboard, VkKeyboardColor

def create_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('поиск', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('пока', color=VkKeyboardColor.NEGATIVE)
    return keyboard