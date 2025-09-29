# AgriConnect - Quick Start Guide

## 🚀 Getting Started

### Test User Credentials
- **Email**: rima@gmail.com
- **Password**: rima00
- **User Type**: Farmer

### Running the Application

1. **Start the application**:
   ```bash
   python run.py
   ```

2. **Access the application**:
   - Open your browser and go to: http://localhost:5000
   - Login with the test credentials above

### Alternative Startup (with sample data)
```bash
python start.py
```

## 🌟 Features Available

### For Farmers (Test User)
- **Dashboard**: Overview of products, courses, and activities
- **Marketplace**: Add and manage agricultural products
- **Learning Hub**: Browse and enroll in courses
- **Investment**: Create investment opportunities
- **Weather**: Real-time weather data and agricultural advice
- **Community**: Participate in forum discussions
- **AI Chatbot**: Get agricultural advice in multiple languages

### Key Features
- **E-commerce Marketplace**: Buy and sell agricultural products
- **E-learning Platform**: Courses on modern farming techniques
- **Mentoring System**: Connect with agricultural experts
- **Investment Platform**: Fund agricultural projects
- **Weather Monitoring**: Real-time weather data and alerts
- **IoT Integration**: Smart farming device management
- **AI Chatbot**: Multilingual support (English, Arabic, Tunisian)
- **Community Forum**: Knowledge sharing and discussions

## 📱 User Interface

### Dashboard
- Statistics cards showing your activity
- Recent products, courses, and forum posts
- Weather information and alerts
- Quick action buttons

### Navigation
- **Dashboard**: Main overview
- **Marketplace**: Product listings and management
- **Learning**: Course catalog and enrollment
- **Mentoring**: Expert guidance and sessions
- **Investment**: Investment opportunities and land listings
- **Weather**: Weather data and agricultural advice
- **Community**: Forum discussions

### AI Assistant
- Click the "AI Assistant" button in the navigation
- Supports English, Arabic, and Tunisian dialect
- Get instant agricultural advice and recommendations

## 🔧 Technical Details

### Database
- SQLite database (agriconnect.db)
- All tables created automatically on first run
- Test user created with sample data

### API Endpoints
- `/api/search` - Global search
- `/api/chat` - AI chatbot
- `/api/weather/current` - Weather data
- `/api/dashboard/stats` - Dashboard statistics

### File Structure
```
agriconnect/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # Route handlers
│   ├── forms/           # Form definitions
│   ├── templates/       # HTML templates
│   ├── static/          # CSS, JS, images
│   └── utils/           # Utility functions
├── git            # Main application
├── start.py            # Startup with sample data
└── create_test_user.py # Create test user
```

## 🎯 Next Steps

1. **Login** with the test credentials
2. **Explore the dashboard** to see your overview
3. **Add a product** in the marketplace
4. **Browse courses** in the learning hub
5. **Try the AI chatbot** for agricultural advice
6. **Check weather data** for your location
7. **Participate in community** discussions

## 🐛 Troubleshooting

### Common Issues
1. **Import errors**: Make sure all dependencies are installed
2. **Database errors**: Delete agriconnect.db and restart
3. **Port already in use**: Change port in run.py

### Reset Database
```bash
rm agriconnect.db
python create_test_user.py
```

## 📞 Support

If you encounter any issues:
1. Check the console output for error messages
2. Verify all dependencies are installed
3. Ensure the database file is writable
4. Check that port 5000 is available

---

**AgriConnect** - Your smart farming companion! 🌱
