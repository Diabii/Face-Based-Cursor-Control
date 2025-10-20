import cv2
import pyautogui
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
import mediapipe as mp

# USTAWIENIA CTK
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Zaokrąglenie kamerki bo ładne ;)
def round_corners(img, radius):
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, img.size[0], img.size[1]), radius=radius, fill=255)
    img.putalpha(mask)
    return img

window = ctk.CTk()
window.geometry("350x375")
window.title("Kamerka")
window.attributes('-topmost', True)
window.configure(fg_color='#b8c2d1')

font = ('Segoe UI', 18)
buttonheight = 35

# FLAGI STERUJĄCE
running = False
stop_program = False
holding_mouse = False

# USTAWIENIA KAMERKI
cap = cv2.VideoCapture(0)
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

# USTAWIENIA FACEMESH
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# FUNKCJE
teeth_ratio_threshold = 5

# Funkcja do aktualizacji labela przy suwaku
def update_ratio_label(value):
    global teeth_ratio_threshold
    teeth_ratio_threshold = float(value)
    ratio_value_label.configure(text=f"{teeth_ratio_threshold:.1f}")

# Przyciski startu/pauzy
def toggle_start():
    global running
    running = not running
    if running:
        btn1.configure(text="Pause", fg_color="#6bbc79", hover_color="#2c983e")
    else:
        btn1.configure(text="Start", fg_color="#f6f6f6", hover_color="#6bbc79")

def close_program():
    global stop_program, holding_mouse
    stop_program = True
    if holding_mouse:
        pyautogui.mouseUp()  # upewnienie że mysz nie zostanie przytrzymana
    window.destroy()

def update_frame():
    global holding_mouse

    ret, frame = cap.read()
    if not ret:
        window.after(10, update_frame)
        return

    frame = cv2.flip(frame, 1)

    # Przycięcie kamerki
    height, width = frame.shape[:2]
    crop_x = 120
    crop_y = 90
    frame = frame[crop_y:height-crop_y, crop_x:width-crop_x]
    height, width = frame.shape[:2]

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(18, 18))

    # Siatka na ekranie
    cv2.line(frame, (width // 3, 0), (width // 3, height), (0, 0, 0), 1)
    cv2.line(frame, (2 * width // 3, 0), (2 * width // 3, height), (0, 0, 0), 1)
    cv2.line(frame, (0, height // 3), (width, height // 3), (0, 0, 0), 1)
    cv2.line(frame, (0, 2 * height // 3), (width, 2 * height // 3), (0, 0, 0), 1)

    x = y = w = h = 0
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

    center_x = x + w // 2
    center_y = y + h // 2
    cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

    col1, col2 = width // 3, 2 * width // 3
    row1, row2 = height // 3, 2 * height // 3
    pole = "brak"

    if w > 0 and h > 0:
        # Pozycja w siatce
        col = 'lewa' if center_x < col1 else 'srodek' if center_x < col2 else 'prawa'
        row = 'gora' if center_y < row1 else 'srodek' if center_y < row2 else 'dol'

        # Mapowanie kombinacji row i col na pole
        pole_map = {
            ('srodek', 'srodek'): 'srodek',
            ('gora', 'lewa'): 'lewy gorny rog',
            ('gora', 'prawa'): 'prawy gorny rog',
            ('dol', 'lewa'): 'lewy dolny rog',
            ('dol', 'prawa'): 'prawy dolny rog'
        }

        # Najpierw sprawdzamy kombinacje row+col
        pole = pole_map.get((row, col))

        # Jeśli nie ma w mapie, to sprawdzamy same row lub col
        if not pole:
            pole = 'gora' if row == 'gora' else 'dol' if row == 'dol' else 'lewo' if col == 'lewa' else 'prawo'


        # Ruch myszki
        if running:
            moves = {
                'lewy gorny rog': (-3.5, -3.5),   # Po pitagorasie ok. 3,5 wyszło xD
                'prawy gorny rog': (3.5, -3.5),
                'lewy dolny rog': (-3.5, 3.5),
                'prawy dolny rog': (3.5, 3.5),
                'gora': (0, -5),
                'dol': (0, 5),
                'lewo': (-5, 0),
                'prawo': (5, 0)
            }
            dx, dy = moves.get(pole, (0, 0))
            pyautogui.moveRel(dx, dy)


        # Podpis nad buzią
        Text_Osoba = 'Osoba - ' + pole
        cv2.putText(frame, Text_Osoba, (x, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # DETEKCJA ZĘBÓW
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)
        teeth_visible = False

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                top_lip = face_landmarks.landmark[13]
                bottom_lip = face_landmarks.landmark[14]
                left_mouth = face_landmarks.landmark[61]
                right_mouth = face_landmarks.landmark[291]

                h_face, w_face, _ = frame.shape
                mouth_width = abs(right_mouth.x - left_mouth.x) * w_face
                mouth_height = abs(top_lip.y - bottom_lip.y) * h_face
                ratio = mouth_width / mouth_height if mouth_height != 0 else 0

                if ratio < teeth_ratio_threshold:
                    teeth_visible = True
                    cv2.putText(frame, "Klikniecie", (width // 2 - 70, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    break

        # Trzymanie lewego przycisku myszy
        if running:
            if teeth_visible and not holding_mouse:
                pyautogui.mouseDown()
                holding_mouse = True
            elif not teeth_visible and holding_mouse:
                pyautogui.mouseUp()
                holding_mouse = False

    # Wyświetlenie w CTK
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    img = img.resize((400, 300))
    img = round_corners(img, radius=30)
    imgtk = ImageTk.PhotoImage(image=img)
    image_label.configure(image=imgtk)
    image_label.image = imgtk

    if not stop_program:
        window.after(10, update_frame)


# GUI
image_label = ctk.CTkLabel(window, text="")
image_label.pack(padx=10, pady=10)

buttonframe = ctk.CTkFrame(window, fg_color="transparent")
buttonframe.columnconfigure(0, weight=1)
buttonframe.columnconfigure(1, weight=1)

btn1 = ctk.CTkButton(buttonframe, text='Start', font=font, text_color='black', height=buttonheight, corner_radius=20,
    fg_color="#f6f6f6", hover_color="#6bbc79", command=toggle_start)
btn1.grid(row=0, column=0, padx=(10,3), sticky='we')

btn2 = ctk.CTkButton(buttonframe, text='Quit', font=font, text_color='black', height=buttonheight, corner_radius=20, 
    fg_color="#f6f6f6", hover_color="#d66b6b", command=close_program)
btn2.grid(row=0, column=1, padx=(3,10), sticky='we')

buttonframe.pack(fill='x')


slider_frame = ctk.CTkFrame(window, fg_color="transparent")
slider_frame.pack(padx=10, pady=(5, 10), fill='x')

slider_frame.columnconfigure(0, weight=1)  # suwak
slider_frame.columnconfigure(1, weight=0)  # wartość

ratio_label = ctk.CTkLabel(
    slider_frame,
    text="Próg pozwala ustawić czułość wykrywania zębów",
    font=('Segoe UI', 14)
)
ratio_label.grid(row=0, column=0, columnspan=2, sticky='we', pady=(0, 5))

ratio_slider = ctk.CTkSlider(
    slider_frame,
    from_=1,
    to=10,
    number_of_steps=18,
    command=update_ratio_label,
    button_color="#424048",
    button_hover_color="#2A292C"
)
ratio_slider.set(teeth_ratio_threshold)
ratio_slider.grid(row=1, column=0, sticky='we', padx=5)

ratio_value_label = ctk.CTkLabel(
    slider_frame,
    text=f"{teeth_ratio_threshold:.1f}",
    font=('Segoe UI', 18)
)
ratio_value_label.grid(row=1, column=1, padx=(0, 5))


# START
update_frame()
window.mainloop()

cap.release()
cv2.destroyAllWindows()

