import base64

# convert Image to Base64 (Encoding)

with open("beauty.jpg", "rb") as img_file:
    my_string = base64.b64encode(img_file.read())
f = open('beauty_string.txt','wb')
f.write(my_string)
f.close()

# convert Base64 to Image (Decoding)

file = open('beauty_string.txt','rb')


byte = file.read()
print(byte)