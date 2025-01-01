from tkinter import Tk, Label, Button, Frame, Canvas, Scrollbar, Text, Entry, Listbox
import requests
from PIL import Image, ImageTk
from io import BytesIO

# ---------- GUI Initialization ----------

# Initialize the GUI
root = Tk()
root.geometry("600x800")  # Set the window size
root.title("Random Meal Viewer")  # Set the window title
root.resizable(False, False)  # Disable window resizing

# ---------- Function: Set Background ----------

def set_background(canvas, image_path):
    """Set a background image for the canvas."""
    try:
        bg_image = Image.open(image_path).resize((600, 800), Image.LANCZOS)
        bg_image = ImageTk.PhotoImage(bg_image)
        canvas.create_image(0, 0, anchor="nw", image=bg_image)
        canvas.bg_image = bg_image  # Prevent garbage collection
    except Exception as e:
        print(f"Error loading background image: {e}")

# ---------- Function: Fetch Random Meal ----------

def get_random_meal():
    """Fetch a random meal and display its details."""
    url = "https://www.themealdb.com/api/json/v1/1/random.php"
    try:
        response = requests.get(url)
        response.raise_for_status()
        meal = response.json().get("meals", [None])[0]

        if meal:
            # Update meal name
            mealName.config(text=meal.get("strMeal", "Unknown Meal"))

            # Update meal instructions
            instructions = meal.get("strInstructions", "No instructions available.")
            mealInstructions.config(state="normal")  # Enable editing
            mealInstructions.delete(1.0, "end")  # Clear previous text
            mealInstructions.insert("end", instructions)
            mealInstructions.config(state="disabled")  # Disable editing

            # Fetch and display meal image
            image_url = meal.get("strMealThumb", "")
            if image_url:
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    image = Image.open(BytesIO(image_response.content)).resize((200, 200), Image.LANCZOS)
                    meal_image = ImageTk.PhotoImage(image)
                    mealImageLabel.config(image=meal_image)
                    mealImageLabel.image = meal_image
                else:
                    mealImageLabel.config(image="", text="Image not available")
            else:
                mealImageLabel.config(image="", text="Image not available")
        else:
            # Handle case where no meal data is returned
            mealName.config(text="No meal found.")
            mealInstructions.config(state="normal")
            mealInstructions.delete(1.0, "end")
            mealInstructions.config(state="disabled")
            mealImageLabel.config(image="", text="")

    except requests.exceptions.RequestException as e:
        # Handle errors from the API request
        mealName.config(text="Error fetching meal")
        mealInstructions.config(state="normal")
        mealInstructions.delete(1.0, "end")
        mealInstructions.insert("end", str(e))
        mealInstructions.config(state="disabled")
        mealImageLabel.config(image="", text="")

# ---------- Function: Meal By Name ----------

def meal_by_name():
    """Display a new frame with a search bar and a scrollable list of meals."""

    def search_meals():
        """Fetch meals matching the search query."""
        query = search_entry.get().strip()
        if not query:
            result_label.config(text="Please enter a meal name.")
            return

        url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            meals = response.json().get("meals", [])

            # Clear the list
            list_frame.delete(0, "end")

            if meals:
                for meal in meals:
                    list_frame.insert("end", meal["strMeal"])
                result_label.config(text=f"Found {len(meals)} meal(s).")
                list_frame.meals_data = meals  # Store meals data
            else:
                result_label.config(text="No meals found.")

        except requests.exceptions.RequestException as e:
            result_label.config(text=f"Error: {str(e)}")

    def show_meal_details(event):
        """Display details of the selected meal."""
        selection = list_frame.curselection()
        if not selection:
            return

        index = selection[0]
        meal = list_frame.meals_data[index]  # Get the selected meal data

        # Create a new frame for meal details
        details_frame = Frame(root, bg="#F7F7FF")
        details_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Meal Name
        Label(
            details_frame, 
            text=meal.get("strMeal", "Unknown Meal"), 
            font=("Calibri", 24, "bold", "italic"), 
            fg="#E0BE36", 
            bg="#F7F7FF"
        ).pack(pady=10)

        # Meal Image
        image_url = meal.get("strMealThumb", "")
        if image_url:
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                image = Image.open(BytesIO(image_response.content)).resize((200, 200), Image.LANCZOS)
                meal_image = ImageTk.PhotoImage(image)
                image_label = Label(details_frame, image=meal_image, bg="#F7F7FF")
                image_label.image = meal_image
                image_label.pack(pady=10)

        # Meal Instructions
        instructions = meal.get("strInstructions", "No instructions available.")
        instructions_frame = Frame(details_frame, bg="#F7F7FF")
        instructions_frame.pack(pady=10, fill="both", expand=True)

        scrollbar = Scrollbar(instructions_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        instructions_text = Text(
            instructions_frame, 
            wrap="word", 
            font=("Arial", 10), 
            fg="#8D7516", 
            bg="#F4F5F5", 
            yscrollcommand=scrollbar.set
        )
        instructions_text.insert("end", instructions)
        instructions_text.config(state="disabled")  # Disable editing
        instructions_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=instructions_text.yview)

        # Back Button
        Button(
            details_frame, 
            text="Back", 
            command=details_frame.destroy, 
            font=("Arial", 14), 
            fg="#F7F7FF", 
            bg="#D9534F"
        ).pack(pady=10)

    # Create a new frame for searching meals
    new_frame = Frame(root, bg="#F7F7FF")
    new_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    # Title
    Label(
        new_frame, 
        text="Search Meals by Name", 
        font=("Calibri", 24, "bold", "italic"), 
        fg="#E0BE36", 
        bg="#F7F7FF"
    ).pack(pady=10)

    # Search bar
    search_entry = Entry(new_frame, font=("Arial", 14), width=30)
    search_entry.pack(pady=10)

    # Search button
    Button(
        new_frame, 
        text="Search", 
        command=search_meals, 
        font=("Arial", 14), 
        fg="#F7F7FF", 
        bg="#F38816"
    ).pack(pady=5)

    # Result label
    result_label = Label(new_frame, text="", font=("Arial", 12), fg="#8D7516", bg="#F7F7FF")
    result_label.pack(pady=5)

    # Scrollable list of meals
    listbox_frame = Frame(new_frame, bg="#F7F7FF")
    listbox_frame.pack(pady=10, fill="both", expand=True)

    scrollbar = Scrollbar(listbox_frame, orient="vertical")
    scrollbar.pack(side="right", fill="y")

    list_frame = Listbox(
        listbox_frame, 
        font=("Arial", 12), 
        yscrollcommand=scrollbar.set, 
        height=20, 
        width=50
    )
    list_frame.pack(side="left", fill="both", expand=True)
    list_frame.bind("<<ListboxSelect>>", show_meal_details)  # Bind item click event
    list_frame.meals_data = []  # Store meal data in the Listbox widget

    scrollbar.config(command=list_frame.yview)

    # Back button
    Button(
        new_frame, 
        text="Back", 
        command=new_frame.destroy, 
        font=("Arial", 14), 
        fg="#F7F7FF", 
        bg="#D9534F"
    ).pack(pady=10)

# ---------- Canvas Setup ----------

canvas = Canvas(root, width=600, height=800)
canvas.pack(fill="both", expand=True)

# Set the Background Image
image_path = r"C:\\Users\\Emelyn\\Documents\\ASSESSMENTS\\L5 SEMESTER 1\\Advanced Programming\\AP A2\\khloe-arledge-Xu7W4u5lG9g-unsplash.jpg"
set_background(canvas, image_path)

# ---------- Main Frame Setup ----------

main_frame = Frame(canvas, bd=2, relief="raised", bg="#F7F7FF")
main_frame.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)

# Title Label
Label(
    main_frame, 
    text=" Random Meal Viewer ", 
    font=("Calibri", 32, "bold", "italic"), 
    fg="#E0BE36",
    bg="#F7F7FF"
).pack(pady=10)

# Button to Fetch a Random Meal
Button(
    main_frame, 
    text="Get Random Meal", 
    command=get_random_meal, 
    font=("Arial", 20),
    fg="#F7F7FF",
    bg="#F38816"
).pack(pady=8)

# Button to switch to Meal By Name
Button(
    main_frame, 
    text="Meal By Name", 
    command=meal_by_name, 
    font=("Arial", 20),
    fg="#F7F7FF",
    bg="#F38816"
).pack(pady=8)

# Meal Name Label
mealName = Label(
    main_frame, 
    text="", 
    font=("Calibri", 24, "bold", "italic"), 
    wraplength=420, 
    fg="#E0BE36",
    bg="#F7F7FF"
)
mealName.pack(pady=10)

# Meal Image Label
mealImageLabel = Label(main_frame, fg="#E0BE36", bg="#F7F7FF")
mealImageLabel.pack(pady=10)

# Scrollable Meal Instructions
scroll_frame = Frame(main_frame)
scroll_frame.pack(pady=10, fill="both", expand=True)

scrollbar = Scrollbar(scroll_frame, orient="vertical")
scrollbar.pack(side="right", fill="y")

mealInstructions = Text(
    scroll_frame, 
    wrap="word", 
    font=("Arial", 10), 
    fg="#8D7516", 
    bg="#F4F5F5", 
    yscrollcommand=scrollbar.set, 
    height=10, 
    width=50
)
mealInstructions.pack(side="left", fill="both", expand=True)
mealInstructions.config(state="disabled")  # Disable editing

scrollbar.config(command=mealInstructions.yview)

# ---------- Run the Application ----------

root.mainloop()
