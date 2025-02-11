import tkinter as tk
from tkinter import messagebox
import sqlite3
from PIL import Image, ImageTk  # Importer depuis Pillow
import pygame
import os  # Pour vérifier si l'image existe

pygame.mixer.init()

# Musiques disponibles
music_list = ["overcooked.mp3", "instru.mp3", "ff7.mp3", "12.mp3"]
current_music_index = 0  # Index de la musique actuellement en cours

# Musique initiale
current_music = music_list[current_music_index]
pygame.mixer.music.load(current_music)
pygame.mixer.music.play(-1, 0.0)  # -1 signifie que la musique boucle indéfiniment
pygame.mixer.music.set_volume(1.0)  # Volume à fond
current_volume = 1.0  # Volume à fond

# Connexion à la base de données
mydb = sqlite3.connect("crazy_kitchen_database.db")
mycursor = mydb.cursor()
result = mycursor.execute("SELECT * FROM ingredient")
ingredients = result.fetchall()
userIngredients = []


def get_recipe(ingredientss):
    mycursor = mydb.cursor()
    placeholders = ','.join(['?'] * len(ingredientss))
    query = f"""
        SELECT r.*  
        FROM recette r 
        JOIN ingredientsrecette ir ON r.id = ir.recetteid
        WHERE ir.ingredientId IN {tuple(ingredientss)}
        GROUP BY r.id, r.nom
        HAVING COUNT(DISTINCT ir.ingredientId) >= 2
        ORDER BY r.id DESC
        LIMIT 1
    """
    mycursor.execute(query)  # Passer la liste en tant que tuple
    recette = mycursor.fetchone()  # Nous ne prenons que la première recette trouvée
    if recette:
        show_recipe_page(recette)  # Afficher la recette dans une nouvelle page
    else:
        # Lancer la musique "sad.mp3" si aucune recette n'est trouvée
        try:
            sad_music = pygame.mixer.Sound("sad.mp3")
            sad_music.set_volume(1.0)  # Mettre le volume à fond
            sad_music.play()  # Jouer la musique "sad.mp3"
        except Exception as e:
            print(f"Erreur lors de la lecture de la musique sad.mp3: {e}")

        messagebox.showinfo("Recette", "Aucune recette trouvée avec ces ingrédients.")


# Fonction pour afficher la recette dans une nouvelle page
def show_recipe_page(recette):
    # Créer une nouvelle fenêtre pour afficher la recette
    recipe_window = tk.Toplevel(app)  # Créer une nouvelle fenêtre
    recipe_window.title("Recette obtenue")
    recipe_window.geometry("800x800")
    
    # Titre de la recette
    recipe_title_label = tk.Label(recipe_window, text=f"Recette : {recette[1]}", font=("Arial", 12))
    recipe_title_label.pack(pady=20)
    
    # Charger l'image de la recette (ici, on prend le 3ème élément de la table `recette`)
    image_path = recette[2]  # L'image se trouve dans le 3ème élément de la table 'recette'
    
    if image_path:  # Vérifier que l'image existe
        if os.path.exists(image_path):  # Vérifier si l'image existe à ce chemin
            try:
                recipe_image = Image.open(image_path)  # Ouvrir l'image
                recipe_image = recipe_image.resize((250, 250))  # Redimensionner l'image
                recipe_image_tk = ImageTk.PhotoImage(recipe_image)
                recipe_image_label = tk.Label(recipe_window, image=recipe_image_tk)
                recipe_image_label.image = recipe_image_tk  # Garder une référence de l'image
                recipe_image_label.pack(pady=20)
            except Exception as e:
                print(f"Erreur lors du chargement de l'image: {e}")
                recipe_image_label = tk.Label(recipe_window, text="Erreur de chargement de l'image")
                recipe_image_label.pack(pady=20)
        else:
            recipe_image_label = tk.Label(recipe_window, text="Image non trouvée")
            recipe_image_label.pack(pady=20)
    else:
        recipe_image_label = tk.Label(recipe_window, text="Aucune image disponible")
        recipe_image_label.pack(pady=20)
    
    # Lancer la musique w.mp3 en parallèle sans arrêter la musique en cours
    try:
        w_music = pygame.mixer.Sound("w.mp3")
        w_music.set_volume(1.0)  # Mettre le volume à fond
        w_music.play()  # Jouer la musique en parallèle
    except Exception as e:
        print(f"Erreur lors de la lecture de la musique w.mp3: {e}")
    
    # Bouton pour fermer la fenêtre de recette
    close_button = tk.Button(recipe_window, text="Fermer", command=recipe_window.destroy)
    close_button.pack(pady=10)


# Fonction pour changer de musique
def toggle_music():
    global current_music_index
    # Arrêter la musique actuelle
    pygame.mixer.music.stop()
    
    # Passer à la prochaine musique dans la liste
    current_music_index = (current_music_index + 1) % len(music_list)  # Boucle à travers les musiques
    
    # Charger et jouer la nouvelle musique
    new_music = music_list[current_music_index]
    pygame.mixer.music.load(new_music)  # Charger la nouvelle musique
    pygame.mixer.music.play(-1, 0.0)  # Lire la musique en boucle
    pygame.mixer.music.set_volume(1.0)  # Volume à fond


# Fonction pour gérer le clic sur un ingrédient
def on_ingredient_click(ingredient_id):
    print(ingredient_id)
    userIngredients.append(ingredient_id)
    selected_ingredients_text = ", ".join([ingredient[1] for ingredient in ingredients if ingredient[0] in userIngredients])
    counter_label.config(text=f"Ingrédients sélectionnés: {selected_ingredients_text}\nNombre d'ingrédients cliqués: {len(userIngredients)}")
    if len(userIngredients) > 2:
        get_recipe(userIngredients)


# Fonction pour supprimer tous les ingrédients sélectionnés
def clear_ingredients():
    global userIngredients
    userIngredients = []  # Réinitialiser la liste des ingrédients sélectionnés
    counter_label.config(text="Ingrédients sélectionnés: \nNombre d'ingrédients cliqués: 0")  # Réinitialiser l'affichage du compteur


def start_program():
    menu_frame.pack_forget()  # Cacher le menu
    app_frame.pack(fill="both", expand=True)  # Afficher le programme principal
    # Changer la couleur de fond en noir après le lancement du jeu
    app_frame.config(bg="black")  # Changer la couleur de fond en noir
    # Changer la musique après 5 secondes
    pygame.mixer.music.stop()  # Arrêter la musique actuelle (overcooked.mp3)
    pygame.mixer.music.load("instru.mp3")  # Charger la nouvelle musique
    pygame.mixer.music.play(0, 5.0)  # Lire la musique après 5 secondes
    pygame.mixer.music.set_volume(1.0)  # Volume à fond


# Fonction pour afficher les crédits
def show_credits():
    credits_window = tk.Toplevel(app)  # Créer une nouvelle fenêtre
    credits_window.title("Crédits")
    credits_window.geometry("400x200")
    
    credits_label = tk.Label(credits_window, text="Crédits\n\nDéveloppé par: Efe et Idriss", font=("Arial", 12), justify="center")
    credits_label.pack(pady=20)
    
    # Bouton pour fermer la fenêtre des crédits
    close_button = tk.Button(credits_window, text="Fermer", command=credits_window.destroy)
    close_button.pack(pady=10)


# Fonction pour gérer la pression sur la touche 'y'
def on_key_press(event):
    if event.char == 'y' or event.char == 'Y':  # Vérifier si 'y' ou 'Y' est pressé
        show_credits()  # Afficher les crédits


# Lier l'événement de pression de touche 'y' à la fonction on_key_press
app = tk.Tk()
app.title("Crazy kitchen deluxe")
app.geometry("1280x720")

# Charger l'image de fond du menu
menu_image = Image.open("ck_menu.png")
menu_image_tk = ImageTk.PhotoImage(menu_image)

# Frame du menu
menu_frame = tk.Frame(app)
menu_frame.pack(fill="both", expand=True)

# Label de fond pour le menu
bg_label = tk.Label(menu_frame, image=menu_image_tk)
bg_label.place(relwidth=1, relheight=1)  # Remplir toute la frame avec l'image

# Bouton pour démarrer le programme (placer au centre de la fenêtre)
start_button = tk.Button(menu_frame, text="Lancer le launcher", command=start_program, font=("Arial", 14))
start_button.place(relx=0.5, rely=0.5, anchor="center")  # Placer le bouton au centre de la fenêtre

# Frame du programme principal (initialement cachée)
app_frame = tk.Frame(app)

# Créer un label pour afficher le compteur et les ingrédients sélectionnés
counter_label = tk.Label(app_frame, text="Ingrédients sélectionnés: \nNombre d'ingrédients cliqués: 0", font=("Arial", 14), fg="black")
counter_label.pack(pady=20)

# Créer un label pour l'image marmite et la placer au centre
marmite_image = Image.open("marmite.png")
marmite_image = marmite_image.resize((500, 500))  # Adapter la taille de l'image
marmite_image_tk = ImageTk.PhotoImage(marmite_image)

marmite_label = tk.Label(app_frame, image=marmite_image_tk)
marmite_label.place(relx=0.5, rely=0.5, anchor="center")  # Placer l'image au centre de la fenêtre

# Créer une Canvas pour le défilement horizontal des boutons d'ingrédients
canvas = tk.Canvas(app_frame, bg="white", height=100)
canvas.pack(fill="x", pady=20)

# Ajouter une barre de défilement horizontale
scrollbar = tk.Scrollbar(app_frame, orient="horizontal", command=canvas.xview)
scrollbar.pack(fill="x", side="bottom")

canvas.config(xscrollcommand=scrollbar.set)

# Créer une Frame à l'intérieur de la Canvas pour contenir les boutons d'ingrédients
ingredient_frame = tk.Frame(canvas)

# Utiliser la méthode create_window pour placer la Frame dans la Canvas
canvas.create_window((0, 0), window=ingredient_frame, anchor="nw")

# Mettre à jour la région de défilement de la canvas pour s'adapter à tous les boutons
def update_scroll_region(event):
    canvas.config(scrollregion=canvas.bbox("all"))

ingredient_frame.bind("<Configure>", update_scroll_region)

# Afficher les boutons des ingrédients avec des images dans ingredient_frame
for id, nom, type, image in ingredients:
    frame = tk.Frame(ingredient_frame)
    frame.pack(side="left", padx=100)  # Centrer les ingrédients horizontalement

    if image:
        img = Image.open(image)
        img = img.resize((60, 60))
        tk_img = ImageTk.PhotoImage(img)
        btn = tk.Button(frame, image=tk_img, command=lambda id=id: on_ingredient_click(id))
        btn.image = tk_img
        btn.pack()
    else:
        btn = tk.Button(frame, text=nom, command=lambda id=id: on_ingredient_click(id))
        btn.pack()

    label = tk.Label(frame, text=nom, fg="black")  # Texte en blanc pour bien contraster sur fond noir
    label.pack()

# Charger l'image du bouton pour changer de musique
music_button_image = Image.open("boutton.png")
music_button_image = music_button_image.resize((100, 100))  # Ajuster la taille si nécessaire
music_button_image_tk = ImageTk.PhotoImage(music_button_image)

# Remplacer le bouton texte par le bouton image
music_button = tk.Button(app_frame, image=music_button_image_tk, command=toggle_music)
music_button.image = music_button_image_tk  # Garder une référence à l'image
music_button.pack(side="bottom", anchor="se", padx=10, pady=10)

# Charger l'image du bouton supprimer (delete.png)
delete_button_image = Image.open("delete.PNG")
delete_button_image = delete_button_image.resize((150, 150))  # Ajuster la taille si nécessaire
delete_button_image_tk = ImageTk.PhotoImage(delete_button_image)

# Remplacer le bouton texte par le bouton image
delete_button = tk.Button(app_frame, image=delete_button_image_tk, command=clear_ingredients)
delete_button.image = delete_button_image_tk  # Garder une référence à l'image
delete_button.pack(side="bottom", anchor="sw", padx=20, pady=20)  # Placer le bouton en bas à gauche

# Lier l'événement de la touche 'y' pour afficher les crédits
app.bind("<KeyPress>", on_key_press)

# Exécuter l'application
app.mainloop()





