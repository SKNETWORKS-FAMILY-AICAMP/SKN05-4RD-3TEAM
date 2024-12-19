// 모달 관련 함수들
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.add('show');
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.remove('show');
}

// 모달 외부 클릭 시 닫기
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        hideModal(event.target.id);
    }
}

// 파일 선택 시 파일명 표시
document.getElementById('profile_image').addEventListener('change', function(e) {
    const fileName = e.target.files[0]?.name || '선택된 파일 없음';
    document.getElementById('selectedFile').textContent = fileName;
});

// ESC 키로 모달 닫기
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => hideModal(modal.id));
    }
});
