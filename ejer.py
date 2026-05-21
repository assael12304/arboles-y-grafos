mkdir -p campus_rutas && cd campus_rutas

cat > modelo_grafo.py << 'EOF'
# Construccion del grafo que representa el campus
# Nodos = edificios y espacios, aristas = senderos con distancia en metros

import networkx as nx

def crear_grafo_campus():
    mapa = nx.Graph()

    # lugares del campus como nodos
    sitios = [
        "Porteria",
        "Rectoria",
        "Facultad Ingenieria",
        "Facultad Ciencias",
        "Sala Computo",
        "Comedor",
        "Enfermeria",
        "Gimnasio",
        "Teatro",
        "Zona Verde",
    ]
    mapa.add_nodes_from(sitios)

    # senderos entre sitios con distancia en metros como peso
    senderos = [
        ("Porteria",           "Rectoria",           100),
        ("Porteria",           "Comedor",              75),
        ("Porteria",           "Zona Verde",           50),
        ("Rectoria",           "Facultad Ingenieria",  60),
        ("Rectoria",           "Facultad Ciencias",    65),
        ("Rectoria",           "Teatro",              140),
        ("Facultad Ingenieria","Sala Computo",          45),
        ("Facultad Ingenieria","Comedor",               80),
        ("Facultad Ciencias",  "Sala Computo",          55),
        ("Facultad Ciencias",  "Enfermeria",            90),
        ("Comedor",            "Enfermeria",            70),
        ("Comedor",            "Zona Verde",            60),
        ("Sala Computo",       "Gimnasio",             110),
        ("Enfermeria",         "Gimnasio",              85),
        ("Gimnasio",           "Teatro",                95),
        ("Zona Verde",         "Teatro",               120),
    ]
    mapa.add_weighted_edges_from(senderos)

    return mapa
EOF

cat > calcular_ruta.py << 'EOF'
# Funciones para calcular y mostrar rutas dentro del campus
# Dijkstra encuentra el camino de menor distancia total

import networkx as nx
from modelo_grafo import crear_grafo_campus

def camino_minimo(mapa, inicio, fin):
    try:
        recorrido = nx.dijkstra_path(mapa, inicio, fin, weight='weight')
        distancia = nx.dijkstra_path_length(mapa, inicio, fin, weight='weight')
        return recorrido, distancia
    except nx.NetworkXNoPath:
        return None, None
    except nx.NodeNotFound as err:
        print(f"Sitio no encontrado en el campus: {err}")
        return None, None

def mostrar_sitios(mapa):
    print("\nSitios del campus:")
    for idx, sitio in enumerate(sorted(mapa.nodes()), 1):
        conexiones = mapa.degree(sitio)
        print(f"  {idx:2}. {sitio:<30} (conexiones: {conexiones})")

def imprimir_recorrido(recorrido, distancia):
    if recorrido is None:
        print("\nNo hay ruta disponible entre esos sitios.")
        return
    pasos = " => ".join(recorrido)
    print(f"\nCamino encontrado:")
    print(f"  {pasos}")
    print(f"  Distancia total: {distancia} metros")
    print(f"  Paradas en el camino: {len(recorrido) - 2} intermedias")

if __name__ == "__main__":
    mapa = crear_grafo_campus()
    mostrar_sitios(mapa)

    consultas = [
        ("Porteria", "Sala Computo"),
        ("Zona Verde", "Teatro"),
        ("Comedor", "Gimnasio"),
    ]

    for inicio, fin in consultas:
        print(f"\nConsulta: '{inicio}' -> '{fin}'")
        recorrido, distancia = camino_minimo(mapa, inicio, fin)
        imprimir_recorrido(recorrido, distancia)
EOF

cat > mapa_visual.py << 'EOF'
# Visualizacion del campus como grafo con matplotlib
# Los nodos de la ruta seleccionada se resaltan en color diferente

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from modelo_grafo import crear_grafo_campus
from calcular_ruta import camino_minimo

def graficar_mapa(mapa, ruta=None, titulo="Mapa del Campus"):
    # coordenadas de cada sitio en el lienzo
    coords = {
        "Porteria":            (0,    0),
        "Rectoria":            (0,    3),
        "Facultad Ingenieria": (-3,   5),
        "Facultad Ciencias":   (3,    5),
        "Sala Computo":        (-2,   7),
        "Comedor":             (-1,   2),
        "Enfermeria":          (4,    3),
        "Gimnasio":            (2,    8),
        "Teatro":              (-1,   9),
        "Zona Verde":          (2,    1),
    }

    fig, ax = plt.subplots(figsize=(13, 10))
    ax.set_title(titulo, fontsize=15, fontweight='bold', pad=20)

    # separar aristas normales de las que pertenecen a la ruta
    aristas_camino  = []
    aristas_resto   = []

    if ruta and len(ruta) > 1:
        pares_ruta = set()
        for i in range(len(ruta) - 1):
            pares_ruta.add((ruta[i], ruta[i+1]))
            pares_ruta.add((ruta[i+1], ruta[i]))
        for u, v in mapa.edges():
            if (u, v) in pares_ruta:
                aristas_camino.append((u, v))
            else:
                aristas_resto.append((u, v))
    else:
        aristas_resto = list(mapa.edges())

    # dibujar caminos normales
    nx.draw_networkx_edges(
        mapa, coords,
        edgelist=aristas_resto,
        edge_color="#B0BEC5",
        width=1.8,
        ax=ax
    )

    # dibujar camino resaltado
    if aristas_camino:
        nx.draw_networkx_edges(
            mapa, coords,
            edgelist=aristas_camino,
            edge_color="#27AE60",
            width=5,
            ax=ax
        )

    # color de nodos segun si pertenecen a la ruta
    colores_nodos = []
    for nodo in mapa.nodes():
        if ruta and nodo == ruta[0]:
            colores_nodos.append("#E74C3C")   # inicio: rojo
        elif ruta and nodo == ruta[-1]:
            colores_nodos.append("#8E44AD")   # fin: morado
        elif ruta and nodo in ruta:
            colores_nodos.append("#27AE60")   # intermedio: verde
        else:
            colores_nodos.append("#2980B9")   # normal: azul

    nx.draw_networkx_nodes(
        mapa, coords,
        node_color=colores_nodos,
        node_size=900,
        ax=ax
    )

    nx.draw_networkx_labels(
        mapa, coords,
        font_size=7,
        font_color="white",
        font_weight="bold",
        ax=ax
    )

    pesos = nx.get_edge_attributes(mapa, 'weight')
    nx.draw_networkx_edge_labels(
        mapa, coords,
        edge_labels={k: f"{v}m" for k, v in pesos.items()},
        font_size=7,
        ax=ax
    )

    # leyenda
    leyenda = [
        mpatches.Patch(color="#E74C3C", label="Inicio"),
        mpatches.Patch(color="#8E44AD", label="Destino"),
        mpatches.Patch(color="#27AE60", label="Ruta optima"),
        mpatches.Patch(color="#2980B9", label="Otros sitios"),
    ]
    ax.legend(handles=leyenda, loc="lower right", fontsize=9)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig("mapa_campus.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Imagen guardada como mapa_campus.png")


if __name__ == "__main__":
    mapa   = crear_grafo_campus()
    inicio = "Porteria"
    fin    = "Gimnasio"
    ruta, dist = camino_minimo(mapa, inicio, fin)
    if ruta:
        print(f"Ruta: {' => '.join(ruta)} ({dist}m)")
    graficar_mapa(mapa, ruta=ruta, titulo=f"Ruta: {inicio} -> {fin}")
EOF

cat > principal.py << 'EOF'
# Punto de entrada del programa
# Menu interactivo para consultar rutas en el campus

from modelo_grafo import crear_grafo_campus
from calcular_ruta import camino_minimo, mostrar_sitios, imprimir_recorrido
from mapa_visual import graficar_mapa

def ejecutar():
    mapa = crear_grafo_campus()

    print("=" * 55)
    print("   SISTEMA DE RUTAS — CAMPUS UNIVERSITARIO")
    print("=" * 55)

    while True:
        print("\n  1. Listar sitios del campus")
        print("  2. Calcular ruta entre dos sitios")
        print("  3. Ver mapa completo del campus")
        print("  4. Ver mapa con ruta resaltada")
        print("  5. Salir")

        eleccion = input("\nOpcion: ").strip()

        if eleccion == "1":
            mostrar_sitios(mapa)

        elif eleccion == "2":
            mostrar_sitios(mapa)
            inicio = input("\nSitio de inicio  : ").strip()
            fin    = input("Sitio de destino : ").strip()
            ruta, dist = camino_minimo(mapa, inicio, fin)
            imprimir_recorrido(ruta, dist)

        elif eleccion == "3":
            print("Abriendo mapa completo...")
            graficar_mapa(mapa, titulo="Mapa completo del campus")

        elif eleccion == "4":
            mostrar_sitios(mapa)
            inicio = input("\nSitio de inicio  : ").strip()
            fin    = input("Sitio de destino : ").strip()
            ruta, dist = camino_minimo(mapa, inicio, fin)
            imprimir_recorrido(ruta, dist)
            if ruta:
                graficar_mapa(
                    mapa,
                    ruta=ruta,
                    titulo=f"Ruta optima: {inicio} -> {fin} ({dist}m)"
                )

        elif eleccion == "5":
            print("\nCerrando el sistema. Hasta luego.")
            break

        else:
            print("Opcion no reconocida. Intenta de nuevo.")

if __name__ == "__main__":
    ejecutar()
EOF

cat > requirements.txt << 'EOF'
networkx
matplotlib
EOF

cat > README.md << 'EOF'
# Sistema de Rutas - Campus Universitario

Aplicativo educativo que modela el campus como un grafo
ponderado no dirigido y calcula rutas optimas entre sitios.

## Archivos

- modelo_grafo.py   -> construye el grafo del campus
- calcular_ruta.py  -> algoritmo Dijkstra para rutas minimas
- mapa_visual.py    -> visualizacion con colores y leyenda
- principal.py      -> menu interactivo principal

## Instalacion

pip install -r requirements.txt

## Ejecucion

python principal.py

## Tecnologias

- Python 3
- NetworkX (estructura de grafo y Dijkstra)
- Matplotlib (visualizacion del mapa)

## Conceptos del proyecto

- Grafo no dirigido ponderado
- Nodos: sitios del campus
- Aristas: senderos con distancia en metros
- Algoritmo de Dijkstra: ruta de menor distancia
EOF

pip install networkx matplotlib --break-system-packages --quiet

echo ""
echo "Archivos generados:"
ls -lh