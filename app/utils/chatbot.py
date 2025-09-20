import openai
import os
import json
from datetime import datetime
from app import db
from app.models.chatbot import ChatSession, ChatMessage

def get_ai_response(message, language='en', session_id=None):
    """Get AI response for chatbot"""
    
    # Set up OpenAI API
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    
    if not openai.api_key:
        return get_mock_response(message, language)
    
    try:
        # Get conversation history
        conversation_history = []
        if session_id:
            session = ChatSession.query.get(session_id)
            if session:
                recent_messages = ChatMessage.query.filter_by(
                    session_id=session_id
                ).order_by(ChatMessage.timestamp.desc()).limit(10).all()
                
                # Reverse to get chronological order
                for msg in reversed(recent_messages):
                    role = "user" if msg.message_type == "user" else "assistant"
                    conversation_history.append({
                        "role": role,
                        "content": msg.content
                    })
        
        # Add current message
        conversation_history.append({
            "role": "user",
            "content": message
        })
        
        # Create system prompt based on language
        system_prompt = get_system_prompt(language)
        
        # Prepare messages for API
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return get_mock_response(message, language)

def get_system_prompt(language):
    """Get system prompt based on language"""
    
    prompts = {
        'en': """You are AgriConnect AI, a helpful agricultural assistant. You help farmers, investors, and agricultural experts with:
        - Crop management and farming techniques
        - Weather-related agricultural advice
        - Market information and pricing
        - Investment opportunities in agriculture
        - Land management and leasing
        - Agricultural education and courses
        - IoT and smart farming technologies
        
        Always provide practical, actionable advice. If you don't know something specific, suggest consulting with local agricultural experts or using the platform's features like the marketplace, learning hub, or mentoring system.""",
        
        'ar': """أنت AgriConnect AI، مساعد زراعي مفيد. تساعد المزارعين والمستثمرين والخبراء الزراعيين في:
        - إدارة المحاصيل والتقنيات الزراعية
        - النصائح الزراعية المتعلقة بالطقس
        - معلومات السوق والأسعار
        - فرص الاستثمار في الزراعة
        - إدارة الأراضي والإيجار
        - التعليم الزراعي والدورات
        - تقنيات الزراعة الذكية وإنترنت الأشياء
        
        قدم دائماً نصائح عملية وقابلة للتطبيق. إذا كنت لا تعرف شيئاً محدداً، اقترح استشارة خبراء زراعيين محليين أو استخدام ميزات المنصة مثل السوق أو مركز التعلم أو نظام الإرشاد.""",
        
        'tn': """Enta AgriConnect AI, mousa3ed zer3i mofid. T3awen fel fellahin, moustathmirin, w khebar zer3iyin f:
        - Idara el mahsoulat w tekniket zer3iya
        - Nase7a zer3iya mta3a el taqs
        - Ma3lumat el souk w el as3ar
        - Fors el istithmar fel zer3a
        - Idara el ard w el ijara
        - Ta3lim zer3i w doros
        - Teknologiyet zer3a dhekiya w IoT
        
        Daima 3ti nase7a 3amaliya w momkina ttwafa. Ila ma ta3refch 7aja m3ayna, iqtar7 istichara ma3 khebar zer3iyin mahaliyin aw istikhdam miziyet el platform mithl el souk aw markaz el ta3lim aw nizam el irchad."""
    }
    
    return prompts.get(language, prompts['en'])

def get_mock_response(message, language):
    """Get mock response when OpenAI API is not available"""
    
    responses = {
        'en': [
            "I understand you're asking about agriculture. While I'm currently in demo mode, AgriConnect offers comprehensive tools for farmers, investors, and experts. You can explore our marketplace, learning hub, mentoring system, and investment platform.",
            "That's a great agricultural question! In a real scenario, I'd provide detailed advice based on current data. For now, I recommend checking our learning courses or connecting with our expert mentors.",
            "I'd be happy to help with your farming question! Our platform includes weather monitoring, IoT device integration, and expert advice. Try exploring our community forum for similar discussions.",
            "For agricultural guidance, I suggest using our smart dashboard features, including real-time weather data, crop management tools, and market insights available on AgriConnect."
        ],
        'ar': [
            "أفهم أنك تسأل عن الزراعة. بينما أنا في وضع العرض التوضيحي حالياً، يوفر AgriConnect أدوات شاملة للمزارعين والمستثمرين والخبراء. يمكنك استكشاف سوقنا ومركز التعلم ونظام الإرشاد ومنصة الاستثمار.",
            "هذا سؤال زراعي رائع! في سيناريو حقيقي، سأقدم نصائح مفصلة بناءً على البيانات الحالية. في الوقت الحالي، أنصح بمراجعة دوراتنا التعليمية أو التواصل مع مرشدينا الخبراء.",
            "سأكون سعيداً لمساعدتك في سؤالك الزراعي! تتضمن منصتنا مراقبة الطقس وتكامل أجهزة إنترنت الأشياء ونصائح الخبراء. جرب استكشاف منتدى مجتمعنا للمناقشات المماثلة.",
            "للإرشاد الزراعي، أقترح استخدام ميزات لوحة التحكم الذكية، بما في ذلك بيانات الطقس في الوقت الفعلي وأدوات إدارة المحاصيل ورؤى السوق المتاحة على AgriConnect."
        ],
        'tn': [
            "Nfhem ennek tes2el 3la zer3a. Khater ena fel mode demo daba, AgriConnect yqaddem adawat shamla lil fellahin, moustathmirin, w khebar. Tnajem tstakshif soukna, markaz ta3lim, nizam irchad, w platform istithmar.",
            "Hetha sou2al zer3i mzyan! Fel scenario 7a9i9i, n3ti nase7a tafsil 3la asas donées 7alya. Daba, ansa7 bmraja3a dorosna ta3limiya aw rabt ma3 mourshidina khebar.",
            "Nkoun sa3id n3awnek f sou2alek zer3i! Platform m3ana tdhammel mraqaba taqs, tawhid aghdhet IoT, w nase7a khebar. Jarab tstakshif mnadi mojtama3na lil mounakchat mithla.",
            "Lil irchad zer3i, aqtar7 istikhdam miziyet dashboard dheki, yadhammel donées taqs real-time, adawat idara mahsoulat, w insights souk mawjouda 3la AgriConnect."
        ]
    }
    
    import random
    return random.choice(responses.get(language, responses['en']))

def get_agricultural_advice(weather_data, crop_type=None):
    """Get agricultural advice based on weather conditions"""
    
    advice = []
    
    if not weather_data:
        return ["No weather data available for agricultural advice."]
    
    # Temperature advice
    if weather_data.temperature < 5:
        advice.append("⚠️ Frost risk: Protect sensitive crops with covers or move them indoors.")
    elif weather_data.temperature > 35:
        advice.append("🌡️ High temperature: Increase irrigation frequency and provide shade for crops.")
    elif 15 <= weather_data.temperature <= 25:
        advice.append("✅ Optimal temperature range for most crops.")
    
    # Humidity advice
    if weather_data.humidity < 30:
        advice.append("💧 Low humidity: Increase irrigation and consider mulching to retain moisture.")
    elif weather_data.humidity > 80:
        advice.append("🌧️ High humidity: Watch for fungal diseases, ensure good air circulation.")
    
    # Precipitation advice
    if weather_data.precipitation > 10:
        advice.append("🌧️ Heavy rain expected: Check drainage systems and protect crops from waterlogging.")
    elif weather_data.precipitation == 0 and weather_data.humidity < 40:
        advice.append("🌵 Dry conditions: Schedule irrigation and consider drought-resistant crops.")
    
    # Wind advice
    if weather_data.wind_speed > 20:
        advice.append("💨 Strong winds: Secure greenhouses and protect young plants.")
    
    # UV index advice
    if weather_data.uv_index > 8:
        advice.append("☀️ High UV index: Provide shade for sensitive plants and protect yourself from sun exposure.")
    
    # Crop-specific advice
    if crop_type:
        crop_advice = get_crop_specific_advice(crop_type, weather_data)
        advice.extend(crop_advice)
    
    return advice if advice else ["Weather conditions are generally favorable for agricultural activities."]

def get_crop_specific_advice(crop_type, weather_data):
    """Get crop-specific agricultural advice"""
    
    crop_advice = {
        'tomatoes': [
            "🍅 Tomatoes: Ensure consistent watering and watch for blossom end rot in high humidity.",
            "🍅 Consider staking tomato plants for better air circulation."
        ],
        'wheat': [
            "🌾 Wheat: Monitor for rust diseases in high humidity conditions.",
            "🌾 Ensure proper drainage to prevent root diseases."
        ],
        'olives': [
            "🫒 Olives: Prune trees during dry periods to improve air circulation.",
            "🫒 Monitor for olive fly infestations in warm, humid conditions."
        ],
        'citrus': [
            "🍊 Citrus: Protect from frost damage during cold spells.",
            "🍊 Ensure adequate drainage to prevent root rot."
        ]
    }
    
    return crop_advice.get(crop_type.lower(), [])
