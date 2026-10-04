from modelo_procesamiento import (
    ProcesadorCSV,
    ProcesadorMAT,
    GestorObjetos,
    validar_entero,
    validar_flotante,
    validar_opcion
)

def menu_principal():
    gestor = GestorObjetos()
    
    while True:
        print("\n" + "="*50)
        print(" SISTEMA DE MONITOREO Y ANÁLISIS DE ERP ")
        print("="*50)
        print("1. Cargar y Procesar Archivo CSV")
        print("2. Cargar y Procesar Archivo MAT")
        print("3. Buscar y Listar Objetos Almacenados (Punto Extra)")
        print("4. Salir")
        
        opc = validar_opcion("Seleccione una opción (1-4): ", ['1', '2', '3', '4'])
        
        if opc == '1':
            ruta = input("\nIngrese el nombre/ruta del archivo CSV (ej. ERP_01.csv): ").strip()
            try:
                obj_csv = ProcesadorCSV(ruta)
                id_obj = input("Asigne un identificador único para este registro: ").strip()
                gestor.guardar_objeto(id_obj, obj_csv)
                
                # Submenú CSV
                while True:
                    print("\n--- MENÚ PROCESAMIENTO CSV ---")
                    print("1. Mostrar información del archivo (__str__)")
                    print("2. Generar Subplots (Stem, Histograma, Scatter)")
                    print("3. Calcular Diferencia Interhemisférica")
                    print("4. Volver al Menú Principal")
                    
                    sub_opc = validar_opcion("Seleccione una opción: ", ['1', '2', '3', '4'])
                    
                    if sub_opc == '1':
                        print("\n" + str(obj_csv))
                    elif sub_opc == '2':
                        print("\nColumnas disponibles en el archivo:", list(obj_csv.df.columns))
                        cond = input("Ingrese el valor exacto de la condición a filtrar: ").strip()
                        c_stem = input("Nombre de la columna para Stem e Histograma: ").strip()
                        c_scat1 = input("Nombre de la columna 1 para Scatter: ").strip()
                        c_scat2 = input("Nombre de la columna 2 para Scatter: ").strip()
                        obj_csv.graficar_condiciones(cond, c_stem, c_scat1, c_scat2)
                    elif sub_opc == '3':
                        print("\nColumnas disponibles:", list(obj_csv.df.columns))
                        c1 = input("Nombre del canal 1 (ej. Izquierdo): ").strip()
                        c2 = input("Nombre del canal 2 (ej. Derecho): ").strip()
                        print("\n" + str(obj_csv.calcular_diferencia_interhemisferica(c1, c2)))
                    elif sub_opc == '4':
                        break

            except Exception as e:
                print(f"\nError al procesar el archivo CSV: {e}")

        elif opc == '2':
            ruta = input("\nIngrese el nombre/ruta del archivo MAT (ej. Visual_Cue.mat): ").strip()
            if not ruta.endswith('.mat'):
                ruta += '.mat'
                
            try:
                obj_mat = ProcesadorMAT(ruta)
                id_obj = input("Asigne un identificador único para este registro: ").strip()
                gestor.guardar_objeto(id_obj, obj_mat)
                
                # Submenú MAT
                while True:
                    print("\n--- MENÚ PROCESAMIENTO MAT ---")
                    print("1. Mostrar estructura del archivo (__str__)")
                    print("2. Operaciones entre 4 Canales y Graficar")
                    print("3. Análisis Estadístico 3D (Boxplots)")
                    print("4. Volver al Menú Principal")
                    
                    sub_opc = validar_opcion("Seleccione una opción: ", ['1', '2', '3', '4'])
                    
                    if sub_opc == '1':
                        print("\n" + str(obj_mat))
                    elif sub_opc == '2':
                        var = input("\nNombre de la variable MAT a procesar: ").strip()
                        print("Ingrese 4 índices de canales (números enteros):")
                        ch = [validar_entero(f"Canal {i+1}: ", 0) for i in range(4)]
                        op = validar_opcion("Operación deseada (suma/resta/multiplicacion): ", ['suma', 'resta', 'multiplicacion'])
                        t1 = validar_flotante("Tiempo inicio en segundos (ej. 0.0): ")
                        t2 = validar_flotante("Tiempo fin en segundos (ej. 1.0): ")
                        obj_mat.operacion_y_grafica(var, ch, op, t1, t2)
                    elif sub_opc == '3':
                        var = input("\nNombre de la variable 3D a analizar: ").strip()
                        print("Seleccione los 2 ejes para calcular el promedio y desviación estándar (ej. 0 y 2):")
                        e1 = validar_entero("Eje 1 (0, 1 o 2): ", 0, 2)
                        e2 = validar_entero("Eje 2 (0, 1 o 2): ", 0, 2)
                        obj_mat.analisis_estadistico_3d(var, (e1, e2))
                    elif sub_opc == '4':
                        break

            except Exception as e:
                print(f"\nError al procesar el archivo MAT: {e}")

        elif opc == '3':
            gestor.listar_objetos()
            if gestor.almacen:
                nombre_b = input("\nIngrese el ID del objeto que desea consultar: ").strip()
                res = gestor.buscar_objeto(nombre_b)
                if res:
                    print(f"\nObjeto encontrado: Tipo {type(res).__name__}")
                else:
                    print("\nNo se encontró ningún objeto registrado con ese ID.")

        elif opc == '4':
            print("\nSaliendo del programa...")
            break

if __name__ == '__main__':
    menu_principal()