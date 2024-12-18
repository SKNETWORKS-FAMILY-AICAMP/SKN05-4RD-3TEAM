document.addEventListener('DOMContentLoaded', function() {
    // 알림 메시지 자동 제거
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            alert.style.display = 'none';
        });
    }, 3000);
});