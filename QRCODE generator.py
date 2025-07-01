import qrcode
url = input("Enter your URL:")
path = input("Enter your file name:")
features = qrcode.QRCode(version=1,box_size=10,border=3)
features.add_data(url)
features.make(fit=True)
image= features.make_image(fill_color="black",back_color="white")
image.save(path)
