# Dua tren image co ban nao
FROM python:3.9.1
# Khai bao thu muc lam viec
WORKDIR /home/ngockhiem/Documents/VTM/Task3


# Copy toàn bộ file mã nguồn và các file khác vào image
COPY requirement.txt requirement.txt
# cai dat cac nen tang can thiet cho file chay  dua vao file cai
RUN pip3 install -r requirement.txt
# run cmd
COPY . .

CMD ["uvicorn","uploadfile-mongo:app","--host","0.0.0.0","--port","5000"]