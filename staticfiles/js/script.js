// static/js/script.js
document.addEventListener("DOMContentLoaded", function () {
    const themeSwitch = document.getElementById('themeSwitch');
    const darkHljsTheme = document.getElementById('hljs-dark-theme');
    const lightHljsTheme = document.getElementById('hljs-light-theme');

    // --- 主题应用函数 ---
    function applyTheme(theme) {
        if (theme === 'light-mode') {
            document.body.classList.add('light-mode');
            themeSwitch.innerHTML = '<i class="fas fa-moon"></i>';
            if (darkHljsTheme && lightHljsTheme) {
                darkHljsTheme.disabled = true;
                lightHljsTheme.disabled = false;
            }
        } else {
            document.body.classList.remove('light-mode');
            themeSwitch.innerHTML = '<i class="fas fa-sun"></i>';
            if (darkHljsTheme && lightHljsTheme) {
                darkHljsTheme.disabled = false;
                lightHljsTheme.disabled = true;
            }
        }
    }

    // --- 页面加载时初始化主题 ---
    const savedTheme = localStorage.getItem('theme') || 'dark-mode';
    applyTheme(savedTheme);

    // --- 切换按钮事件 ---
    if (themeSwitch) {
        themeSwitch.addEventListener('click', () => {
            let currentTheme = document.body.classList.contains('light-mode') ? 'light-mode' : 'dark-mode';
            let newTheme = currentTheme === 'light-mode' ? 'dark-mode' : 'light-mode';
            localStorage.setItem('theme', newTheme);
            applyTheme(newTheme);
        });
    }

    // --- 滚动加载动画 ---
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.card').forEach(card => {
        observer.observe(card);
    });

    // ===================================
    // 个人中心 "只读/编辑" 模式切换
    // ===================================
    const displayView = document.getElementById('profile-display-view');
    const editView = document.getElementById('profile-edit-view');
    const editBtn = document.getElementById('edit-profile-btn');
    const cancelBtn = document.getElementById('cancel-edit-btn');

    if (displayView && editView && editBtn && cancelBtn) {
        editBtn.addEventListener('click', function() {
            displayView.style.display = 'none';
            editView.style.display = 'block';
        });

        cancelBtn.addEventListener('click', function() {
            editView.style.display = 'none';
            displayView.style.display = 'block';
        });
    }
});