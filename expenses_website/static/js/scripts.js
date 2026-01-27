document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('bd-theme');
    const html = document.documentElement;

    // Встановлюємо тему з localStorage при завантаженні
    const savedTheme = localStorage.getItem('theme') || 'light';
    html.setAttribute('data-bs-theme', savedTheme);

    themeToggle.addEventListener('click', () => {
        const currentTheme = html.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        html.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });
});