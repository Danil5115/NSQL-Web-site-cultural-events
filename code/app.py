from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import redis
from neo4j import GraphDatabase
import json
from bson import json_util


app = Flask(__name__)

# Connecting to MongoDB // Подключение к MongoDB
client = MongoClient("mongodb://admin:admin@mongodb:27017/")
db = client["seminar_db"]
events_collection = db["events"]

# Connecting to Redis   Подключение к Redis
redis_client = redis.StrictRedis(host="redis", port=6379, decode_responses=True)

# Connecting to Neo4j  Подключение к Neo4j
neo4j_uri = "bolt://neo4j:7687"
neo4j_user = "neo4j"
neo4j_password = "password"


# Function to create "Event Type" nodes in Neo4j tx is a transaction   Функция для создания узлов "Тип мероприятия" в Neo4j tx-это транзакция
def create_event_types(tx):
    # Creation of the "Cultural Events" node   Создание узла "Культурные мероприятия"
    tx.run("CREATE (c:EventType {name: 'Cultural events'})")

    event_types = ["Theatrical performance", "Musical concert", "Festival", "Educational event", "Art exhibition"]
    for event_type in event_types:
        #  Create an Event Type node   Создание узла "Тип мероприятия"
        tx.run("CREATE (et:EventCategory {name: $name})", name=event_type)

        # Linking "Event Type" to "Cultural Events"   Связывание "Тип мероприятия" с "Культурные мероприятия"
        tx.run("MATCH (c:EventType {name: 'Cultural events'}), (et:EventCategory {name: $name}) "
               "CREATE (et)-[:IS_SUBTYPE]->(c)", name=event_type)


# Initialization of "Event Type" nodes at application startup   Инициализация узлов "Тип мероприятия" при запуске приложения
with GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password)) as driver:
    driver.session().write_transaction(create_event_types)

# Function for saving an event in Neo4j   Функция для сохранения мероприятия в Neo4j
def save_event_to_neo4j(event_id, event):
    with GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password)) as driver:
        with driver.session() as session:
            event_type = event.get('type', 'Other')

            session.run(
                "CREATE (e:Event {id: $id, name: $name, location: $location, date: $date, description: $description})",
                id=event_id,
                name=event['name'],
                location=event['location'],
                date=event['date'],
                description=event['description']
            )

            # Create a link between the "Event" and "Event Type" nodes  Создание связи между узлами "Мероприятие" и "Тип мероприятия"
            session.run(
                "MATCH (e:Event {id: $id}), (et:EventCategory {name: $type}) "
                "CREATE (e)-[:IS_TYPE]->(et)",
                id=event_id,
                type=event_type
            )

def initialize_mongodb():
    predefined_events = [
        {'name': "A Night of Enchantment: The Phantom's Masquerade",'location': 'Gothic Theatre, Broadway Street','date': '2023-12-15','description': "Step into a world of mystery and allure at 'A Night of Enchantment.' Immerse yourself in the grandeur of The Phantom's Masquerade, where the elegance of the 19th century collides with the mystique of a masked ball. Witness breathtaking performances, opulent costumes, and the unveiling of secrets in this theatrical masterpiece.", 'type': 'Theatrical performance'},
        {'name': "Shakespearean Revelry: Midsummer Night's Dream",'location': 'Fairywood Amphitheater, Riverside Park','date': '2023-12-28','description': "Escape to an enchanted forest as 'Shakespearean Revelry' presents 'A Midsummer Night's Dream.' Join the whimsical journey of love and mischief as the moonlight weaves its magic. This open-air theatrical performance promises an evening filled with laughter, romance, and the fantastical world of Shakespeare.",'type': 'Theatrical performance'},
        {'name': "Harmony Fusion",'location': "Melody Hall",'date': '2023-12-16','description': "Immerse yourself in an unforgettable night of musical brilliance at Harmony Fusion! This concert brings together virtuoso performers, captivating melodies, and an electrifying atmosphere. Join us for a magical experience that transcends genres and celebrates the power of music to unite hearts and souls. Don't miss the chance to be part of this extraordinary celebration of sound and rhythm.",'type': 'Musical concert'},
        {'name': "Rhythmic Resonance",'location': "Serenade Pavilion",'date': '2023-12-10','description': "Embark on a rhythmic journey at Rhythmic Resonance, where the beats echo and melodies soar. This musical extravaganza promises an evening of enchanting performances, from soulful ballads to upbeat rhythms. Set in the charming Serenade Pavilion, this concert invites you to experience the power of live music in a mesmerizing ambiance. Join us for an unforgettable night filled with harmonies that will linger in your heart long after the last note fades away.",'type': 'Musical concert'},
        {'name': "Festival of Lights",'location': "City Park Amphitheater",'date': '2023-12-19','description': "Experience the magical Festival of Lights, where the park transforms into a mesmerizing wonderland with vibrant colors, interactive art installations, and live performances. Join us for a night filled with joy, laughter, and the spirit of celebration.",'type': 'Festival'},
        {'name': "Nature Fest Extravaganza",'location': "Riverside Meadows",'date': '2024-05-20','description': "oin us for the Nature Fest Extravaganza, a one-of-a-kind outdoor celebration of the wonders of nature. This family-friendly festival offers a variety of activities, including guided nature walks, birdwatching sessions, eco-friendly craft workshops, and a star-gazing night. Discover the beauty of our planet and learn how to contribute to environmental conservation. A day of fun and education awaits!",'type': 'Festival'},
        {'name': 'Interactive Science Workshop','location': 'Science Center Auditorium','date': '2024-01-01','description': 'Join us for an engaging workshop where experts will explore fascinating scientific concepts through hands-on experiments and interactive discussions. This educational event is perfect for science enthusiasts of all ages.','type': 'Educational event'},
        {'name': 'Coding Bootcamp for Beginners','location': 'TechHub Co-Working Space','date': '2024-02-01','description': 'Embark on a coding journey with our comprehensive bootcamp designed for beginners. Learn the fundamentals of programming, web development, and get hands-on experience with real-world projects. No prior coding experience required!','type': 'Educational event'},
        {'name': 'Artistic Expression Showcase','location': 'Contemporary Art Gallery','date': '2023-12-28','description': 'Immerse yourself in the vibrant world of contemporary art at the Artistic Expression Showcase. This exhibition features a diverse collection of paintings, sculptures, and installations created by both emerging and established artists. Explore the intersection of culture, emotion, and creativity in this one-of-a-kind art experience.','type': 'Art exhibition'},
        {'name': 'Innovative Sculpture Symposium','location': 'Sculpture Park','date': '2023-12-29','description': 'Join us for an extraordinary day at the Innovative Sculpture Symposium. Witness renowned sculptors from around the world as they transform raw materials into captivating works of art. From abstract to figurative sculptures, this event celebrates the power of three-dimensional artistic expression.','type': 'Art exhibition'}
    ]
    for event_data in predefined_events:
        events_collection.insert_one(event_data)
        save_event_to_neo4j(str(event_data['_id']), event_data)
initialize_mongodb()


# Function to search for recommendations based on event type   Функция для поиска рекомендаций на основе типа мероприятия
def get_recommendations(event_type):
    with GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password)) as driver:
        with driver.session() as session:
            result = session.run(
                "MATCH (e:Event)-[:IS_TYPE]->(et:EventCategory {name: $type}) "
                "RETURN e.name as eventName, e.location as eventLocation, e.date as eventDate, e.description as eventDescription "
                "LIMIT 5",
                type=event_type
            )

            recommendations = [
                {
                    "name": record["eventName"],
                    "location": record["eventLocation"],
                    "date": record["eventDate"],
                    "description": record["eventDescription"],
                }
                for record in result
            ]

            return recommendations



# Home page   Главная страница
@app.route('/', methods=['GET', 'POST'])
def index():
    cache_message = None
    recommendations = None

    if request.method == 'POST':
        # Retrieving a user request from a form  Получение запроса пользователя из формы
        query = request.form['search_query'].strip()

        # Search for events in the Redis cache  Поиск мероприятий в кэше Redis
        cached_results = redis_client.get(f'search:{query}')
        if cached_results:
            # If the results are found in the cache, we use them  Если результаты найдены в кэше, используем их
            event_list = json.loads(cached_results)
            cache_message = "Results retrieved from Redis cache"
            event_type = event_list[0]['type']
            recommendations = get_recommendations(event_type)
        else:
            # If the results are not found in the cache, search in MongoDB  Если результаты не найдены в кэше, выполняем поиск в MongoDB
            event_list = list(events_collection.find({"name": {"$regex": query, "$options": "i"}})) #$regex регулярные выражения для поиска. query название. i что мы ищем

            # Save the search results in the Redis cache (within 60 seconds)   Сохраняем результаты поиска в кэше Redis (в течение 60 секунд)
            redis_client.setex(f'search:{query}', 60, json_util.dumps(event_list))

            # Getting the event type from the first result  Получение типа мероприятия из первого результата
            if event_list and 'type' in event_list[0]:
                event_type = event_list[0]['type']

                # Receive recommendations based on the type of event   Получение рекомендаций на основе типа мероприятия
                recommendations = get_recommendations(event_type)

        return render_template('index.html', search_results=event_list, query=query,
                               cache_message=cache_message, recommendations=recommendations)

    return render_template('index.html', search_results=None, query=None, cache_message=None, recommendations=None)


# Events page   Страница с мероприятиями
@app.route('/events')
def events():
    # Getting the list of events from MongoDB sorted by date   Получение списка мероприятий из MongoDB, отсортированных по дате
    event_list = list(events_collection.find().sort('date', 1))

    return render_template('events.html', events=event_list)

# Function for adding an event to MongoDB   Функция добавления мероприятия в MongoDB
@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        # Retrieving data from a form  Получение данных из формы
        event_name = request.form['event_name']
        event_location = request.form['event_location']
        event_date = request.form['event_date']
        event_description = request.form['event_description']
        event_type = request.form['event_type']

        # Saving an event in MongoDB  Сохранение мероприятия в MongoDB
        event_data = {
            'name': event_name,
            'location': event_location,
            'date': event_date,
            'description': event_description,
            'type': event_type
        }
        event_id = str(events_collection.insert_one(event_data).inserted_id)

        # Saving an event in Neo4j  Сохранение мероприятия в Neo4j
        save_event_to_neo4j(event_id, event_data)

        return redirect(url_for('events'))

    return render_template('add_event.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
