// AgriConnect Main JavaScript

// Global variables
let currentLanguage = 'en';
let chatSessionId = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Initialize charts if present
    initializeCharts();

    // Initialize real-time updates
    initializeRealTimeUpdates();

    // Initialize search functionality
    initializeSearch();

    // Initialize chatbot
    initializeChatbot();
}

// Chart initialization
function initializeCharts() {
    // Weather chart
    const weatherCtx = document.getElementById('weatherChart');
    if (weatherCtx) {
        const weatherChart = new Chart(weatherCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Temperature (°C)',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false
                    }
                }
            }
        });
    }

    // IoT data chart
    const iotCtx = document.getElementById('iotChart');
    if (iotCtx) {
        const iotChart = new Chart(iotCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Sensor Data',
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// Real-time updates
function initializeRealTimeUpdates() {
    // Update weather data every 10 minutes
    setInterval(updateWeatherData, 600000);
    
    // Update IoT data every 30 seconds
    setInterval(updateIoTData, 30000);
    
    // Update notifications every minute
    setInterval(updateNotifications, 60000);
}

function updateWeatherData() {
    fetch('/api/weather/current')
        .then(response => response.json())
        .then(data => {
            if (data.temperature) {
                updateWeatherDisplay(data);
            }
        })
        .catch(error => console.error('Error updating weather:', error));
}

function updateIoTData() {
    fetch('/api/iot/devices')
        .then(response => response.json())
        .then(data => {
            updateIoTDisplay(data);
        })
        .catch(error => console.error('Error updating IoT data:', error));
}

function updateNotifications() {
    fetch('/api/notifications')
        .then(response => response.json())
        .then(data => {
            updateNotificationDisplay(data);
        })
        .catch(error => console.error('Error updating notifications:', error));
}

// Search functionality
function initializeSearch() {
    const searchInput = document.getElementById('globalSearch');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(performSearch, 300));
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function performSearch(event) {
    const query = event.target.value;
    if (query.length < 3) return;

    fetch(`/api/search?q=${encodeURIComponent(query)}&limit=5`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data);
        })
        .catch(error => console.error('Error performing search:', error));
}

function displaySearchResults(results) {
    // Implementation for displaying search results
    console.log('Search results:', results);
}

// Chatbot functionality
function initializeChatbot() {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        });
    }
}

function setLanguage(language) {
    currentLanguage = language;
    
    // Update UI language indicators
    document.querySelectorAll('.language-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Add active class to selected language
    const selectedBtn = document.getElementById(`lang-${language}`);
    if (selectedBtn) {
        selectedBtn.classList.add('active');
    }
    
    // Update language display
    const langNames = {
        'ar': 'العربية',
        'tn': 'التونسي',
        'en': 'English'
    };
    
    const currentLangSpan = document.getElementById('currentLang');
    if (currentLangSpan) {
        currentLangSpan.textContent = langNames[language] || language;
    }
    
    // Update placeholder text based on language
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        const placeholders = {
            'ar': 'اسأل عن أي شيء يخص الزراعة...',
            'tn': 'اسأل على أي حاجة تخص الفلاحة...',
            'en': 'Ask me anything about agriculture...'
        };
        chatInput.placeholder = placeholders[language] || placeholders['en'];
    }
}

function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();
    
    if (!message) return;

    // Add user message to chat
    addMessageToChat(message, 'user');
    chatInput.value = '';

    // Show typing indicator
    showTypingIndicator();

    // Send message to API
    console.log('🚀 Sending message to API:', {
        message: message,
        session_id: chatSessionId,
        language: currentLanguage
    });

    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            session_id: chatSessionId,
            language: currentLanguage
        })
    })
    .then(response => {
        console.log('📡 Raw response:', response);
        console.log('📡 Response status:', response.status);
        console.log('📡 Response ok:', response.ok);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('📦 Response data:', data);
        hideTypingIndicator();
        
        if (data && data.response) {
            console.log('✅ Adding bot response to chat');
            addMessageToChat(data.response, 'bot');
            if (data.session_id) {
                chatSessionId = data.session_id;
                console.log('💾 Session ID saved:', chatSessionId);
            }
        } else {
            console.error('❌ No response in data:', data);
            throw new Error('No response received from server');
        }
    })
    .catch(error => {
        hideTypingIndicator();
        console.error('❌ Chat error details:', error);
        console.error('❌ Error type:', error.constructor.name);
        console.error('❌ Error message:', error.message);
        
        const errorMessages = {
            'ar': 'عذراً، حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى.',
            'tn': 'عذراني، صار خطأ في الاتصال. جرب مرة أخرى.',
            'en': 'Sorry, a connection error occurred. Please try again.'
        };
        
        const errorMsg = errorMessages[currentLanguage] || errorMessages['en'];
        addMessageToChat(`${errorMsg}\n\n🔍 Debug: ${error.message}`, 'bot');
    });
}

function addMessageToChat(message, sender) {
    const chatMessages = document.getElementById('chatMessages');
    
    // Remove welcome message if this is the first real message
    const welcomeMsg = chatMessages.querySelector('.text-center.text-muted');
    if (welcomeMsg && (sender === 'user' || sender === 'bot')) {
        welcomeMsg.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-wrapper mb-3 ${sender}`;
    
    const time = new Date().toLocaleTimeString();
    
    // Format the message content - preserve line breaks and structure
    const formattedMessage = message
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold text
        .replace(/\*(.*?)\*/g, '<em>$1</em>');  // Italic text
    
    const isRTL = /[\u0600-\u06FF\u0750-\u077F]/.test(message); // Detect Arabic/RTL text
    
    if (sender === 'user') {
        messageDiv.innerHTML = `
            <div class="d-flex justify-content-end mb-2">
                <div class="user-message p-3 rounded-3 bg-primary text-white shadow-sm" style="max-width: 80%; ${isRTL ? 'direction: rtl; text-align: right;' : ''}">
                    <div class="message-content">${formattedMessage}</div>
                    <div class="message-time mt-1">
                        <small class="opacity-75">${time}</small>
                    </div>
                </div>
                <div class="ms-2">
                    <i class="fas fa-user-circle fa-2x text-primary"></i>
                </div>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="d-flex justify-content-start mb-2">
                <div class="me-2">
                    <i class="fas fa-robot fa-2x text-success"></i>
                </div>
                <div class="bot-message p-3 rounded-3 bg-light border shadow-sm" style="max-width: 85%; ${isRTL ? 'direction: rtl; text-align: right;' : ''}">
                    <div class="d-flex align-items-center mb-2">
                        <strong class="text-success">🌾 المساعد الزراعي الذكي</strong>
                    </div>
                    <div class="message-content" style="line-height: 1.6; white-space: pre-line;">${formattedMessage}</div>
                    <div class="message-time mt-2">
                        <small class="text-muted">${time}</small>
                    </div>
                </div>
            </div>
        `;
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message-wrapper mb-3 typing-indicator';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <div class="d-flex justify-content-start mb-2">
            <div class="me-2">
                <i class="fas fa-robot fa-2x text-success"></i>
            </div>
            <div class="bot-message p-3 rounded-3 bg-light border shadow-sm">
                <div class="d-flex align-items-center">
                    <div class="spinner-border spinner-border-sm me-2 text-success" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <span class="text-success">🌾 يفكر في إجابتك الزراعية...</span>
                </div>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Utility functions
function formatCurrency(amount, currency = 'TND') {
    return new Intl.NumberFormat('en-TN', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(new Date(date));
}

function formatDateTime(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(date));
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Image preview
function previewImage(input, previewId) {
    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById(previewId);
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
        };
        reader.readAsDataURL(file);
    }
}

// Confirmation dialogs
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Loading states
function showLoading(element) {
    element.disabled = true;
    element.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
}

function hideLoading(element, originalText) {
    element.disabled = false;
    element.innerHTML = originalText;
}

// Toast notifications
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// API helper functions
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        showToast('An error occurred. Please try again.', 'danger');
        throw error;
    }
}

// Local storage helpers
function saveToLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
        console.error('Error saving to localStorage:', error);
    }
}

function getFromLocalStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
        console.error('Error reading from localStorage:', error);
        return defaultValue;
    }
}

// Export functions for global use
window.AgriConnect = {
    setLanguage,
    sendMessage,
    formatCurrency,
    formatDate,
    formatDateTime,
    validateForm,
    previewImage,
    confirmAction,
    showLoading,
    hideLoading,
    showToast,
    apiRequest,
    saveToLocalStorage,
    getFromLocalStorage
};
