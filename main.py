import random
import time
import json
import os








#FUNCION SALUDAR AL CLIENTE
def saludar():

    saludo = [
        "*************Bienvendio a CMA-JM**************",
        "*                                            *",
        "******PROGRAMA DE INVENTARIO DE VENTA*********",
        "*                                            *",
        "**********************************************"
    ]

    for linea in saludo:
        print(linea)
        time.sleep(random.uniform(0, 0.5))  # Pausa entre cada línea

saludar()




#CREANDO EL INVENTARIO Y PRECIOS
inventarios = []
precios = []
carrito = []
cantidades = []
ventas_del_dia = int(0)



NOMBRE_ARCHIVO = "inventario.json"


#FUNCION PARA CARGAR DATOS

# CARGAR DATOS
def cargar_datos():
    global inventarios, precios, cantidades, ventas_del_dia # <--- Agregamos cantidades
    if os.path.exists(NOMBRE_ARCHIVO):
        with open(NOMBRE_ARCHIVO, "r") as archivo:
            datos = json.load(archivo)
            inventarios = datos.get("nombres", [])
            precios = datos.get("precios", [])
            cantidades = datos.get("cantidades", []) # <--- Cargamos cantidades
            ventas_del_dia = datos.get("ventas_del_dia", 0)
            print("✅ Datos cargados del cuaderno.")
    else:
        print("💡 No hay cuaderno previo, empezando desde cero.")
cargar_datos()


# GUARDAR DATOS
def guardar_datos():
    datos_a_guardar = {
        "nombres": inventarios,
        "precios": precios,
        "cantidades": cantidades,
        "ventas_del_dia": ventas_del_dia
    }
    with open(NOMBRE_ARCHIVO, "w") as archivo:
        json.dump(datos_a_guardar, archivo, indent=4)
    print("💾 Inventario guardado físicamente en el disco.")







# FUNCION MOSTRAR EL INVENTARIO
def inventario():
    print("\n--- INVENTARIO CMA-JM ---")
    # Usamos zip con las TRES listas
    for i, (producto, precio, cant) in enumerate(zip(inventarios, precios, cantidades), start=1):
        if producto is not None:
            print(f"{i}. {producto.title()} - ${precio} | Stock: {cant}")
    print("--------------------------\n")



print(f"Tus ventas total son: {ventas_del_dia}")


#DECISIONES DEL MENU
def decisiones():
    print("\n--- MENÚ DE OPCIONES ---")

    print("1- Ver inventario")
    print("2- Agregar inventario")
    print("3- Vender Articulo")
    print("4- Salir de la tienda\n")

#LLAMAMOS A LA FUNCION PARA QUE APAREZCAN LAS DECISIONES A TOMAR
decisiones()








#BUCLE WHILE PARA LAS DECISIONES
while True:
    # INPUT DEL CLIENTE
    seleccion_menu = input("Selecciona la opcion que quieres: ")


    if seleccion_menu == "1":
        print("Ver inventario:\n")
        #LLAMAMOS A LA FUNCION INVENTARIO PARA QUE MUESTRE EL INVENTARIO
        inventario()

        print("\n")

        #LLAMAMOS A LA FUNCION DECISIOENS
        decisiones()








    elif seleccion_menu == "2":

        # 1. Pedimos el nombre y lo limpiamos

        nombre_nuevo = input("Ingresa Tu Nuevo Articulo: ").lower().strip()

        # 2. Verificamos si el producto YA EXISTE

        if nombre_nuevo in inventarios:

            # Si existe, buscamos su posición (índice)

            indice = inventarios.index(nombre_nuevo)

            print(f"El producto '{nombre_nuevo}' ya existe en el inventario.")

            while True:
                try:
                    cuantos_llegan = int(input(f"¿Cuántas unidades nuevas llegaron?: "))

                    # SUMAMOS a la cantidad que ya existía en esa posición

                    cantidades[indice] += cuantos_llegan

                    print(f"✅ Stock actualizado. Ahora hay {cantidades[indice]} unidades.")

                    break # SALIMOS  DEL BUCLE WHILE

                except ValueError:
                    print("Error Cantidad No Valida.")


        else:

            # 3. Si ES NUEVO, pedimos todos los datos por primera vez

            print(f"✨ '{nombre_nuevo}' es un producto nuevo para el negocio.")

            while True:
                try:
                    precio_nuevo = float(input("Ingresa El Precio Del Articulo: "))
                    break  # Si llega aquí es porque el número es válido, salimos del bucle
                except ValueError:
                    print("❌ Eso no es un número válido, intenta de nuevo")




            while True:
                try:
                    cantidad_inicial = int(input("¿Con cuántas unidades inicias el stock?: "))

                    # Agregamos a las tres listas al mismo tiempo para mantener el orden

                    inventarios.append(nombre_nuevo)

                    precios.append(precio_nuevo)

                    cantidades.append(cantidad_inicial)

                    print(f"✅ {nombre_nuevo} agregado exitosamente.")

                    break # SALIMOS DEL BUCLE WHILE

                # 4. Guardamos en el JSON para que el cambio sea físico

                except ValueError:
                    print("Lo que agregaste no es valido")


        guardar_datos()




        print("Articulo Agregado Exitosamente")
        print(f"Inventario:\n")
        #LLAMAMOS LA FUNCION INVENTARIO PARA QUE APAREZCA LUEGO DE AGREGAR EL ARTICULO
        inventario()

        #PREGUNTAMOS SI QUEREMOS AGREGAR OTRO ARTICULO O VER MAS OPCIONES
        print("1- Quieres Agregar Otro Producto.")
        print("2- Ver Mas Opciones.")


        mas_productos_o_mas_opciones = input("Que Quieres Hacer?: ")


        while mas_productos_o_mas_opciones == "1":

            if mas_productos_o_mas_opciones == "1":
                print("Agregar inventario:\n")
                inventarios.append(input("Ingresa Tu Nuevo Articulo: "))

                print("Ingresa El Precio De EL Articulo:")
                precios.append(int(input("Precio: ")))
                print("Articulo Agregado Exitosamente")
                guardar_datos() # GUARDAMOS LOS DATOS NUEVOS

                print("Inventario:\n")
                inventario()

                print("1- Quieres Agregar Otro Producto.")
                print("2- Ver Mas Opciones.")


                mas_productos_o_mas_opciones = input("Que Quieres Hacer?: ")

            elif mas_productos_o_mas_opciones == "2":
                print("Mas Opciones:\n")
                decisiones()

        else:
            decisiones()














    elif seleccion_menu == "3":

        print("Vender Articulos: \n")

        inventario()

        vender = input("Que Articulo Quieres Vender?: ").lower().strip()

        encontrado = False

        for elemento in range(len(inventarios)):

            # SEGURIDAD: Primero verificamos que el producto no sea None

            if inventarios[elemento] is not None:

                # Ahora sí podemos usar .lower() con confianza

                if inventarios[elemento].lower() == vender:

                    encontrado = True

                    if cantidades[elemento] > 0:

                        cantidades[elemento] -= 1

                        precio_vendido = precios[elemento]

                        print(f"💰 Venta confirmada: {inventarios[elemento]} por ${precio_vendido}")

                        ventas_del_dia += int(precio_vendido)

                        guardar_datos()



                    else:

                        print(f"🚫 No hay stock de '{vender}'.")

                    break

        if not encontrado:
            print(f"❌ El producto '{vender}' no existe.")












    #SI ELIGE LA OPCION 4 SALE DEL PROGRAMA Y NO SE EJECUTA MAS
    elif seleccion_menu == "4":
        print("Gracias Por Usar Este Programa")
        guardar_datos()  # <--- ¡IMPORTANTE! Escribir antes de irse
        break


    # LOGICA PARA LA SELECCION DE MENU POR SI ELIGE ALGO QUE NO ES VALIDO
    else:
        print("Opcion Invalida!")



print(ventas_del_dia)























