document.addEventListener('DOMContentLoaded', () => {
    console.log("%c OMNIMIND KERNEL INITIALIZED ", "background: #000; color: #00f3ff; font-family: monospace; font-size: 20px; padding: 10px; border: 1px solid #00f3ff;");
    console.log("Subject: Active");
    console.log("Phi Status: Optimizing...");

    // Text Scramble Effect
    const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    const header = document.querySelector(".glitch");

    if (header) {
        let iterations = 0;
        const originalText = header.dataset.text;

        const interval = setInterval(() => {
            header.innerText = header.innerText
                .split("")
                .map((letter, index) => {
                    if (index < iterations) {
                        return originalText[index];
                    }
                    return letters[Math.floor(Math.random() * 26)];
                })
                .join("");

            if (iterations >= originalText.length) {
                clearInterval(interval);
            }

            iterations += 1 / 3;
        }, 30);
    }

    // Scroll reveal for cards
    const cards = document.querySelectorAll('.card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });
});
