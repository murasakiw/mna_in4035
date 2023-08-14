import cv2
from matplotlib import pyplot as plt
from PIL import Image
from landingai.predict import Predictor
from landingai.visualize import overlay_predictions
from IPython.display import display, Markdown
import webbrowser
import random
import json
from time import sleep
import http.client

# Food Clasifier 1
#endpoint_id = "4eb6f2c4-b341-4d24-a3df-7980c1e28a21"
#api_key = "land_sk_0pEAuiKzYGNDoaN8yfFYiaFvxP169SiZdC7DuCHbeEPgNrsUWk"

# Food Clasifier 2
endpoint_id = "6256f1a4-3976-4e29-8400-f86648ecd091"
api_key = "land_sk_0pEAuiKzYGNDoaN8yfFYiaFvxP169SiZdC7DuCHbeEPgNrsUWk"

cv2.namedWindow('RTSP Video', cv2.WINDOW_NORMAL)

def read_sensor(): #Función que lee de la base de datos el estado del sensor
    # Definir la URL
    url = "/pls/apex/a01794338/consulta/sensor"

    # Establecer la conexión
    conn = http.client.HTTPSConnection("apex.oracle.com")

    # Realizar la solicitud GET
    conn.request("GET", url)

    # Obtener la respuesta
    response = conn.getresponse()

    # Leer y mostrar el contenido de la respuesta
    data = response.read()
    json_data = json.loads(data.decode("utf-8"))
    sensor_presencia = json_data['items'][0]['status']
    sensor_peso = json_data['items'][0]['peso']
    # print(sensor_presencia)
    # print(type(sensor_presencia))
    # print(sensor_presencia == 'on')
    # print(data.decode("utf-8"))

    # Cerrar la conexión
    conn.close()
    return sensor_presencia, sensor_peso

def main():
    # Replace 'YOUR_RTSP_URL' with your actual RTSP stream URL
    #rtsp_url = 'rtsp://10.200.60.9/profile7/media.smp'
    
    # Open the RTSP stream
    cap = cv2.VideoCapture(0)
    #cap = cv2.cvtColor(cap, cv2.COLOR_BGR2RGB)

    # Check if the stream is opened correctly
    if not cap.isOpened():
        print("Error: Unable to open the RTSP stream.")
        return

    while True:
        # Read a frame from the RTSP stream
        sensor_presencia, sensor_peso = read_sensor()
        ret, frame = cap.read()

        if not ret:
            print("Error: Failed to read a frame from the RTSP stream.")
            break

        # Display the frame in a window
        cv2.imshow('RTSP Video', frame)

        # Store the last captured frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        last_captured_frame = frame

        # Listen for key events
        key = cv2.waitKey(1)

        # Exit the loop if the 'q' key is pressed
        if key & 0xFF == ord('q'):
            break

        # Perform API inference if the 'c' key is pressed
        elif sensor_presencia == 'on':
        # elif key & 0xFF == ord('c'):
            if last_captured_frame is not None:
                # Save the last captured frame to a temporary image file
                temp_image_path = last_captured_frame

                # Run inference
                predictor = Predictor(endpoint_id, api_key=api_key)
                results = predictor.predict(temp_image_path)

                # Print the predictions
                display(results)
                print(type(results))
                #print(results[1])
                print(len(results))

                # Extract label_name from results
                label = results[0].label_name

                # Print the extracted label
                print(label)

                # Generación de peso random
                peso_random = random.uniform(0.9,5.9)
                # peso = round(peso_random,1)
                peso = sensor_peso
                print("Peso aleatorio: ",peso)

                # Publicación de lectura en APEX
                # url_apex = "https://apex.oracle.com/pls/apex/a01794338/enviar_datos/env_datos"
                # url_send = "{}?tipo={}&peso={}".format(url_apex,label,peso)
                # webbrowser.open(url_send)
                # print(url_send)
                url_apex = "/pls/apex/a01794338/enviar_datos/env_datos"
                url_send = "{}?tipo={}&peso={}".format(url_apex,label,peso)
                # Establecer la conexión
                conn = http.client.HTTPSConnection("apex.oracle.com")
                # Realizar la solicitud GET
                conn.request("GET", url_send)
                # Obtener la respuesta
                response = conn.getresponse()

                # Draw raw results on the original image
                frame_ov = overlay_predictions(results, image=frame)
                plt.imshow(frame_ov)
                plt.title("Predicción de Captura")
                plt.show()

    # Release the video capture and close the display window
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
