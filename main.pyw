import sqlite3
import tkinter.messagebox
from tkinter import *

create_productos_table = '''create table products (
        id integer primary key autoincrement,
        description text not null,
        price real not null,
        quantity integer not null
    )'''

conn = sqlite3.connect('inventario')
print('Migrando tablas')
try:
    conn.execute(create_productos_table)
except sqlite3.OperationalError:
    print('Ya existen las tablas')

font = 'Comic Sans MS'
input_config = {'padx': 5, 'pady': 5, 'bg': 'lightgray', 'font': (font, 10)}
root_bg = 'white'

root = Tk()
root.title('Inventario de productos')
root.iconbitmap('youtube.ico')
root.geometry('1280x720')
root.config(bg=root_bg)

frame = LabelFrame(bg='lightgray', text='Creación/Edición')
frame.pack(fill=BOTH, padx=10, pady=10)

id_producto_valor = IntVar()
nombre_producto_valor = StringVar()
precio_producto_valor = DoubleVar()
cantidad_producto_valor = IntVar()
boton_formulario_valor = StringVar(value='Crear Producto')


def reset_form():
    global nombre_producto_valor
    global precio_producto_valor
    global cantidad_producto_valor
    global editando
    global boton_formulario_valor

    boton_formulario_valor.set('Crear Producto')
    nombre_producto_valor.set('')
    precio_producto_valor.set(0.0)
    cantidad_producto_valor.set(0)
    editando = False


def guardar_producto():
    global nombre_producto_valor
    global precio_producto_valor
    global cantidad_producto_valor
    global editando
    nombre_producto = nombre_producto_valor.get()
    precio_producto = precio_producto_valor.get()
    cantidad_producto = cantidad_producto_valor.get()

    if nombre_producto == '' or precio_producto == 0.0 or cantidad_producto == 0:
        tkinter.messagebox.showerror('Error', 'Por favor complete todos los campos')
        return

    if editando:
        global id_producto_valor

        query = 'update products set description = ?, price = ?, quantity = ? where id = ?'
        conn.execute(query, (nombre_producto, precio_producto, cantidad_producto, id_producto_valor.get()))
    else:
        query = 'insert into products (description, price, quantity) values (?, ?, ?)'
        conn.execute(query, (nombre_producto, precio_producto, cantidad_producto))

    conn.commit()
    refresh_products()
    action = 'editado' if editando else 'creado'
    tkinter.messagebox.showinfo(f'Producto {action}', f'El producto fue {action} con éxito')
    reset_form()


def refresh_products():
    global listado_frame

    for widget in listado_frame.winfo_children():
        widget.destroy()
    mostrar_productos()


def preparar_edicion(id):
    global nombre_producto_valor
    global precio_producto_valor
    global cantidad_producto_valor
    global boton_formulario_valor
    global editando

    print(f'Editando producto con id: {id}')
    editando = True
    boton_formulario_valor.set('Editar Producto')
    query = 'select description, price, quantity from products where id = ?'
    producto = conn.execute(query, (id,)).fetchone()
    id_producto_valor.set(id)
    nombre_producto_valor.set(producto[0])
    precio_producto_valor.set(producto[1])
    cantidad_producto_valor.set(producto[2])


def borrar_producto(id):
    query = 'delete from products where id = ?'
    conn.execute(query, (id,))
    conn.commit()
    refresh_products()
    tkinter.messagebox.showinfo('Producto borrado', 'El producto fue borrado con éxito')


# Form

editando = False
nuevo_producto_button = Button(frame, text='Nuevo Producto', bg='gray', font=(font, 10), command=reset_form, )
nuevo_producto_button.grid(row=0, column=3, padx=5, pady=5)

nombre_producto_label = Label(frame, text='Nombre de producto', **input_config)
nombre_producto_label.grid(row=0, column=0)
nombre_producto_input = Entry(frame, font=(font, 10), bg='white', textvariable=nombre_producto_valor)
nombre_producto_input.grid(row=0, column=1)

precio_producto_label = Label(frame, text='Precio', **input_config)
precio_producto_label.grid(row=1, column=0)
precio_producto_input = Entry(frame, font=(font, 10), bg='white', textvariable=precio_producto_valor)
precio_producto_input.grid(row=1, column=1)

cantidad_producto_label = Label(frame, text='Cantidad', **input_config)
cantidad_producto_label.grid(row=2, column=0)
cantidad_producto_input = Entry(frame, font=(font, 10), bg='white', textvariable=cantidad_producto_valor)
cantidad_producto_input.grid(row=2, column=1)

button = Button(frame, textvariable=boton_formulario_valor, bg='gray', font=(font, 10), command=guardar_producto)
button.grid(row=3, column=0, columnspan=4, sticky='nsew', padx=5, pady=5)


def scroll(canvas):
    canvas.configure(scrollregion=canvas.bbox('all'))


canvas = Canvas(root, bg='lightgray', bd=1, relief='raised')
canvas.pack(side=LEFT, padx=10, pady=10, fill=BOTH, expand=True)

listado_frame = LabelFrame(canvas, bg='lightgray', text='Listado de productos')
listado_frame.pack(fill=BOTH, padx=10, pady=10, expand=True)

scroll_bar = Scrollbar(root, command=canvas.yview)
scroll_bar.pack(side=RIGHT, fill=Y, padx=10, pady=10)

listado_frame.bind('<Configure>', lambda event: scroll(canvas))

canvas.config(yscrollcommand=scroll_bar.set)
canvas.create_window((0, 0), window=listado_frame, anchor='nw')


# Listado de productos

def mostrar_productos():
    productos = conn.execute('select id, description, price, quantity from products').fetchall()
    id_titulo = Label(listado_frame, text='Id de producto', **input_config, bd=2, relief="raised", width=20)
    id_titulo.grid(row=0, column=0, sticky='ew')
    nombre_producto = Label(listado_frame, text='Nombre', **input_config, bd=2, relief="raised", width=20)
    nombre_producto.grid(row=0, column=1, sticky='ew')
    precio_producto = Label(listado_frame, text='Precio', **input_config, bd=2, relief="raised", width=20)
    precio_producto.grid(row=0, column=2, sticky='ew')
    cantidad_producto = Label(listado_frame, text='Cantidad', **input_config, bd=2, relief="raised", width=20)
    cantidad_producto.grid(row=0, column=3, sticky='ew')
    acciones = Label(listado_frame, text='Acciones', **input_config, bd=2, relief="raised", width=40)
    acciones.grid(row=0, column=4, columnspan=2, sticky='ew')
    for i in range(0, len(productos)):
        id_producto = Label(listado_frame, text=productos[i][0], **input_config, bd=2, relief='raised', width=20)
        id_producto.grid(row=i + 1, column=0, sticky='ew')

        nombre_producto = Label(listado_frame, text=productos[i][1], **input_config, bd=2, relief='raised', width=20)
        nombre_producto.grid(row=i + 1, column=1, sticky='ew')

        precio_producto = Label(listado_frame, text=f'$ {round(productos[i][2], 2)}', **input_config, bd=2,
                                relief='raised', width=20)
        precio_producto.grid(row=i + 1, column=2, sticky='ew')

        cantidad_producto = Label(listado_frame, text=int(productos[i][3]), **input_config, bd=2, relief='raised',
                                  width=20)
        cantidad_producto.grid(row=i + 1, column=3, sticky='ew')

        id = int(productos[i][0])
        boton_editar = Button(listado_frame, text='Editar', bg='gray', font=(font, 10),
                              command=lambda id=id: preparar_edicion(id), bd=2, relief='raised', width=20)
        boton_editar.grid(row=i + 1, column=4, sticky='ew')

        boton_borrar = Button(listado_frame, text='Borrar', bg='gray', font=(font, 10),
                              command=lambda id=id: borrar_producto(id), bd=2, relief='raised', width=20)
        boton_borrar.grid(row=i + 1, column=5, sticky='ew')


mostrar_productos()

root.mainloop()
