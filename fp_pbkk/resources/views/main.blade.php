<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SlothKeys - Lazy Inputer</title>
    <link rel="stylesheet" href="{{ asset('css/style.css') }}">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap">
</head>
<body>
    <header class="header">
        <nav class="nav">
            <div class="nav-left">
                <a href="#home">Home</a>
                <a href="#saved">Saved</a>
                <a href="#help">Help</a>
                <a href="#faq">FAQ</a>
            </div>
            <div class="logo">SlothKeys</div>
            <div class="nav-right">
                <button class="register-btn">Register</button>
                <a href="#login" class="login-link">Log in</a>
            </div>
        </nav>
    </header>

    <main class="main-content">
        <h1 class="title">Lazy Inputer</h1>
        <p class="subtitle">Input your data as simple as it can be</p>

        <div class="drop-zone" id="dropZone">
            <p class="drop-text">Drop a PDF file here</p>
        </div>

        <p class="description">
            An AI that skips the typing—just point to the fields, and it turns them into a ready-to-use CSV.
        </p>
    </main>

    <footer class="footer">
        <p class="footer-text">© Slothkeys 2025</p>
    </footer>

    <script>
        // Add drag and drop functionality
        const dropZone = document.getElementById('dropZone');

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (file.type === 'application/pdf') {
                    dropZone.innerHTML = `<p class="drop-text">PDF uploaded: ${file.name}</p>`;
                } else {
                    alert('Please upload a PDF file only.');
                }
            }
        });

        // Click to upload functionality
        dropZone.addEventListener('click', () => {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'application/pdf';
            input.onchange = (e) => {
                const file = e.target.files[0];
                if (file) {
                    dropZone.innerHTML = `<p class="drop-text">PDF uploaded: ${file.name}</p>`;
                }
            };
            input.click();
        });
    </script>
</body>
</html>
