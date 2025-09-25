<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SlothKeys - CSV Ready</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <link rel="stylesheet" href="<?php echo e(asset('css/style.css')); ?>">
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

        <p class="success-message">CSV File is ready.</p>

        <a href="#" class="download-btn" onclick="downloadFile()">Download File</a>

        <p class="backup-link" onclick="downloadFile()">Click here if download failed</p>

        <p class="description">
            An AI that skips the typing—just point to the fields, and it turns them into a ready-to-use CSV.
        </p>
    </main>

    <footer class="footer">
        <p class="footer-text">© Slothkeys 2025</p>
    </footer>

    <!-- Chat Button -->
    <button class="chat-button" onclick="toggleChat()">
        <i class="fas fa-comments"></i>
    </button>

    <!-- Chat Window -->
    <div class="chat-window" id="chatWindow">
        <div class="chat-header">
            <div class="chat-title">Chat</div>
            <button class="chat-close" onclick="toggleChat()">×</button>
        </div>

        <div class="chat-messages" id="chatMessages">
            <div class="message ai">Halo! Ada pertanyaan tentang YYY.csv?</div>
            <div class="message user">Lorem ipsum dolor</div>
        </div>

        <div class="chat-input-container">
            <input type="text" class="chat-input" id="chatInput" placeholder="Ketik pesan..." onkeypress="handleEnter(event)">
            <button class="chat-send" onclick="sendMessage()">
                <i class="fas fa-paper-plane"></i>
            </button>
        </div>
    </div>

    <script>
        function toggleChat() {
            const chatWindow = document.getElementById('chatWindow');
            const chatButton = document.querySelector('.chat-button');

            if (chatWindow.classList.contains('active')) {
                chatWindow.classList.remove('active');
                chatButton.style.display = 'flex';
            } else {
                chatWindow.classList.add('active');
                chatButton.style.display = 'none';
            }
        }

        function sendMessage() {
            const input = document.getElementById('chatInput');
            const messages = document.getElementById('chatMessages');

            if (input.value.trim()) {
                // Add user message
                const userMessage = document.createElement('div');
                userMessage.className = 'message user';
                userMessage.textContent = input.value;
                messages.appendChild(userMessage);

                // Clear input
                const messageText = input.value;
                input.value = '';

                // Scroll to bottom
                messages.scrollTop = messages.scrollHeight;

                // Simulate AI response after delay
                setTimeout(() => {
                    const aiMessage = document.createElement('div');
                    aiMessage.className = 'message ai';
                    aiMessage.textContent = getAIResponse(messageText);
                    messages.appendChild(aiMessage);
                    messages.scrollTop = messages.scrollHeight;
                }, 1000);
            }
        }

        function handleEnter(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        function getAIResponse(userMessage) {
            const responses = [
                "Terima kasih atas pertanyaan Anda! Saya akan membantu Anda dengan file CSV.",
                "Apakah ada masalah dengan download file CSV-nya?",
                "File CSV Anda sudah siap untuk digunakan. Ada yang ingin ditanyakan?",
                "Saya siap membantu Anda dengan pertanyaan seputar data dan file CSV.",
                "Bagaimana saya bisa membantu Anda lebih lanjut dengan file yang telah diproses?"
            ];
            return responses[Math.floor(Math.random() * responses.length)];
        }

        function downloadFile() {
            // Create a sample CSV content
            const csvContent = "data:text/csv;charset=utf-8,Name,Email,Phone\nJohn Doe,john@example.com,123-456-7890\nJane Smith,jane@example.com,098-765-4321";

            // Create download link
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "processed_data.csv");
            document.body.appendChild(link);

            // Trigger download
            link.click();
            document.body.removeChild(link);

            // Show success message
            alert("CSV file downloaded successfully!");
        }

        // Close chat when clicking outside
        document.addEventListener('click', function(event) {
            const chatWindow = document.getElementById('chatWindow');
            const chatButton = document.querySelector('.chat-button');

            if (chatWindow.classList.contains('active') &&
                !chatWindow.contains(event.target) &&
                !chatButton.contains(event.target)) {
                toggleChat();
            }
        });
    </script>
</body>
</html>
<?php /**PATH D:\Naufal\ITS\SEMESTER 5\Pemrograman Berbasis Kerangka Kerja\FP_PBKK\FP\fp_pbkk\resources\views/download.blade.php ENDPATH**/ ?>