// 날짜 포맷팅 유틸리티 함수
window.formatDate = function(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}.${month}.${day}`;
};

// 뉴스 제목 파싱 함수
function parseNewsTitle(title) {
    const separators = /\s*[|\-–—]\s*(?=[^|\-–—]*$)/;
    const parts = title.split(separators);
    
    return parts.length > 1 
        ? {
            title: parts[0].trim(),
            publisher: parts[parts.length - 1].trim()
        }
        : {
            title: title,
            publisher: 'Google News'
        };
}

// 뉴스 로딩 및 렌더링 함수
function loadGoogleNews(container = '#newsList', isSidebar = true) {
    const newsContainer = document.querySelector(container);
    if (!newsContainer) {
        console.error('뉴스 컨테이너를 찾을 수 없습니다.');
        return;
    }

    // 로딩 상태 표시
    newsContainer.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i> 보도자료를 불러오는 중...
        </div>
    `;

    fetch('/api/google-news/')
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (!data.success || !data.news || !data.news.length) {
                newsContainer.innerHTML = '<div class="no-data">등록된 보도자료가 없습니다.</div>';
                return;
            }

            if (isSidebar) {
                renderSidebarNews(newsContainer, data.news);
            }
        })
        .catch(error => {
            console.error('Error fetching news:', error);
            newsContainer.innerHTML = '<div class="error">뉴스를 불러오는데 실패했습니다.</div>';
        });
}

// 사이드바 뉴스 렌더링 함수
function renderSidebarNews(container, newsData) {
    const newsItems = newsData.slice(0, 3); // 최대 4개 항목만 표시
    const newsHTML = newsItems.map(news => {
        const parsedTitle = parseNewsTitle(news.title);
        return `
            <div class="news-item">
                <a href="${news.link}" target="_blank">
                    <span class="news-title">${parsedTitle.title}</span>
                    <div class="news-meta">
                        <span class="news-date">${window.formatDate(news.pubDate)}</span>
                        <span class="news-publisher">${parsedTitle.publisher}</span>
                    </div>
                </a>
            </div>
        `;
    }).join('');

    container.innerHTML = newsHTML;
}

// 초기화 및 자동 업데이트 설정
document.addEventListener('DOMContentLoaded', function() {
    const sidebarContainer = document.querySelector('#newsList');
    if (sidebarContainer) {
        console.log('사이드바 뉴스 로드 시작');
        loadGoogleNews('#newsList', true);
        
        // 5분마다 자동 업데이트
        setInterval(() => {
            loadGoogleNews('#newsList', true);
        }, 300000);
    }
});