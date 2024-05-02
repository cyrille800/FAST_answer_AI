import tkinter as tk
from tkinter import ttk, PhotoImage
import pyautogui
import time
from communicatechatgpt import get_reponse_chat_gpt
from ScreenCaptureTool import ScreenCaptureTool
from pynput import keyboard
import chardet


# Fonction pour changer la couleur de fond du bouton
def update_button_color(is_enabled):
    global is_ocr
    color = 'purple' if is_enabled else 'black'
    is_ocr = not is_ocr
    ocr_btn.config(background=color)
    
    
def send_screens():
    
    global wait, tab_screen, counter, components, start_
    wait = True

    try:

        # Masquer la fenêtre principale pendant la capture
        app.withdraw()
        time.sleep(0.5)  # Laisse du temps pour que la fenêtre principale soit cachée
        
        # Simuler une demande à une API ou autre traitement ici
        get_reponse_chat_gpt(tab_screen, is_ocr = is_ocr, pat = start_)

        tab_screen = []
        counter = 1
        reload_content(components)
        start_ = time.time()

        time.sleep(0.5)
        app.deiconify()
        wait = False
    except Exception as e:
        # messagebox.showerror("Erreur", str(e))
        app.deiconify()
        wait = False
        
def exit_app():
    app.destroy()

def on_enter(e, btn):
    btn.config(background='gray')  # Change la couleur de fond au survol

def on_leave(e, btn):
    btn.config(background='black')  # Restaure la couleur de fond originale quand la souris quitte le bouton

def on_press(key):

    if key == keyboard.Key.alt_gr and wait==False:
        send_screens()
    
def reload_content(components):
    notebook = components['notebook']
    tabs_info = components['tabs_info']
    general_text_widget = components['general_text_widget']
    text_widgets = components['text_widgets']

    general_text_widget.config(state="normal")
    general_text_widget.delete("1.0", tk.END)

    all_content = ""
    separator = "\n"

    for index, (tab_name, file_name) in enumerate(tabs_info):
        text_widget = text_widgets[index]
        text_widget.config(state="normal")
        text_widget.delete("1.0", tk.END)

        try:
            with open(file_name, 'rb') as file:
                raw_data = file.read()
            encoding = chardet.detect(raw_data)['encoding']
            file_content = raw_data.decode(encoding)
            text_widget.insert("end", file_content)
        except FileNotFoundError:
            file_content = f"Le fichier {file_name} n'a pas été trouvé.\n"
            text_widget.insert("end", file_content)
        except UnicodeDecodeError:
            file_content = "Erreur de décodage après détection automatique de l'encodage.\n"
            text_widget.insert("end", file_content)

        text_widget.config(state="disabled")

        if all_content:
            general_text_widget.insert("end", separator, "separator")
        general_text_widget.insert("end", f"Contenu de {tab_name}:\n{file_content}\n", "file_content")

    general_text_widget.config(state="disabled")

def open_tabbed_window(app):
    
    #initialisaitn de la fenetre
    new_window = tk.Toplevel(app)
    new_window.title("Contenu des fichiers")
    new_window.attributes('-alpha', 0.8)
    new_window.configure(background='black')

    #Style de la fenetre
    notebook = ttk.Notebook(new_window)
    style = ttk.Style(new_window)
    style.theme_use('default')
    style.configure('TNotebook', background='black', borderwidth=0)
    style.configure('TNotebook.Tab', background='#ccc', foreground='black', padding=[20, 10], font=('Helvetica', 10, 'bold'), borderwidth=2, relief='solid', bordercolor='black')
    style.map('TNotebook.Tab', background=[('selected', '#7D4FFE'), ('active', '#cecece')])
    style.configure('TFrame', background='black', borderwidth=0)

    #Creation d'une page par fichier
    general_frame = ttk.Frame(notebook, style='TFrame')
    notebook.add(general_frame, text="General")
    general_text_widget = tk.Text(general_frame, wrap="word", height=55, width=50, bg='black', fg='white', borderwidth=0, relief='flat')
    general_text_widget.pack(expand=True, fill='both')

    tabs_info = [("GPT", "gpt.txt"), ("Gemini", "gemini.txt"), ("Opus", "opus.txt")]
    text_widgets = []

    for tab_name, file_name in tabs_info:
        tab_frame = ttk.Frame(notebook, style='TFrame')
        notebook.add(tab_frame, text=tab_name)
        text_widget = tk.Text(tab_frame, wrap="word", height=55, width=100, bg='black', fg='white', borderwidth=0, relief='flat')
        text_widget.pack(expand=True, fill='both')
        text_widgets.append(text_widget)

    #retourner les widget creer
    components = {
        'notebook': notebook,
        'tabs_info': tabs_info,
        'general_text_widget': general_text_widget,
        'text_widgets': text_widgets
    }

    notebook.pack(expand=True, fill='both')
    return components
    

def screen_tab():
    global app_screen,counter, tab_screen, start_
    app_screen.start_capture(start_, counter)
    tab_screen.append(f"screenshot{counter}.png")

    counter +=1

def on_press_window(event):
    # Enregistrer la position initiale de la souris
    app._drag_start_x = event.x
    app._drag_start_y = event.y

def on_drag_window(event):
    # Calculer le déplacement relatif à la position initiale
    dx = event.x - app._drag_start_x
    dy = event.y - app._drag_start_y
    
    # Déplacer la fenêtre de ce déplacement
    x = app.winfo_x() + dx
    y = app.winfo_y() + dy
    app.geometry(f"+{x}+{y}")
    
def load_icon(icon_filename):
    """Charge une icône et retourne un objet PhotoImage."""
    return PhotoImage(file=icon_filename)

def create_button(parent, image, command=None, on_enter=None, on_leave=None, bind_left_click=None, bind_drag=None,
                  background='black', borderwidth=0, highlightthickness=0, relief='flat', cursor=None, width=None, height=None, pady=(0, 0)):
    """Crée et retourne un bouton configuré."""
    btn = tk.Button(parent, image=image, command=command, background=background, borderwidth=borderwidth,
                    highlightthickness=highlightthickness, relief=relief, cursor=cursor, width=width, height=height)
    btn.pack(pady=pady)
    if bind_left_click:
        btn.bind("<Button-1>", bind_left_click)
    if bind_drag:
        btn.bind("<B1-Motion>", bind_drag)
    if on_enter:
        btn.bind("<Enter>", lambda e, btn=btn: on_enter(e, btn))
    if on_leave:
        btn.bind("<Leave>", lambda e, btn=btn: on_leave(e, btn))
    return btn

if __name__ =="__main__":
    
    selected_title = ""
    wait = False
    counter = 1
    tab_screen = []
    is_ocr = True
        
    start_ = time.time()

    current_keys = set()

    tab_screen = []
        
    # Listener pour surveiller les événements de clavier
    listener = keyboard.Listener(on_press=on_press)
    listener.start()


    app = tk.Tk()
    app_screen = ScreenCaptureTool(app)

    app.title("Selectionner une fenetre")
    app.overrideredirect(True)
    app.configure(background='black')

    # Bind the mouse enter and leave events

    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    window_width = 100
    window_height = 400
    x = screen_width - window_width - 20
    y = (screen_height - window_height) // 2
    app.geometry(f'{window_width}x{window_height}+{x}+{y}')
    app.attributes('-topmost', True)
    app.lift()  # Place la fenêtre au premier plan lors de sa création


    # Dictionnaire des noms de fichiers des icônes
    icon_files = {
        'chat_gpt': 'chatgpt.png',
        'ocr_img': 'ocr.png',
        'tapScreen': 'tapScreen.png',
        'icon_close': 'close.png',
        'icon_setting': 'setting.png',
        'icon_reponse': 'reponse.png'
    }

    # Chargement des icônes
    icons = {key: load_icon(filename) for key, filename in icon_files.items()}

    # Affectation directe des variables
    chat_gpt, ocr_img, tapScreen, icon_close, icon_setting, icon_reponse = (
        icons["chat_gpt"], icons["ocr_img"], icons["tapScreen"], icons["icon_close"], icons["icon_setting"], icons["icon_reponse"]
    )

    components = open_tabbed_window(app)

    open_combobox_btn = create_button(app, image=chat_gpt, cursor="fleur", bind_left_click=on_press_window, bind_drag=on_drag_window)
    ocr_btn = create_button(app, image=ocr_img, command=lambda: update_button_color(not is_ocr), height=80)
    open_combotapScreen = create_button(app, image=tapScreen, command=screen_tab, width=100, pady=(10, 0), on_enter=on_enter, on_leave=on_leave)
    exit_btn = create_button(app, image=icon_close, command=exit_app, width=100, pady=(30, 0), on_enter=on_enter, on_leave=on_leave)
    reponse_btn = create_button(app, image=icon_reponse, command=lambda: reload_content(components), width=100, pady=(10, 20), on_enter=on_enter, on_leave=on_leave)

    app.mainloop()