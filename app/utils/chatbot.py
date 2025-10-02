import openai
import os
import json
import re
import random
from datetime import datetime
from app import db
from app.models.chatbot import ChatSession, ChatMessage

# Gemini AI Integration
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = False
    
    # Configure Gemini API
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    if GEMINI_API_KEY:
        print("🔧 Initializing Gemini API...")
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Find available models and use the first working one
        try:
            print("🔍 Checking available Gemini models...")
            available_models = list(genai.list_models())
            
            # Print available models for debugging
            print(f"📋 Found {len(available_models)} models")
            for model in available_models[:5]:  # Show first 5
                if 'generateContent' in model.supported_generation_methods:
                    print(f"   ✅ Available: {model.name}")
            
            # Try to use the latest available models first
            preferred_models = [
                "models/gemini-2.5-flash",
                "models/gemini-2.5-pro-preview-03-25",
                "models/gemini-1.5-pro", 
                "models/gemini-1.5-flash",
                "gemini-2.5-flash",
                "gemini-1.5-pro",
                "gemini-1.5-flash"
            ]
            
            gemini_model = None
            for model_name in preferred_models:
                try:
                    print(f"🧪 Testing model: {model_name}")
                    gemini_model = genai.GenerativeModel(model_name)
                    
                    # Simple test without content generation
                    if gemini_model:
                        print(f"✅ Successfully initialized: {model_name}")
                        GEMINI_AVAILABLE = True
                        break
                        
                except Exception as model_error:
                    print(f"❌ Model {model_name} failed: {model_error}")
                    continue
                    
            if not GEMINI_AVAILABLE:
                print("❌ No working Gemini models found")
                # Try one more time with any available model
                for model in available_models:
                    if 'generateContent' in model.supported_generation_methods:
                        try:
                            print(f"🔄 Trying fallback model: {model.name}")
                            gemini_model = genai.GenerativeModel(model.name)
                            GEMINI_AVAILABLE = True
                            print(f"✅ Using fallback model: {model.name}")
                            break
                        except:
                            continue
                
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            GEMINI_AVAILABLE = False
            
except ImportError:
    print("⚠️ Google Generative AI not installed. Using fallback to OpenAI/mock responses.")
    GEMINI_AVAILABLE = False
    gemini_model = None

def detect_language(text):
    """Detect language from user input"""
    if not text.strip():
        return 'ar'
    
    text_lower = text.lower()
    
    # Tunisian Arabic detection (dialect)
    tunisian_words = ['kifech', 'nazre3', 'tofeh', 'dela3', 'chnowa', 'wach', 'mta3', 'besh', 'aaslama', 'chneya', 'fama', 'barsha']
    if any(word in text_lower for word in tunisian_words):
        return 'tn'
    
    # Arabic script detection
    arabic_pattern = re.compile('[\u0600-\u06FF]')
    if arabic_pattern.search(text):
        return 'ar'
    
    # French detection
    french_words = ['comment', 'cultiver', 'planter', 'agriculture', 'serre', 'sol', 'eau', 'culture', 'ferme', 'récolte']
    if any(word in text_lower for word in french_words):
        return 'fr'
    
    # English detection
    english_words = ['how', 'grow', 'plant', 'agriculture', 'farming', 'greenhouse', 'crop', 'harvest', 'soil', 'water']
    if any(word in text_lower for word in english_words):
        return 'en'
    
    # Default to Arabic for MENA region
    return 'ar'

def get_gemini_response(query, language='ar'):
    """Get response from Gemini AI with agriculture focus"""
    if not GEMINI_AVAILABLE or not gemini_model:
        return None
    
    try:
        # Create agriculture-focused prompts based on language
        if language == 'ar':
            prompt = f"""أنت خبير زراعي متخصص في الزراعة في تونس والمنطقة المغاربية. أجب على هذا السؤال باللغة العربية:

السؤال: {query}

قدم إجابة مفيدة ومفصلة عن:
- تقنيات الزراعة المناسبة للمناخ التونسي
- أفضل أوقات الزراعة والحصاد
- إدارة المياه والري
- مكافحة الآفات بطريقة طبيعية
- اختيار الأصناف المناسبة
- نصائح عملية يمكن تطبيقها

استخدم معلومات حديثة ومناسبة للمزارعين في تونس."""

        elif language == 'tn':
            prompt = f"""Enta khabir zer3i motakhassis fel zer3a f Tounes w el mantaqa el maghribiya. Jaweb 3la hedha sou2al bil lahja tounisiya:

Sou2al: {query}

3ti jawaba mofida w mofasla 3la:
- Tekniket zer3a monasba lil manakh tounisi
- A7san aw9at zer3a w 7asad
- Idarat el miya w el ray
- Mokafahat el afat bil toriqa tabi3iya
- Ikhtiyar el asnaf el monasba
- Nase7a 3amaliya momkin tat7a9a9

Ista3mal ma3loumet 7aditha w monasba lil fellahin f Tounes."""

        elif language == 'fr':
            prompt = f"""Vous êtes un expert agricole spécialisé dans l'agriculture en Tunisie et au Maghreb. Répondez à cette question en français:

Question: {query}

Fournissez une réponse utile et détaillée sur:
- Techniques agricoles adaptées au climat tunisien
- Meilleurs moments pour planter et récolter
- Gestion de l'eau et irrigation
- Lutte naturelle contre les parasites
- Choix des variétés appropriées
- Conseils pratiques applicables

Utilisez des informations récentes et adaptées aux agriculteurs tunisiens."""

        else:  # English
            prompt = f"""You are an agricultural expert specializing in farming in Tunisia and North Africa. Answer this question in English:

Question: {query}

Provide a helpful and detailed answer about:
- Agricultural techniques suitable for Tunisian climate
- Best times for planting and harvesting
- Water management and irrigation
- Natural pest control methods
- Choosing appropriate varieties
- Practical applicable advice

Use current information suitable for farmers in Tunisia."""

        print(f"🤖 Sending prompt to Gemini (language: {language})")
        print(f"🔍 Gemini model available: {gemini_model is not None}")
        
        # Generate response with better error handling
        try:
            print("🔄 Calling gemini_model.generate_content...")
            response = gemini_model.generate_content(prompt)
            print(f"🔍 Response object type: {type(response)}")
            print(f"🔍 Response object: {response}")
            
            if response and hasattr(response, 'text'):
                print(f"🔍 Response has text attribute: {hasattr(response, 'text')}")
                if response.text:
                    print(f"✅ Gemini response received ({len(response.text)} chars)")
                    print(f"🔍 Response preview: {response.text[:100]}...")
                    return response.text.strip()
                else:
                    print(f"❌ Response.text is empty: '{response.text}'")
            elif response and hasattr(response, 'parts'):
                print(f"🔍 Response has parts: {len(response.parts) if response.parts else 0}")
                # Handle structured response
                text_parts = []
                for part in response.parts:
                    if hasattr(part, 'text'):
                        text_parts.append(part.text)
                        print(f"🔍 Part text: {part.text[:50]}...")
                if text_parts:
                    result = ' '.join(text_parts).strip()
                    print(f"✅ Gemini structured response received ({len(result)} chars)")
                    return result
                else:
                    print("❌ No text parts found in structured response")
            else:
                print(f"❌ Response has no text or parts attributes")
                print(f"🔍 Available attributes: {dir(response) if response else 'None'}")
            
            print("❌ No valid response text from Gemini")
            return None
            
        except Exception as api_error:
            print(f"❌ Gemini content generation error: {type(api_error).__name__}: {api_error}")
            import traceback
            traceback.print_exc()
            return None
            
    except Exception as e:
        print(f"❌ Gemini function error: {e}")
        return None

def get_ai_response(message, language=None, session_id=None):
    """Enhanced AI response with Gemini integration"""
    
    # Auto-detect language if not provided
    if not language:
        language = detect_language(message)
    
    print(f"🧠 Processing message: '{message}' (detected language: {language})")
    print(f"🔍 GEMINI_AVAILABLE: {GEMINI_AVAILABLE}")
    print(f"🔍 is_agriculture_related: {is_agriculture_related(message)}")
    
    # Try Gemini first for agriculture questions
    if GEMINI_AVAILABLE and is_agriculture_related(message):
        print("🌱 Trying Gemini for agriculture response...")
        try:
            gemini_response = get_gemini_response(message, language)
            print(f"🔍 Gemini raw response: '{gemini_response}'")
            print(f"🔍 Gemini response length: {len(gemini_response.strip()) if gemini_response else 0}")
            
            if gemini_response and len(gemini_response.strip()) > 10:  # Valid response
                print(f"✅ Returning Gemini response: {gemini_response[:100]}...")
                return gemini_response
            else:
                print("⚠️ Gemini response too short or empty, trying fallback...")
        except Exception as e:
            print(f"⚠️ Gemini failed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    else:
        if not GEMINI_AVAILABLE:
            print("❌ Gemini not available")
        if not is_agriculture_related(message):
            print("❌ Message not agriculture-related")
    
    # Final fallback to enhanced mock response
    print("📝 Using enhanced mock response...")
    return get_enhanced_mock_response(message, language)

def is_agriculture_related(query):
    """Check if query is agriculture related"""
    agriculture_keywords = {
        'en': ['farm', 'crop', 'plant', 'grow', 'harvest', 'soil', 'irrigation', 'pesticide', 'fertilizer', 'greenhouse', 'agriculture', 'farming'],
        'ar': ['زراعة', 'محصول', 'نبات', 'حقل', 'مزرعة', 'بذور', 'حصاد', 'تربة', 'ري', 'سماد', 'آفة'],
        'fr': ['agriculture', 'culture', 'plante', 'récolte', 'ferme', 'sol', 'irrigation', 'engrais', 'serre'],
        'tn': ['zer3a', 'mahsoul', 'nabta', 'ha9l', 'mazra3a', 'bdhour', 'hasad', 'torba', 'ray', 'smad']
    }
    
    query_lower = query.lower()
    
    # Check all language keywords
    for lang_keywords in agriculture_keywords.values():
        if any(keyword in query_lower for keyword in lang_keywords):
            return True
    
    return True  # Default to True for agriculture platform

def get_system_prompt(language):
    """Enhanced system prompt based on language"""
    
    prompts = {
        'en': """You are AgriConnect AI, an expert agricultural assistant specializing in Tunisia and North Africa. You help farmers, investors, and agricultural experts with:
        - Crop management and farming techniques for Mediterranean/arid climates
        - Weather-related agricultural advice for MENA region
        - Market information and pricing for local crops
        - Investment opportunities in agriculture
        - Land management and leasing
        - Agricultural education and courses
        - IoT and smart farming technologies
        - Water conservation and irrigation techniques
        - Pest management using natural methods
        
        Focus on practical advice for Tunisian farmers. Consider local climate, soil conditions, and traditional practices. Always provide actionable, culturally appropriate recommendations.""",
        
        'ar': """أنت AgriConnect AI، مساعد زراعي خبير متخصص في تونس والمنطقة المغاربية. تساعد المزارعين والمستثمرين والخبراء الزراعيين في:
        - إدارة المحاصيل والتقنيات الزراعية للمناخ المتوسطي والجاف
        - النصائح الزراعية المتعلقة بالطقس لمنطقة الشرق الأوسط وشمال أفريقيا
        - معلومات السوق والأسعار للمحاصيل المحلية
        - فرص الاستثمار في الزراعة
        - إدارة الأراضي والإيجار
        - التعليم الزراعي والدورات
        - تقنيات الزراعة الذكية وإنترنت الأشياء
        - حفظ المياه وتقنيات الري
        - إدارة الآفات بالطرق الطبيعية
        
        ركز على النصائح العملية للمزارعين التونسيين. اعتبر المناخ المحلي وظروف التربة والممارسات التقليدية. قدم دائماً توصيات قابلة للتطبيق ومناسبة ثقافياً.""",
        
        'tn': """Enta AgriConnect AI, mousa3ed zer3i khabir motakhassis f Tounes w el mantaqa el maghribiya. T3awen fel fellahin, moustathmirin, w khebar zer3iyin f:
        - Idara el mahsoulat w tekniket zer3iya lil manakh motawassi w najf
        - Nase7a zer3iya mta3a el taqs lil mantaqa MENA
        - Ma3loumat el souk w el as3ar lil mahsoulat mahalliya
        - Fors el istithmar fel zer3a
        - Idara el ard w el ijara
        - Ta3lim zer3i w doros
        - Teknologiyet zer3a dhekiya w IoT
        - Hifz el miya w tekniket ray
        - Idarat el afat bil toro9 tabi3iya
        
        Rakkez 3la nase7a 3amaliya lil fellahin touansa. Khodh bil i3tibar el manakh mahalli w dhorof torba w momarasat ta9lidiya. Daima 3ti tawsiyat momkin ttat7a9a9 w monasba thaqafiyan.""",
        
        'fr': """Vous êtes AgriConnect AI, un assistant agricole expert spécialisé en Tunisie et Afrique du Nord. Vous aidez les agriculteurs, investisseurs et experts agricoles avec:
        - Gestion des cultures et techniques agricoles pour climats méditerranéens/arides
        - Conseils agricoles liés à la météo pour la région MENA
        - Informations de marché et prix pour les cultures locales
        - Opportunités d'investissement en agriculture
        - Gestion et location de terres
        - Éducation agricole et cours
        - Technologies agricoles intelligentes et IoT
        - Conservation de l'eau et techniques d'irrigation
        - Gestion des parasites par méthodes naturelles
        
        Concentrez-vous sur des conseils pratiques pour les agriculteurs tunisiens. Considérez le climat local, les conditions du sol et les pratiques traditionnelles."""
    }
    
    return prompts.get(language, prompts['en'])

def get_enhanced_mock_response(message, language):
    """Enhanced mock responses with agriculture focus"""
    
    responses = {
        'en': [
            "🌱 Great question about agriculture! Based on Tunisian farming conditions, I'd recommend focusing on drought-resistant crops and efficient irrigation methods. Our platform offers detailed courses on sustainable farming practices.",
            "🚜 For that farming challenge, consider the Mediterranean climate patterns in Tunisia. Water conservation is key - check our IoT monitoring tools to optimize irrigation timing.",
            "🌾 That's an excellent agricultural inquiry! In Tunisia's climate, timing is crucial for planting and harvesting. Our weather monitoring and expert mentoring can help you plan effectively.",
            "🍅 Regarding your crop question, consider local soil conditions and seasonal patterns. Our marketplace connects you with other farmers who've faced similar challenges in the region."
        ],
        'ar': [
            "🌱 سؤال ممتاز حول الزراعة! بناءً على ظروف الزراعة التونسية، أنصح بالتركيز على المحاصيل المقاومة للجفاف وطرق الري الفعالة. منصتنا تقدم دورات مفصلة عن ممارسات الزراعة المستدامة.",
            "🚜 بالنسبة لهذا التحدي الزراعي، اعتبر أنماط المناخ المتوسطي في تونس. حفظ المياه أمر أساسي - تفقد أدوات المراقبة الذكية لتحسين توقيت الري.",
            "🌾 هذا استفسار زراعي ممتاز! في مناخ تونس، التوقيت أمر حاسم للزراعة والحصاد. مراقبة الطقس والإرشاد الخبير يمكن أن يساعدك في التخطيط الفعال.",
            "🍅 بخصوص سؤالك عن المحاصيل، اعتبر ظروف التربة المحلية والأنماط الموسمية. سوقنا يربطك بمزارعين آخرين واجهوا تحديات مماثلة في المنطقة."
        ],
        'tn': [
            "🌱 Sou2al mzyan 3la zer3a! 3la asas dhorof zer3a f Tounes, ansa7 brakkez 3la mahsoulat moqawma lil jaf w toro9 ray fa33ala. Platform mt3na tqaddem doros mofasla 3la momarasat zer3a mostadama.",
            "🚜 Bel nisba li hedha ta7addi zer3i, khodh bil i3tibar anmat manakh motawassi f Tounes. Hifz miya asasi - chouf adawat moraqaba dhekiya besh t7assen taw9it ray.",
            "🌾 Hedha istifsar zer3i momtaz! F manakh Tounes, taw9it 7asm lil zer3a w hasad. Moraqabet taqs w irshad khabir ynajem y3awnek fi takhtit fa33al.",
            "🍅 Bel nisba li sou2alek 3la mahsoulat, khodh bil i3tibar dhorof torba mahalliya w anmat mawsimiya. Soukna yrabtk ma3 fellahin okhra wa9fou ta7adiyat mithla fi mantaqa."
        ],
        'fr': [
            "🌱 Excellente question sur l'agriculture! Selon les conditions agricoles tunisiennes, je recommande de se concentrer sur les cultures résistantes à la sécheresse et les méthodes d'irrigation efficaces.",
            "🚜 Pour ce défi agricole, considérez les modèles climatiques méditerranéens en Tunisie. La conservation de l'eau est clé - consultez nos outils de surveillance IoT pour optimiser le timing d'irrigation.",
            "🌾 C'est une excellente question agricole! Dans le climat tunisien, le timing est crucial pour planter et récolter. Notre surveillance météo et mentorat expert peuvent vous aider.",
            "🍅 Concernant votre question sur les cultures, considérez les conditions du sol local et les patterns saisonniers. Notre marketplace vous connecte avec d'autres fermiers ayant fait face à des défis similaires."
        ]
    }
    
    return random.choice(responses.get(language, responses['en']))

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
