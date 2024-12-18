document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');
    const helpButton = document.getElementById('helpButton');
    const chatGuide = document.querySelector('.chat-guide');
    const closeChatGuide = document.getElementById('closeChatGuide'); // 헤더 영역에 배치한 X 버튼
    const profileSection = document.getElementById('profileSection');
    const userId = document.getElementById('userId');

    // 필수 요소 확인
    if (!helpButton || !chatInput || !sendButton || !chatMessages || !chatGuide || !closeChatGuide) {
        console.error('필요한 요소를 찾을 수 없습니다.');
        return;
    }

    let isGuideVisible = false;

    helpButton.addEventListener('click', function() {
        isGuideVisible = !isGuideVisible;
        
        if (isGuideVisible) {
            chatGuide.style.display = 'flex';
            setTimeout(() => {
                chatGuide.style.opacity = '1';
            }, 10);
        } else {
            chatGuide.style.opacity = '0';
            setTimeout(() => {
                chatGuide.style.display = 'none';
            }, 300);
        }
    });

    closeChatGuide.addEventListener('click', function() {
        // X 버튼 클릭 시 가이드 닫기
        isGuideVisible = false;
        chatGuide.style.opacity = '0';
        setTimeout(() => {
            chatGuide.style.display = 'none';
        }, 300);
    });

    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;
    
        addMessage('user', message);
        chatInput.value = '';
    
        fetch('/api/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            if (data.response) {
                const formattedResponse = data.response.replace(/\n/g, '<br>');
                addMessage('bot', formattedResponse);
            } else {
                addMessage('bot', '죄송합니다. 응답을 받지 못했습니다.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('bot', '죄송합니다. 오류가 발생했습니다.');
        });
    }

    function addMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        if (type === 'bot') {
            const botWrapper = document.createElement('div');
            botWrapper.className = 'bot-message-wrapper';
            
            const avatar = document.createElement('div');
            avatar.className = 'bot-avatar';
            avatar.innerHTML = '<i class="fas fa-robot"></i>';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.innerHTML = content;
            
            botWrapper.appendChild(avatar);
            botWrapper.appendChild(contentDiv);
            messageDiv.appendChild(botWrapper);
        } else {
            messageDiv.innerHTML = content;
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    let isExpanded = false;

    profileSection.addEventListener('click', function(e) {
        if (e.target.closest('.profile-btn')) {
            return;
        }

        isExpanded = !isExpanded;
        this.classList.toggle('expanded', isExpanded);

        if (userId) {
            userId.style.display = isExpanded ? 'block' : 'none';
        }
    });

    document.addEventListener('click', function(e) {
        if (!profileSection.contains(e.target) && isExpanded) {
            isExpanded = false;
            profileSection.classList.remove('expanded');
            if (userId) userId.style.display = 'none';
        }
    });

    function updateSidebarNews() {
        const newsList = document.getElementById('newsList');
        if (!newsList) {
            console.error('newsList element not found');
            return;
        }
    
        newsList.innerHTML = '<div class="loading">뉴스를 불러오는 중...</div>';
    
        fetch('/api/google-news/')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success && data.news) {
                    newsList.innerHTML = data.news.map(item => `
                        <div class="news-item">
                            <a href="${item.link}" target="_blank">
                                <span class="news-title">${item.title}</span>
                                <div class="news-meta">
                                    <span class="news-date">${item.pubDate}</span>
                                </div>
                            </a>
                        </div>
                    `).join('');
                } else {
                    throw new Error('Invalid news data format');
                }
            })
            .catch(error => {
                console.error('Error fetching news:', error);
                newsList.innerHTML = `<div class="error">뉴스를 불러오는데 실패했습니다.</div>`;
            });
    }
    
    updateSidebarNews();
    setInterval(updateSidebarNews, 300000);
});

function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return '';
}