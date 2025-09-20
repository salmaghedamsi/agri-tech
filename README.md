# AgriConnect - Smart Farming Platform

AgriConnect is a comprehensive smart farming platform that connects farmers, investors, and agricultural experts in a unified ecosystem. The platform provides e-commerce marketplace, e-learning hub, mentoring system, investment opportunities, weather monitoring, IoT integration, and community features.

## Features

### 🌱 For Farmers

- **E-commerce Marketplace**: Sell agricultural products directly to consumers
- **Learning Hub**: Access courses on modern farming techniques
- **IoT Integration**: Monitor crops with smart sensors and devices
- **Weather Monitoring**: Real-time weather data and agricultural advice
- **Investment Opportunities**: Create investment proposals for funding
- **Community Support**: Connect with other farmers and experts

### 💰 For Investors

- **Investment Platform**: Browse and invest in agricultural projects
- **Land Investment**: Buy, sell, or lease agricultural land
- **Market Analytics**: Access market data and trends
- **Expert Consultation**: Connect with agricultural experts

### 🎓 For Experts

- **Course Creation**: Create and sell educational content
- **Mentoring System**: Provide one-on-one guidance to farmers
- **Community Engagement**: Share knowledge through forums
- **Revenue Generation**: Monetize expertise through courses and mentoring

### 🤖 AI Features

- **Multilingual Chatbot**: Support in English, Arabic, and Tunisian dialect
- **Agricultural Advice**: AI-powered recommendations based on weather and crop data
- **Smart Notifications**: Automated alerts for weather, IoT devices, and market changes

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy with SQLite/PostgreSQL
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **AI Integration**: OpenAI GPT for chatbot
- **Weather API**: OpenWeatherMap integration
- **Real-time Updates**: WebSocket support for live data

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd agriconnect
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:

   ```env
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///agriconnect.db
   OPENAI_API_KEY=your-openai-api-key
   WEATHER_API_KEY=your-weather-api-key
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   ```

5. **Initialize the database**

   ```bash
   python run.py
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

The application will be available at `http://localhost:5000`

## Project Structure

```
agriconnect/
├── app/
│   ├── __init__.py          # Flask app initialization
│   ├── models/              # Database models
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── course.py
│   │   ├── land.py
│   │   ├── forum.py
│   │   ├── weather.py
│   │   ├── iot.py
│   │   ├── mentoring.py
│   │   ├── investment.py
│   │   └── chatbot.py
│   ├── routes/              # Route handlers
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── marketplace.py
│   │   ├── learning.py
│   │   ├── mentoring.py
│   │   ├── investment.py
│   │   ├── weather.py
│   │   ├── community.py
│   │   ├── admin.py
│   │   └── api.py
│   ├── forms/               # WTForms
│   │   ├── auth.py
│   │   ├── product.py
│   │   ├── course.py
│   │   ├── land.py
│   │   ├── forum.py
│   │   ├── mentoring.py
│   │   └── investment.py
│   ├── utils/               # Utility functions
│   │   ├── weather.py
│   │   └── chatbot.py
│   ├── static/              # Static files
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/           # HTML templates
│       ├── base.html
│       ├── auth/
│       ├── dashboard/
│       ├── marketplace/
│       ├── learning/
│       ├── mentoring/
│       ├── investment/
│       ├── weather/
│       ├── community/
│       └── admin/
├── migrations/              # Database migrations
├── tests/                   # Test files
├── config.py               # Configuration
├── run.py                  # Application entry point
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Detailed File Reference

Use this section to quickly understand what each important file or folder does.

### Root level

- `run.py`: Development entry point. Creates the Flask app from `app/__init__.py` and runs the dev server.
- `start.py`: Optional alternate starter; often used to run with production servers or CLI helpers.
- `config.py`: Central configuration. Loads settings from environment variables (see `.env`/`env_example.txt`).
- `requirements.txt`: Python dependencies to install with `pip`.
- `README.md`: This documentation.
- `QUICK_START.md`: Shorter, step-by-step setup instructions.
- `env_example.txt`: Template for your `.env` file. Copy and rename to `.env` then fill in secrets.
- `migrations/`: Database migration scripts (Alembic/Flask-Migrate). Auto-generated when models change.
- `tests/`: Test suite skeleton. Add unit/integration tests here.
- `instance/agriconnect.db`: SQLite database file stored outside version control defaults. Safe place for instance data.
- `create_test_user.py`: Helper script to seed the DB with a test user.

### `app/` package

- `app/__init__.py`: App factory; initializes Flask, database, login manager, blueprints, and extensions.

#### `app/models/` (Database models)

- `user.py`: User accounts, authentication properties, roles, and relationships.
- `product.py`: Marketplace products, categories, reviews, pricing, and inventory fields.
- `course.py`: Learning entities: courses, modules, enrollments, and progress tracking.
- `land.py`: Land listing entities for sale/lease and related investment linkages.
- `forum.py`: Community forum posts, comments, categories, and relationships.
- `weather.py`: Weather data storage for current and forecast metrics; alert entities.
- `iot.py`: IoT devices, sensor readings, and alert thresholds.
- `mentoring.py`: Mentor profiles, mentoring requests, and scheduled sessions.
- `investment.py`: Investment opportunities and proposals; ties to `land` and `user`.
- `chatbot.py`: AI chat sessions and messages persisted for conversation history.

#### `app/routes/` (Blueprints and endpoints)

- `auth.py`: Login, register, logout, password reset flows.
- `dashboard.py`: Main authenticated dashboard pages and stats.
- `marketplace.py`: Product listing, product detail, add/edit product endpoints.
- `learning.py`: Course list/detail, create course, enroll, and progress endpoints.
- `mentoring.py`: Mentor discovery, requests, scheduling actions.
- `investment.py`: Investment discovery and proposal submission routes.
- `weather.py`: Weather dashboard and API feeds for current/forecast.
- `community.py`: Forum index, create post, search, and related APIs.
- `admin.py`: Admin-only management pages and actions.
- `api.py`: Shared JSON APIs used across modules (e.g., search, small utilities).

#### `app/forms/` (WTForms schemas for validation)

- `auth.py`: Login, registration, password reset forms.
- `product.py`: Add/edit product forms with validation.
- `course.py`: Create course/module forms.
- `land.py`: Create land listing forms.
- `forum.py`: Create forum post/comment forms.
- `mentoring.py`: Mentor profile and mentoring request forms.
- `investment.py`: Create investment and proposal forms.

#### `app/utils/` (Reusable helpers)

- `weather.py`: Functions to call weather APIs, transform data, and cache results.
- `chatbot.py`: OpenAI client wrappers and message formatting for the chatbot.

#### `app/static/` (Front-end assets)

- `css/style.css`: Global styles and module-specific tweaks.
- `js/main.js`: Basic interactive behavior and small utilities.
- `images/`: Static images and icons.

#### `app/templates/` (Jinja2 templates)

- `base.html`: Global layout, navbar, flash messages, and asset includes.
- `auth/`: `login.html`, `register.html`, `forgot_password.html`, `reset_password.html`.
- `dashboard/`: Main user dashboard pages.
- `marketplace/`: `index.html`, `product_detail.html`, `add_product.html`.
- `learning/`: Course listing and detail pages.
- `mentoring/`: Mentoring discovery and scheduling pages.
- `investment/`: Investment listing and creation pages.
- `weather/`: Weather dashboard visualizations.
- `community/`: Forum index and create post page.
- `admin/`: Admin layout and management templates.

### How things fit together (high-level flow)

- A request hits a blueprint in `app/routes/*`, which may use a `WTForm` from `app/forms/*` to validate input.
- Business logic interacts with models in `app/models/*` via SQLAlchemy sessions.
- Helpers in `app/utils/*` call external services (OpenAI, weather) and return normalized data.
- A response is rendered with a template in `app/templates/*` or returned as JSON from API routes.

### Common tasks

- Add a new page: create route in `app/routes`, template in `app/templates`, optional form in `app/forms`, and model updates in `app/models` if needed.
- Add a new API: define endpoint in `app/routes/api.py` or the relevant module route file; return JSON.
- Change config: update environment variables and, if needed, defaults in `config.py`.

## API Endpoints

### Authentication

- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/logout` - User logout

### Dashboard

- `GET /dashboard/` - Main dashboard
- `GET /api/dashboard/stats` - Dashboard statistics

### Marketplace

- `GET /marketplace/` - Product listings
- `POST /marketplace/add-product` - Add new product
- `GET /api/marketplace/search` - Search products

### Learning

- `GET /learning/` - Course listings
- `POST /learning/create-course` - Create new course
- `POST /learning/course/<id>/enroll` - Enroll in course

### Investment

- `GET /investment/` - Investment opportunities
- `POST /investment/create-investment` - Create investment opportunity
- `POST /investment/investment/<id>/propose` - Submit investment proposal

### Weather

- `GET /weather/` - Weather dashboard
- `GET /api/weather/current` - Current weather data
- `GET /api/weather/forecast` - Weather forecast

### Community

- `GET /community/` - Forum home
- `POST /community/create-post` - Create forum post
- `GET /api/community/search` - Search forum posts

### AI Chatbot

- `POST /api/chat` - Send message to AI chatbot

## Database Models

### User Management

- **User**: User accounts with different types (farmer, investor, expert, admin)
- **Authentication**: Secure password hashing and session management

### E-commerce

- **Product**: Agricultural products for sale
- **ProductCategory**: Product categorization
- **ProductReview**: Customer reviews and ratings

### Learning

- **Course**: Educational courses
- **CourseModule**: Course content modules
- **CourseEnrollment**: Student enrollments
- **CourseProgress**: Learning progress tracking

### Investment

- **Investment**: Investment opportunities
- **InvestmentProposal**: Investment proposals
- **Land**: Land listings
- **LandInvestment**: Land investment records
- **LandLease**: Land lease agreements

### Community

- **ForumPost**: Community forum posts
- **ForumComment**: Post comments and replies
- **ForumCategory**: Forum categories

### Weather & IoT

- **WeatherData**: Weather sensor data
- **WeatherAlert**: Weather alerts and warnings
- **IoTDevice**: IoT device management
- **IoTData**: IoT sensor readings
- **IoTAlert**: Device alerts and notifications

### Mentoring

- **Mentor**: Expert mentor profiles
- **MentoringRequest**: Mentoring session requests
- **MentoringSession**: Scheduled mentoring sessions

### AI Chatbot

- **ChatSession**: Chat conversation sessions
- **ChatMessage**: Individual chat messages

## Configuration

The application uses environment variables for configuration. Key settings include:

- `SECRET_KEY`: Flask secret key for session security
- `DATABASE_URL`: Database connection string
- `OPENAI_API_KEY`: OpenAI API key for chatbot functionality
- `WEATHER_API_KEY`: Weather API key for weather data
- `MAIL_*`: Email configuration for notifications

## Deployment

### Production Deployment

1. **Set up a production database** (PostgreSQL recommended)
2. **Configure environment variables** for production
3. **Use a WSGI server** like Gunicorn
4. **Set up reverse proxy** with Nginx
5. **Enable HTTPS** with SSL certificates
6. **Set up monitoring** and logging

### Docker Deployment

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Create an issue in the repository
- Contact the development team
- Check the documentation

## Roadmap

### Phase 1 (Current)

- ✅ Core platform functionality
- ✅ User management and authentication
- ✅ E-commerce marketplace
- ✅ Learning management system
- ✅ Basic AI chatbot

### Phase 2 (Planned)

- 🔄 Advanced IoT integration
- 🔄 Mobile application
- 🔄 Advanced analytics dashboard
- 🔄 Payment gateway integration
- 🔄 Multi-language support

### Phase 3 (Future)

- 📋 Blockchain integration for land ownership
- 📋 Advanced AI recommendations
- 📋 Satellite imagery integration
- 📋 Supply chain tracking
- 📋 Carbon footprint monitoring

---

**AgriConnect** - Empowering sustainable agriculture through technology and community.
