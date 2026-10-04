import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
import os
import io


def validar_entero(mensaje, minimo=None, maximo=None):
    """Valida la entrada de un número entero en un rango determinado."""
    while True:
        try:
            val = int(input(mensaje))
            if minimo is not None and val < minimo:
                print(f"Error: El valor debe ser >= {minimo}")
                continue
            if maximo is not None and val > maximo:
                print(f"Error: El valor debe ser <= {maximo}")
                continue
            return val
        except ValueError:
            print("Entrada inválida. Ingrese un número entero válido.")

def validar_flotante(mensaje):
    """Valida la entrada de un número flotante."""
    while True:
        try:
            return float(input(mensaje))
        except ValueError:
            print("Entrada inválida. Ingrese un número válido.")

def validar_opcion(mensaje, opciones_validas):
    """Valida que la opción seleccionada esté dentro de las opciones permitidas."""
    while True:
        val = input(mensaje).strip()
        if val in opciones_validas:
            return val
        print(f"Opción no válida. Opciones permitidas: {opciones_validas}")



class ProcesadorCSV:
    def __init__(self, ruta_archivo):
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"El archivo {ruta_archivo} no existe.")
        
        self.ruta = ruta_archivo
        self.df = pd.read_csv(ruta_archivo)
        
        # Asignar la columna de tiempo como índice
        if 'Tiempo' in self.df.columns:
            self.df.set_index('Tiempo', inplace=True)
        elif 'Time' in self.df.columns:
            self.df.set_index('Time', inplace=True)
            
    def __str__(self):
        info_str = "=== INFORMACIÓN DEL ARCHIVO CSV ===\n"
        info_str += f"Ruta: {self.ruta}\n\n"
        info_str += "--- INFORMACIÓN GENERAL (info) ---\n"
        
        buffer = io.StringIO()
        self.df.info(buf=buffer)
        info_str += buffer.getvalue() + "\n"
        
        info_str += "--- DESCRIPCIÓN ESTADÍSTICA (describe) ---\n"
        info_str += str(self.df.describe())
        return info_str

    def graficar_condiciones(self, condicion, canal_stem_hist, canal_scatter1, canal_scatter2, ruta_guardado="grafico_csv.png"):
        """Genera 3 subplots según la condición seleccionada y guarda la figura."""
        col_cond = 'Condicion' if 'Condicion' in self.df.columns else ('Condición' if 'Condición' in self.df.columns else None)
        if not col_cond:
            coincidencias = [c for c in self.df.columns if 'cond' in c.lower()]
            if coincidencias:
                col_cond = coincidencias[0]
            else:
                print("Error: No se encontró una columna de condición.")
                return

        df_cond = self.df[self.df[col_cond] == condicion]
        if df_cond.empty:
            print(f"No se encontraron datos para la condición: {condicion}")
            return

        fig = plt.figure(figsize=(12, 8))
        fig.suptitle(f"Análisis ERP - Condición: {condicion}", fontsize=14, fontweight='bold')


        ax1 = fig.add_subplot(2, 2, 1)
        ax1.stem(df_cond.index.values, df_cond[canal_stem_hist].values)
        ax1.axvline(x=0, color='r', linestyle='--', label='t = 0 ms')
        ax1.set_xlabel('Tiempo (ms)')
        ax1.set_ylabel('Amplitud (µV)')
        ax1.set_title(f'Stem Plot: {canal_stem_hist}')
        ax1.legend()
        ax1.grid(True)


        ax2 = fig.add_subplot(2, 2, 2)
        ax2.hist(df_cond[canal_stem_hist], bins=20, color='skyblue', edgecolor='black')
        ax2.set_xlabel('Amplitud (µV)')
        ax2.set_ylabel('Frecuencia')
        ax2.set_title(f'Histograma: {canal_stem_hist}')
        ax2.grid(True)


        ax3 = fig.add_subplot(2, 1, 2)
        ax3.scatter(df_cond[canal_scatter1], df_cond[canal_scatter2], alpha=0.6, color='purple')
        ax3.set_xlabel(f'{canal_scatter1} (µV)')
        ax3.set_ylabel(f'{canal_scatter2} (µV)')
        ax3.set_title(f'Scatter Plot: {canal_scatter1} vs {canal_scatter2}')
        ax3.grid(True)

        plt.tight_layout()
        plt.savefig(ruta_guardado, dpi=300)
        print(f"Gráfico guardado en: {ruta_guardado}")
        plt.show()

    def calcular_diferencia_interhemisferica(self, canal1, canal2, nombre_nueva_col=None):
        """Calcula la resta entre dos canales y guarda el resultado en una nueva columna."""
        if nombre_nueva_col is None:
            nombre_nueva_col = f"Diff_{canal1}_{canal2}"
        self.df[nombre_nueva_col] = self.df[canal1] - self.df[canal2]
        print(f"Columna '{nombre_nueva_col}' creada correctamente.")
        return self.df[[canal1, canal2, nombre_nueva_col]].head()



class ProcesadorMAT:
    def __init__(self, ruta_archivo, fs=250):
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"El archivo {ruta_archivo} no existe.")
        self.ruta = ruta_archivo
        self.fs = fs
        self.mat_data = sio.loadmat(ruta_archivo)

    def __str__(self):
        info_mat = sio.whosmat(self.ruta)
        res = "=== INFORMACIÓN ESTRUCTURADA DEL ARCHIVO .MAT ===\n"
        res += f"{'Variable':<20} | {'Dimensiones':<15} | {'Tipo de Dato':<10}\n"
        res += "-" * 52 + "\n"
        for var in info_mat:
            nombre, shape, dtype = var
            res += f"{nombre:<20} | {str(shape):<15} | {dtype:<10}\n"
        return res

    def operacion_y_grafica(self, nombre_var, canales_idx, funcion_op, t_min, t_max, ruta_guardado="operacion_mat.png"):
        """Aplica operaciones sobre 4 canales en un intervalo de tiempo y grafica."""
        matriz = self.mat_data[nombre_var]
        
        if matriz.ndim == 3:
            matriz_2d = np.mean(matriz, axis=2) if matriz.shape[2] < matriz.shape[0] else np.mean(matriz, axis=0)
        else:
            matriz_2d = matriz

        num_muestras = matriz_2d.shape[1]
        eje_t_completo = np.arange(num_muestras) / self.fs

        idx_min = max(0, int(t_min * self.fs))
        idx_max = min(num_muestras, int(t_max * self.fs))

        if idx_min >= idx_max:
            print("Intervalo de tiempo inválido.")
            return

        eje_tiempo = eje_t_completo[idx_min:idx_max]
        segmentos = [matriz_2d[ch, idx_min:idx_max] for ch in canales_idx]

        if funcion_op == 'suma':
            resultado = segmentos[0] + segmentos[1] + segmentos[2] + segmentos[3]
        elif funcion_op == 'resta':
            resultado = segmentos[0] - segmentos[1] - segmentos[2] - segmentos[3]
        elif funcion_op == 'multiplicacion':
            resultado = segmentos[0] * segmentos[1] * segmentos[2] * segmentos[3]
        else:
            print("Operación no válida.")
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        for idx, ch in enumerate(canales_idx):
            ax1.plot(eje_tiempo, segmentos[idx], label=f'Canal {ch}')
        ax1.set_xlabel('Tiempo (s)')
        ax1.set_ylabel('Amplitud (µV)')
        ax1.set_title('Canales Seleccionados')
        ax1.legend()
        ax1.grid(True)

        ax2.plot(eje_tiempo, resultado, color='black', label=f'Resultado ({funcion_op})')
        ax2.set_xlabel('Tiempo (s)')
        ax2.set_ylabel('Amplitud (µV)')
        ax2.set_title(f'Operación: {funcion_op}')
        ax2.legend()
        ax2.grid(True)

        plt.tight_layout()
        plt.savefig(ruta_guardado, format='png', dpi=300)
        print(f"Gráfico guardado en: {ruta_guardado}")
        plt.show()

    def analisis_estadistico_3d(self, nombre_var, ejes):
        """Calcula promedio y desviación estándar sobre una matriz 3D y genera boxplots."""
        matriz = self.mat_data[nombre_var]
        if matriz.ndim != 3:
            print("Error: La matriz seleccionada no es 3D.")
            return

        promedio = np.mean(matriz, axis=ejes)
        desviacion = np.std(matriz, axis=ejes)
        print(f"\nForma del vector resultante (Promedio): {promedio.shape}")
        print(f"Forma del vector resultante (Desviación): {desviacion.shape}")

        plt.figure(figsize=(8, 6))
        plt.boxplot([promedio.ravel(), desviacion.ravel()], labels=['Promedio (µV)', 'Desviación (µV)'])
        plt.title('Distribución Estadística de la Matriz 3D')
        plt.ylabel('Amplitud (µV)')
        plt.grid(True)
        plt.show()



class GestorObjetos:
    def __init__(self):
        self.almacen = {}

    def guardar_objeto(self, nombre, objeto):
        self.almacen[nombre] = objeto
        print(f"Objeto '{nombre}' guardado correctamente.")

    def buscar_objeto(self, nombre):
        return self.almacen.get(nombre, None)

    def listar_objetos(self):
        if not self.almacen:
            print("No hay objetos almacenados actualmente.")
        else:
            print("\n--- OBJETOS ALMACENADOS ---")
            for k, v in self.almacen.items():
                print(f"ID: {k} | Tipo: {type(v).__name__}")