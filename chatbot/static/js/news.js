window.formatDate = function(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}.${month}.${day}`;
};

document.addEventListener('DOMContentLoaded', function() {
    function parseNewsTitle(title) {
        // 다양한 구분자 패턴 처리 ('|', '-', '–', '—' 등)
        const separators = /\s*[|\-–—]\s*(?=[^|\-–—]*$)/;
        const parts = title.split(separators);
        
        if (parts.length > 1) {
            return {
                title: parts[0].trim(),
                publisher: parts[parts.length - 1].trim()
            };
        }
        
        return {
            title: title,
            publisher: 'Google News'
        };
    }

    function loadGoogleNews() {
        const newsContainer = document.querySelector('.newsSlider');
        if (!newsContainer) {
            console.error('보도자료 컨테이너를 찾을 수 없습니다.');
            return;
        }

        newsContainer.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i>보도자료를 불러오는 중...</div>';
        
        fetch('/api/google-news/')
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                console.log('받은 데이터:', data);
                
                if (!data.success || !data.news || !data.news.length) {
                    newsContainer.innerHTML = '<div class="no-data">등록된 보도자료가 없습니다.</div>';
                    return;
                }
                
                newsContainer.innerHTML = data.news.map(news => {
                    const { title, publisher } = parseNewsTitle(news.title);
                    return `
                        <div class="item News">
                            <a href="${news.link}" target="_blank">
                                <div class="news-content">
                                    <span class="Category">보도</span>
                                    <div class="news-meta">
                                        <span class="Publisher">${publisher}</span>
                                        <span class="Separator">|</span>
                                        <span class="Day">${window.formatDate(news.pubDate)}</span>
                                    </div>
                                    <span class="Title">${title}</span>
                                </div>
                            </a>
                        </div>
                    `;
                }).join('');
            })
            .catch(error => {
                console.error('보도자료 로드 실패:', error);
                newsContainer.innerHTML = '<div class="error">보도자료를 불러오는데 실패했습니다.</div>';
            });
    }

    // 초기 로드
    loadGoogleNews();

    // 5분마다 자동 새로고침
    setInterval(loadGoogleNews, 300000);
});