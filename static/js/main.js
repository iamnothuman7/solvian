/**
 * Solvian — JavaScript Principal
 * Funcionalidades de interação: navbar, animações, loading.
 */

document.addEventListener('DOMContentLoaded', function () {

    // ========================================================================
    // NAVBAR — Scroll effect e hamburger toggle
    // ========================================================================

    const navbar = document.getElementById('navbar');
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');

    // Efeito de scroll na navbar
    if (navbar) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // Toggle do menu mobile
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function () {
            navMenu.classList.toggle('active');

            // Animar hamburger
            const hamburger = navToggle.querySelector('.hamburger');
            if (hamburger) {
                hamburger.classList.toggle('active');
            }
        });

        // Fechar menu ao clicar em um link
        navMenu.querySelectorAll('.nav-link').forEach(function (link) {
            link.addEventListener('click', function () {
                navMenu.classList.remove('active');
            });
        });
    }

    // ========================================================================
    // ANIMAÇÃO DE ENTRADA — Fade in ao aparecer na tela
    // ========================================================================

    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1,
    };

    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observar cards e seções
    document.querySelectorAll('.card, .stat-card, .kpi-card, .detail-card, .tech-card').forEach(function (el) {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        observer.observe(el);
    });

    // ========================================================================
    // FORMATAÇÃO DE NÚMEROS — Moeda e kWh
    // ========================================================================

    // Formatar valores monetários exibidos
    document.querySelectorAll('[data-format="currency"]').forEach(function (el) {
        const valor = parseFloat(el.textContent);
        if (!isNaN(valor)) {
            el.textContent = valor.toLocaleString('pt-BR', {
                style: 'currency',
                currency: 'BRL',
            });
        }
    });

    // ========================================================================
    // COORDENADAS — Auto-preenchimento com Geolocation API
    // ========================================================================

    const latInput = document.getElementById('id_latitude');
    const lonInput = document.getElementById('id_longitude');

    if (latInput && lonInput && !latInput.value && !lonInput.value) {
        // Tentar obter localização do navegador
        if ('geolocation' in navigator) {
            // Não pedir automaticamente — apenas se o campo estiver vazio
            // O usuário pode clicar no campo para ativar
            latInput.addEventListener('focus', function requestGeo() {
                if (!latInput.value) {
                    navigator.geolocation.getCurrentPosition(
                        function (pos) {
                            latInput.value = pos.coords.latitude.toFixed(4);
                            lonInput.value = pos.coords.longitude.toFixed(4);
                        },
                        function () {
                            // Silenciosamente falhar — o usuário digita manualmente
                        },
                        { timeout: 5000 }
                    );
                }
                latInput.removeEventListener('focus', requestGeo);
            });
        }
    }

    // ========================================================================
    // SMOOTH SCROLL para links âncora
    // ========================================================================

    document.querySelectorAll('a[href^="#"]').forEach(function (link) {
        link.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href').slice(1);
            const target = document.getElementById(targetId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
});
