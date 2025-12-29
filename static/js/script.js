document.addEventListener("DOMContentLoaded", () => {
    
    // 1. Initialize Smooth Scroll (Lenis)
    const lenis = new Lenis({
        duration: 1.2,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    });
    function raf(time) {
        lenis.raf(time);
        requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    // 2. GSAP Animations
    gsap.registerPlugin(ScrollTrigger);

    // Hero Text Reveal
    gsap.utils.toArray('.reveal-text').forEach((elem, i) => {
        gsap.from(elem, {
            y: 50,
            opacity: 0,
            duration: 1,
            ease: "power3.out",
            delay: 0.2 * i
        });
    });

    // Parallax on Scroll for Hero elements
    gsap.utils.toArray(".parallax").forEach(layer => {
        const speed = layer.getAttribute('data-speed');
        gsap.to(layer, {
            y: (i, target) => ScrollTrigger.maxScroll(window) * speed,
            ease: "none",
            scrollTrigger: {
                trigger: "body",
                start: "top top",
                end: "bottom bottom",
                scrub: 0
            }
        });
    });

    // Staggered Tool Cards Entry
    document.querySelectorAll('.category-section').forEach(section => {
        gsap.from(section.querySelectorAll('.tool-card'), {
            scrollTrigger: {
                trigger: section,
                start: "top 80%",
            },
            y: 50,
            opacity: 0,
            duration: 0.8,
            stagger: 0.1,
            ease: "power2.out"
        });
    });

    // 3. File Upload Logic (Only on Tool Pages)
    const form = document.getElementById('uploadForm');
    if (form) {
        const fileInput = document.getElementById('fileInput');
        const fileList = document.getElementById('fileList');
        const dropzone = document.getElementById('dropzone');
        const loader = document.getElementById('loader');
        const result = document.getElementById('result');
        const downloadLink = document.getElementById('downloadLink');
        const convertBtn = document.getElementById('convertBtn');

        // Update File List UI
        fileInput.addEventListener('change', (e) => {
            fileList.innerHTML = '';
            fileList.classList.remove('hidden');
            
            Array.from(e.target.files).forEach(file => {
                const item = document.createElement('div');
                item.className = 'flex items-center justify-between bg-white/5 p-3 rounded-lg border border-white/10';
                item.innerHTML = `
                    <span class="text-sm truncate text-gray-300">${file.name}</span>
                    <span class="text-xs text-neon">${(file.size/1024/1024).toFixed(2)} MB</span>
                `;
                fileList.appendChild(item);
            });
        });

        // Handle Submit
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            if(!fileInput.files.length) return alert("Please select files first.");

            // UI Changes
            form.classList.add('opacity-50', 'pointer-events-none');
            loader.classList.remove('hidden');

            const formData = new FormData(form);

            try {
                const response = await fetch(`/api/process/${toolSlug}`, {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();

                loader.classList.add('hidden');
                
                if (data.success) {
                    form.classList.add('hidden');
                    result.classList.remove('hidden');
                    downloadLink.href = data.download_url;
                    
                    // Simple confetti effect for success
                    gsap.from(result, {scale: 0.8, opacity: 0, ease: "elastic.out(1, 0.3)", duration: 1});
                } else {
                    alert('Error: ' + data.error);
                    form.classList.remove('opacity-50', 'pointer-events-none');
                }
            } catch (err) {
                console.error(err);
                alert('An error occurred during upload.');
                loader.classList.add('hidden');
                form.classList.remove('opacity-50', 'pointer-events-none');
            }
        });
    }
});