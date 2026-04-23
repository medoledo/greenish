document.addEventListener('DOMContentLoaded', function() {
    createParticles();
});

function createParticles() {
    const container = document.getElementById('particles');
    if (!container) return;
    const particleCount = 30;
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 5 + 's';
        particle.style.animationDuration = (3 + Math.random() * 4) + 's';
        particle.textContent = ['🌿', '🍃', '🌱', '💚', '♻️', '🌍'][Math.floor(Math.random() * 6)];
        container.appendChild(particle);
    }
}