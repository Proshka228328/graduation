import cv2

# Используйте ваш IP-адрес, порт и учетные данные, указанные в IP Webcam
ip_address = '10.147.20.19'
port = '8080'
username = 'horse'
password = 's10102008s'

video_url = f'http://{username}:{password}@{ip_address}:{port}/video'

cap = cv2.VideoCapture(video_url)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Error reading frame.")
        break

    cv2.imshow('Video Stream', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
