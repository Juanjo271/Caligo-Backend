import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "caliguia.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

POIS_DATA = [
    {
        "id": 1,
        "nombre": "Iglesia La Ermita",
        "categoria": "Arquitectura / Religioso",
        "tags": '["Historia", "Religioso", "Arquitectura"]',
        "lat": 3.4548,
        "lon": -76.5328,
        "radio_metros": 50,
        "descripcion": "Estilo gótico inspirado en la Catedral de Colonia. Ícono visual de Cali desde 1940.",
        "historia": "¡Oís! Esta es la Iglesia La Ermita, la más bonita de Cali. Fue construida entre 1935 y 1940, inspirada en la Catedral de Colonia, Alemania. Los caleños la quieren mucho porque es el corazón religioso del centro. Dicen que si vos pedís algo aquí, la ciudad te lo devuelve. Vení, acercate más, ¡esta es una parada obligatoria!",
        "imagen_referencia": "ermita.jpg",
        "audio_narracion": "ermita.mp3",
        "es_legendario": 1,
    },
    {
        "id": 2,
        "nombre": "El Gato del Río",
        "categoria": "Cultura / Arte",
        "tags": '["Cultura", "Arte", "Símbolo"]',
        "lat": 3.4504,
        "lon": -76.5411,
        "radio_metros": 40,
        "descripcion": "Escultura gigante del artista Hernando Tejada. El felino más famoso de Colombia.",
        "historia": "¡Eso sí es el Gato del Río, el más famoso de todo Cali! Fue hecho por Hernando Tejada y tiene unas gatas pequeñas alrededor que son sus hijos. Dicen que si te hacés una foto con él, te trae buena suerte. Es el símbolo de la ciudad, parce. Aquí ao lado del río Cali, este gato manda saludos a todo el mundo.",
        "imagen_referencia": "gato_del_rio.jpg",
        "audio_narracion": "gato_del_rio.mp3",
        "es_legendario": 1,
    },
    {
        "id": 3,
        "nombre": "Cristo Rey",
        "categoria": "Monumento / Mirador",
        "tags": '["Naturaleza", "Mirador", "Espiritual"]',
        "lat": 3.4364,
        "lon": -76.5658,
        "radio_metros": 60,
        "descripcion": "Estatua de 26 metros en el Cerro de los Cristales. La vista más privilegiada de Cali.",
        "historia": "¡Oís parce! Ese es Cristo Rey, una bestia de 26 metros de alto. Está arriba del Cerro de los Cristales y desde allá podés ver toda Cali, incluso los Farallones cuando están claros. Lo construyeron en 1953 y es como el guardián de la ciudad. Si subís hasta arriba, date por vencido porque el aliento te vai a faltar, pero la vista vale金子 cada paso.",
        "imagen_referencia": "cristo_rey.jpg",
        "audio_narracion": "cristo_rey.mp3",
        "es_legendario": 1,
    },
    {
        "id": 4,
        "nombre": "Barrio San Antonio",
        "categoria": "Histórico / Bohemio",
        "tags": '["Salsa", "Gastronomía", "Cultura"]',
        "lat": 3.4475,
        "lon": -76.5414,
        "radio_metros": 70,
        "descripcion": "Calles empedradas, arquitectura colonial y el mejor ambiente de Cali.",
        "historia": "¡Aquí estamos en San Antonio, el barrio más chévere de Cali! Es histórico, tiene las calles empedradas y una energía que no se puede explicar, hay que vivirla. Por aquí fica la mejor gastronomía caleña, hay muchos restaurants ricos y la noche es increíble. Si te gusta bailar, este es tu райсон. Vení, caminemos juntos por estas callecitas.",
        "imagen_referencia": "san_antonio.jpg",
        "audio_narracion": "san_antonio.mp3",
        "es_legendario": 0,
    },
    {
        "id": 5,
        "nombre": "Bulevar del Río",
        "categoria": "Urbano / Espacio Público",
        "tags": '["Urbano", "Río", "Eventos"]',
        "lat": 3.4533,
        "lon": -76.5325,
        "radio_metros": 50,
        "descripcion": "Paseo peatonal junto al río Cali. Lugar de eventos, paseos y vida nocturna.",
        "historia": "¡Este es el Bulevar del Río! Uno de los lugares másLindos de Cali, fica al lado del río Cali y siempre hay gente. En las noches se pone hermoso con las luces. Hay artistas callejeros, vendedores de comida, parejas bailando... es que este río tiene Alma, parce. Si tenés que elegir un solo lugar para caminar, que sea este.",
        "imagen_referencia": "bulevar_del_rio.jpg",
        "audio_narracion": "bulevar_del_rio.mp3",
        "es_legendario": 0,
    },
    {
        "id": 6,
        "nombre": "Plazoleta Jairo Varela",
        "categoria": "Salsa / Cultura",
        "tags": '["Salsa", "Música", "Cultura"]',
        "lat": 3.4545,
        "lon": -76.5342,
        "radio_metros": 40,
        "descripcion": "Museo interactivo de la salsa y el monumento 'Cali Pachanguero'.",
        "historia": "¡Estás en la Plazoleta Jairo Varela! Este es el templo de la salsa en Cali. Jairo Varela fue el fundador del Grupo Niche, una leyenda de la música colombiana. Aquí hay un monumento increíble que se llama 'Cali Pachanguero', con unas trompetas enormes. Si te gusta bailar salsa, este es tu lugar en el mundo. ¡Aquí la música nunca para!",
        "imagen_referencia": "plazoleta_jairo_varela.jpg",
        "audio_narracion": "plazoleta_jairo_varela.mp3",
        "es_legendario": 1,
    },
    {
        "id": 7,
        "nombre": "Sebastián de Belalcázar",
        "categoria": "Monumento / Mirador",
        "tags": '["Historia", "Mirador", "Fundación"]',
        "lat": 3.4509,
        "lon": -76.5458,
        "radio_metros": 45,
        "descripcion": "Estatua del fundador de Cali señalando hacia el mar. Punto histórico clave.",
        "historia": "Ese es Sebastián de Belalcázar, el tipo que fundó a Cali en 1536. Es un conquistador español que llegó buscando El Dorado y enместо de oro encontró esta tierra hermosa. La estatua lo muestra señalando hacia el mar, como cuando llegó. Es un poco la historia de cómo todo empezó aquí. Si te metés por la historia, este statue tiene mucho que contarte.",
        "imagen_referencia": "sebastian_belalcazar.jpg",
        "audio_narracion": "sebastian_belalcazar.mp3",
        "es_legendario": 0,
    },
    {
        "id": 8,
        "nombre": "Zoológico de Cali",
        "categoria": "Naturaleza / Familia",
        "tags": '["Naturaleza", "Familia", "Biodiversidad"]',
        "lat": 3.4486,
        "lon": -76.5517,
        "radio_metros": 80,
        "descripcion": "Considerado uno de los mejores zoológicos de Latinoamérica. Enfoque en biodiversidad.",
        "historia": "¡Bienvenido al Zoo de Cali, uno de los mejores de todo Latinoamérica! Acá tienen más de 3.000 animales de 900 especies diferentes. Lo más chévere es que están en ambientes que simulan su hábitat natural. Hay halcones, tigres, leones, monos... Si venís con niños, no hay forma de que no se delighten. Es una pasada en biodiversidad, parce.",
        "imagen_referencia": "zoologico.jpg",
        "audio_narracion": "zoologico.mp3",
        "es_legendario": 0,
    },
    {
        "id": 9,
        "nombre": "Río Pance",
        "categoria": "Ecoturismo",
        "tags": '["Naturaleza", "Río", "Ecoturismo"]',
        "lat": 3.3325,
        "lon": -76.6322,
        "radio_metros": 60,
        "descripcion": "Destino tradicional de 'baño de río' en las faldas de los Farallones.",
        "historia": "¡Ah, el Río Pance! Este es el lugar donde los caleños van a escapar del calor. Queda al pie de los Farallones de Cali, que son estas montañas enormes que protegen a la ciudad. El agua es fría, rica, cristalina. Los fines de semana se llena de familias, hay vendedores de raspados, arepas... Es la Nat到你 del caleño. Venite a chapuzarte, parce, que aquí el único estrés es tener que irte.",
        "imagen_referencia": "rio_pance.jpg",
        "audio_narracion": "rio_pance.mp3",
        "es_legendario": 0,
    },
    {
        "id": 10,
        "nombre": "Plaza de Cayzedo",
        "categoria": "Histórico / Centro",
        "tags": '["Historia", "Centro", "Patrimonio"]',
        "lat": 3.4519,
        "lon": -76.5325,
        "radio_metros": 45,
        "descripcion": "Corazón histórico de Cali, rodeado por el Palacio Nacional y la Catedral.",
        "historia": "¡Esta es la Plaza de Cayzedo, el corazón histórico de Cali! Aquí está la Catedral de San Pedro, el Palacio Nacional, y un poco de toda la historia de la ciudad. Cayzedo es porque el Precidente Cayzedo murió aquí defendiendo la democracia en 1840. Hoy es un lugar de encuentro, de política, de manifestación... pero también de areperas y de história. Si querés entender a Cali, empezás por aquí.",
        "imagen_referencia": "plaza_cayzedo.jpg",
        "audio_narracion": "plaza_cayzedo.mp3",
        "es_legendario": 0,
    },
]


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pois (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            categoria TEXT,
            tags TEXT,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            radio_metros INTEGER DEFAULT 50,
            descripcion TEXT,
            historia TEXT,
            imagen_referencia TEXT,
            audio_narracion TEXT,
            es_legendario INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orb_descriptors (
            poi_id INTEGER PRIMARY KEY,
            descriptor BLOB,
            image_path TEXT,
            FOREIGN KEY (poi_id) REFERENCES pois(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poi_id INTEGER,
            timestamp INTEGER,
            attempts INTEGER DEFAULT 0,
            bypassed INTEGER DEFAULT 0,
            FOREIGN KEY (poi_id) REFERENCES pois(id)
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM pois")
    if cursor.fetchone()[0] == 0:
        for poi in POIS_DATA:
            cursor.execute("""
                INSERT INTO pois (id, nombre, categoria, tags, lat, lon, radio_metros,
                                  descripcion, historia, imagen_referencia, audio_narracion, es_legendario)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                poi["id"], poi["nombre"], poi["categoria"], poi["tags"],
                poi["lat"], poi["lon"], poi["radio_metros"],
                poi["descripcion"], poi["historia"],
                poi["imagen_referencia"], poi["audio_narracion"], poi["es_legendario"]
            ))
        print(f"Se insertaron {len(POIS_DATA)} POIs en la base de datos.")

    conn.commit()
    conn.close()
    print(f"Base de datos inicializada en: {DB_PATH}")


if __name__ == "__main__":
    init_db()