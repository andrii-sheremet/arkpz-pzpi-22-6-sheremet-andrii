from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError

# Ініціалізація Flask та Marshmallow
app = Flask(__name__)
ma = Marshmallow(app)

# Модель для валідації вхідних даних
class GreetingRequestSchema(ma.Schema):
    name = ma.String(required=True, validate=lambda x: len(x) > 0, error_messages={"required": "Name is required", "null": "Name cannot be empty"})

# Валідація запиту
def validate_request_data(data):
    try:
        # Валідація за допомогою схемы Marshmallow
        schema = GreetingRequestSchema()
        return schema.load(data)  # Якщо дані правильні, повертається очищений об'єкт
    except ValidationError as err:
        return err.messages  # Повертає повідомлення про помилки валідації

# Створення API для обробки запитів
@app.route('/api/greet', methods=['POST'])
def greet():
    data = request.get_json()

    # Викликаємо функцію для валідації даних
    validation_result = validate_request_data(data)

    if isinstance(validation_result, dict):  # Якщо дані коректні
        name = validation_result.get('name', 'Guest')
        return jsonify(message=f"Hello, {name}!")
    else:
        # Якщо є помилки валідації, повертаємо їх клієнту
        return jsonify(validation_result), 400

# Головна точка входу для запуску сервера
if __name__ == '__main__':
    app.run(debug=True)
