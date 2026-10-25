from PIL import Image
img = Image.open('app_icon.png')
img.save('app_icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
print("Файл app_icon.ico успешно создан!")