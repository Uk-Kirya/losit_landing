$(document).ready(function () {

    // =========================
    // BOOTSTRAP FORM
    // =========================

    'use strict';

    $(".phone__mask").mask("+7 (999) 999 - 99 - 99");

    var forms = document.querySelectorAll('.needs-validation');

    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // =========================
    // OWL CAROUSEL
    // =========================

    var owl = $('.carousel');

    owl.owlCarousel({
        margin: 12,
        nav: true,
        dots: false,
        autoHeight: false,
        loop: false,

        responsive: {
            0: {
                items: 1
            },
            576: {
                items: 1
            },
            768: {
                items: 2
            },
            1200: {
                items: 3
            }
        }
    });


    // =========================
    // ПЛАВНЫЙ СКРОЛЛ
    // =========================

    $("a.topLink").click(function () {

        const target = $(this).attr("href");

        $("html, body").animate({
            scrollTop: $(target).offset().top
        }, {
            duration: 0,
            easing: "swing"
        });

        return false;
    });


    // =========================
    // HEADER + MOBILE BUTTON
    // =========================

    let lastScrollTop = 0;
    let ticking = false;

    const header = document.querySelector('header');
    const mobileButton = document.querySelector('.mobile__button');

    if (header && mobileButton) {

        window.addEventListener('scroll', function () {

            if (!ticking) {

                window.requestAnimationFrame(function () {

                    const scrollTop = window.scrollY;
                    const headerHeight = header.offsetHeight;

                    if (Math.abs(lastScrollTop - scrollTop) > 5) {

                        if (
                            scrollTop > lastScrollTop &&
                            scrollTop > headerHeight
                        ) {

                            header.classList.remove('nav-down');
                            header.classList.add('nav-up');

                            mobileButton.classList.remove('mob-but-up');
                            mobileButton.classList.add('mob-but-down');

                        } else if (
                            scrollTop + window.innerHeight <
                            document.documentElement.scrollHeight
                        ) {

                            header.classList.remove('nav-up');
                            header.classList.add('nav-down');

                            mobileButton.classList.remove('mob-but-down');
                            mobileButton.classList.add('mob-but-up');
                        }

                        lastScrollTop = scrollTop;
                    }

                    ticking = false;
                });

                ticking = true;
            }

        }, {
            passive: true
        });
    }


    // =========================
    // MOBILE BUTTON
    // =========================

    const heroBlock = document.querySelector('.hero__block');
    const mobileButton2 = document.querySelector('.mobile__button');

    if (
        heroBlock &&
        mobileButton2
    ) {

        const observer = new IntersectionObserver((entries) => {

            entries.forEach((entry) => {

                if (entry.isIntersecting) {
                    mobileButton2.classList.add('hide');
                } else {
                    mobileButton2.classList.remove('hide');
                }

            });

        }, {
            threshold: 0.1
        });

        observer.observe(heroBlock);
    }


    // =========================
    // COOKIES
    // =========================

    const cookieKey = 'losit-cookie-consent';
    const cookieBanner = document.querySelector('#cookie-banner');
    const acceptCookies = document.querySelector('#accept-cookies');

    try {

        if (!window.localStorage.getItem(cookieKey)) {

            window.setTimeout(() => {

                if (cookieBanner) {
                    cookieBanner.hidden = false;
                }

            }, 1200);
        }

    } catch {

        if (cookieBanner) {
            cookieBanner.hidden = false;
        }
    }


    if (acceptCookies) {

        acceptCookies.addEventListener('click', () => {

            try {
                window.localStorage.setItem(
                    cookieKey,
                    'accepted'
                );
            } catch {}

            if (cookieBanner) {
                cookieBanner.hidden = true;
            }

        });

    }


    // =========================
    // PLYR + BOOTSTRAP MODALS
    // =========================

    document.querySelectorAll('.modal').forEach(modal => {

        const video = modal.querySelector('video');

        if (!video) return;

        const player = new Plyr(video, {

            controls: [
                'play-large',
                'play',
                'progress',
                'current-time',
                'mute',
                'volume',
                'fullscreen'
            ],

            settings: []

        });


        modal.addEventListener('hidden.bs.modal', () => {

            player.pause();
            player.currentTime = 0;

        });

    });

});