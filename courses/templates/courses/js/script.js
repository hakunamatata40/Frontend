document.addEventListener('DOMContentLoaded', function() {
    // Initialize Hero Swiper
    const heroSwiper = new Swiper('.hero-swiper', {
        loop: true,
        autoplay: {
            delay: 6000,
            disableOnInteraction: false,
        },
        effect: 'fade',
        fadeEffect: {
            crossFade: true
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
            dynamicBullets: true,
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
    });

    // Initialize Subjects Swiper
    const subjectsSwiper = new Swiper('.subjects-swiper', {
        slidesPerView: 'auto',
        spaceBetween: 8,
        freeMode: true,
        mousewheel: {
            forceToAxis: true,
        },
        grabCursor: true,
        resistance: true,
        resistanceRatio: 0.7,
        breakpoints: {
            640: {
                spaceBetween: 12,
            },
            1024: {
                spaceBetween: 16,
            }
        }
    });

    // Animate elements on scroll
    const animateOnScroll = (entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    };

    const observer = new IntersectionObserver(animateOnScroll, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    // Observe course cards and other elements
    document.querySelectorAll('.course-card, .section-title, .search-container, .subjects-section').forEach(el => {
        observer.observe(el);
    });

    // Add hover effect to course images
    document.querySelectorAll('.course-card').forEach(card => {
        const img = card.querySelector('.course-image');
        if (img) {
            card.addEventListener('mouseenter', () => {
                img.style.transform = 'scale(1.05)';
            });
            card.addEventListener('mouseleave', () => {
                img.style.transform = 'scale(1)';
            });
        }
    });
});