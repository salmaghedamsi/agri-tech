from app import create_app, db
from app.models.user import User
from app.models.product import Product
from app.models.course import Course
from app.models.land import Land
from app.models.forum import ForumPost, ForumComment
from app.models.weather import WeatherData
from app.models.iot import IoTDevice, IoTData

app = create_app()

def create_tables():
    """Create database tables"""
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, host='0.0.0.0', port=5000)
