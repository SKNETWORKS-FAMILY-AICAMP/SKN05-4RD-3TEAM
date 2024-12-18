window.formatDate = function(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}.${month}.${day}`;
};

// 뉴스 제목을 구분자 기준으로 나누는 함수
function parseNewsTitle(title) {
    const separators = /\s*[|\-–—]\s*(?=[^|\-–—]*$)/; // 다양한 구분자 처리
    const parts = title.split(separators);
    
    if (parts.length > 1) {
        return {
            title: parts[0].trim(),
            publisher: parts[parts.length - 1].trim()
        };
    }
    
    return {
        title: title,
        publisher: 'Google News' // 구분자가 없을 경우 기본 값
    };
}

function loadGoogleNews(container = '#newsList', isSidebar = true) {
    const newsContainer = document.querySelector(container);
    if (!newsContainer) {
        console.error('뉴스 컨테이너를 찾을 수 없습니다.');
        return;
    }

    // 로딩 표시
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
                const newsItems = data.news.slice(0, 4);
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

                newsContainer.innerHTML = newsHTML;
            }
        })
        .catch(error => {
            console.error('Error fetching news:', error);
            newsContainer.innerHTML = '<div class="error">뉴스를 불러오는데 실패했습니다.</div>';
        });
}

document.addEventListener('DOMContentLoaded', function () {
    // 사이드바 뉴스만 로드
    const sidebarContainer = document.querySelector('#newsList');
    if (sidebarContainer) {
        console.log('사이드바 뉴스 로드 시도');
        loadGoogleNews('#newsList', true);
    }


    // 5분마다 자동 업데이트
    setInterval(() => {
        if (sidebarContainer) loadGoogleNews('#newsList', true);
    }, 300000);
});