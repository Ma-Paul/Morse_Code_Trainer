import customtkinter
def button_callback():
    button = customtkinter.CTkButton(app, text="1 Knopf", command=button_callback, fg_color="#076df2")
    button.grid(row=0, column=0, padx=60, pady=20, sticky="ew")

app = customtkinter.CTk()
app.title("myApp")
app.geometry("600x150")

button = customtkinter.CTkButton(app, text="1 Knopf", command=button_callback, fg_color="#078cf2")
button.grid(row=0, column=0, padx=60, pady=20, sticky="ew")
button2 = customtkinter.CTkButton(app, text="2 Knöpfe", command=button_callback)
button2.grid(row=0, column=1, padx=60, pady=20, sticky="ew")
app.mainloop()