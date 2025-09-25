<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LearnVid AI - Chat</title>
    <link href="https://fonts.googleapis.com/css2?family=Montaga&display=swap" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Costaline:wght@400&display=swap');

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Montaga', serif;
            background: #F9F7F7;
            color: #112D4E;
            height: 100vh;
            overflow: hidden;
        }

        .container {
            display: flex;
            height: 100vh;
        }

        /* Sidebar */
        .sidebar {
            width: 260px;
            background: #112D4E;
            color: #F9F7F7;
            display: flex;
            flex-direction: column;
            border-right: 1px solid rgba(219, 226, 239, 0.1);
        }

        .sidebar-header {
            padding: 16px 12px;
        }

        .new-chat-btn {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 12px;
            background: transparent;
            border: 1px solid rgba(219, 226, 239, 0.2);
            border-radius: 8px;
            color: #F9F7F7;
            cursor: pointer;
            transition: all 0.2s ease;
            font-family: 'Montaga', serif;
            font-size: 14px;
            width: 100%;
        }

        .new-chat-btn:hover {
            background: rgba(219, 226, 239, 0.1);
        }

        .new-chat-btn svg {
            width: 16px;
            height: 16px;
        }

        .sidebar-menu {
            padding: 8px 12px;
            flex: 1;
            overflow-y: auto;
        }

        .menu-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 12px;
            color: #DBE2EF;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 14px;
            margin-bottom: 2px;
        }

        .menu-item:hover {
            background: rgba(219, 226, 239, 0.1);
        }

        .menu-item svg {
            width: 16px;
            height: 16px;
        }

        .chats-section {
            margin-top: 20px;
        }

        .chats-title {
            color: #DBE2EF;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
            padding: 0 12px;
            opacity: 0.7;
        }

        .chat-item {
            padding: 8px 12px;
            color: #DBE2EF;
            border-radius: 6px;
            margin-bottom: 2px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 14px;
            line-height: 1.4;
            position: relative;
        }

        .chat-item:hover {
            background: rgba(219, 226, 239, 0.1);
        }

        .chat-item.active {
            background: #3F72AF;
            color: #F9F7F7;
        }

        .sidebar-footer {
            padding: 12px;
            border-top: 1px solid rgba(219, 226, 239, 0.1);
        }

        .user-info {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .user-info:hover {
            background: rgba(219, 226, 239, 0.1);
        }

        .user-avatar {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: #3F72AF;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
        }

        .username {
            color: #DBE2EF;
            font-size: 14px;
        }

        /* Main Chat Area */
        .chat-main {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #F9F7F7;
        }

        .chat-header {
            padding: 12px 16px;
            border-bottom: 1px solid rgba(17, 45, 78, 0.1);
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #F9F7F7;
        }

        .chat-title {
            font-family: 'Costaline', cursive;
            font-size: 1.1rem;
            color: #112D4E;
        }

        .chat-actions {
            display: flex;
            gap: 8px;
        }

        .action-btn {
            padding: 6px 12px;
            background: transparent;
            border: 1px solid rgba(17, 45, 78, 0.2);
            border-radius: 6px;
            color: #3F72AF;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 12px;
        }

        .action-btn:hover {
            background: rgba(63, 114, 175, 0.1);
            color: #112D4E;
        }

        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
            position: relative;
            background: #F9F7F7;
        }

        .welcome-screen {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 40px;
        }

        .welcome-screen.hidden {
            display: none;
        }

        .welcome-title {
            font-family: 'Costaline', cursive;
            font-size: 2.5rem;
            color: #112D4E;
            margin-bottom: 15px;
        }

        .welcome-subtitle {
            color: #3F72AF;
            font-size: 1.2rem;
            opacity: 0.9;
        }

        .chat-messages {
            flex: 1;
            padding: 20px;
            display: none;
            overflow-y: auto;
        }

        .message {
            margin-bottom: 24px;
            display: flex;
            align-items: flex-start;
            gap: 12px;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }

        .message.user {
            flex-direction: row-reverse;
        }

        .message-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
            flex-shrink: 0;
        }

        .message.ai .message-avatar {
            background: #3F72AF;
            color: #F9F7F7;
        }

        .message.user .message-avatar {
            background: #DBE2EF;
            color: #112D4E;
        }

        .message-content {
            max-width: 70%;
            padding: 16px 20px;
            border-radius: 18px;
            font-size: 14px;
            line-height: 1.5;
            position: relative;
        }

        .message.ai .message-content {
            background: #3F72AF;
            color: #F9F7F7;
            border-bottom-left-radius: 6px;
        }

        .message.user .message-content {
            background: #DBE2EF;
            color: #112D4E;
            border-bottom-right-radius: 6px;
        }

        /* Input Area */
        .input-area {
            padding: 20px;
            background: #F9F7F7;
        }

        .input-container {
            max-width: 800px;
            margin: 0 auto;
            position: relative;
            background: #F9F7F7;
            border-radius: 24px;
            border: 2px solid #DBE2EF;
            display: flex;
            align-items: flex-end;
            min-height: 52px;
            transition: all 0.3s ease;
        }

        .input-container:focus-within {
            border-color: #3F72AF;
            box-shadow: 0 0 0 3px rgba(63, 114, 175, 0.1);
        }

        .upload-btn {
            padding: 12px;
            background: transparent;
            border: none;
            cursor: pointer;
            color: #3F72AF;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            margin: 4px;
            transition: all 0.2s ease;
            position: relative;
        }

        .upload-btn:hover {
            background: rgba(63, 114, 175, 0.1);
            color: #112D4E;
        }

        .upload-btn svg {
            width: 20px;
            height: 20px;
        }

        .upload-dropdown {
            position: absolute;
            bottom: 100%;
            left: 0;
            margin-bottom: 8px;
            background: #F9F7F7;
            border: 2px solid #DBE2EF;
            border-radius: 8px;
            min-width: 200px;
            display: none;
            z-index: 1000;
            box-shadow: 0 4px 20px rgba(17, 45, 78, 0.1);
        }

        .upload-dropdown.show {
            display: block;
        }

        .upload-option {
            padding: 12px 16px;
            color: #112D4E;
            cursor: pointer;
            transition: all 0.2s ease;
            border-bottom: 1px solid #DBE2EF;
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 14px;
        }

        .upload-option:last-child {
            border-bottom: none;
        }

        .upload-option:hover {
            background: rgba(63, 114, 175, 0.1);
            color: #112D4E;
        }

        .upload-option svg {
            width: 16px;
            height: 16px;
            color: #3F72AF;
        }

        .message-input {
            flex: 1;
            padding: 12px 16px;
            border: none;
            background: transparent;
            font-family: 'Montaga', serif;
            font-size: 15px;
            color: #112D4E;
            outline: none;
            resize: none;
            min-height: 24px;
            max-height: 120px;
            line-height: 1.5;
        }

        .message-input::placeholder {
            color: #3F72AF;
            opacity: 0.7;
        }

        .send-button {
            padding: 12px;
            background: transparent;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            margin: 4px;
            transition: all 0.2s ease;
        }

        .send-button:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }

        .send-button:not(:disabled):hover {
            background: rgba(63, 114, 175, 0.1);
        }

        .send-button svg {
            width: 20px;
            height: 20px;
            color: #3F72AF;
        }

        .send-button:not(:disabled) svg {
            color: #3F72AF;
        }

        /* File upload hidden input */
        .file-input {
            display: none;
        }

        /* Mobile Responsiveness */
        @media (max-width: 768px) {
            .sidebar {
                width: 240px;
            }

            .welcome-title {
                font-size: 1.5rem;
            }

            .input-area {
                padding: 16px;
            }

            .chat-messages {
                padding: 16px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="sidebar-header">
                <button class="new-chat-btn" id="new-chat-btn">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M12 4.5v15m7.5-7.5h-15"/>
                    </svg>
                    New chat
                </button>
            </div>

            <div class="sidebar-menu">
                <div class="menu-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"/>
                    </svg>
                    Search chats
                </div>

                <div class="menu-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
                    </svg>
                    Library
                </div>

                <div class="chats-section">
                    <div class="chats-title">Today</div>
                    <div class="chat-item active">Landing page design</div>
                    <div class="chat-item">AI education video names</div>
                    <div class="chat-item">Kids' art ideas</div>
                    <div class="chat-item">New chat</div>
                </div>
            </div>

            <div class="sidebar-footer">
                <div class="user-info">
                    <div class="user-avatar">U</div>
                    <div class="username">Username</div>
                </div>
            </div>
        </div>

        <!-- Main Chat Area -->
        <div class="chat-main">
            <div class="chat-header">
                <div class="chat-title">LearnVid AI</div>
                <div class="chat-actions">
                    <button class="action-btn">Share</button>
                    <button class="action-btn">⋯</button>
                </div>
            </div>

            <div class="chat-container">
                <!-- Welcome Screen -->
                <div class="welcome-screen" id="welcome-screen">
                    <h1 class="welcome-title">Welcome, User!</h1>
                    <p class="welcome-subtitle">What should we learn today?</p>
                </div>

                <!-- Chat Messages -->
                <div class="chat-messages" id="chat-messages">
                    <!-- Messages will be dynamically added here -->
                </div>
            </div>

            <!-- Input Area -->
            <div class="input-area">
                <div class="input-container">
                    <div class="upload-btn" id="upload-btn">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M12 4.5v15m7.5-7.5h-15"/>
                        </svg>
                        <div class="upload-dropdown" id="upload-dropdown">
                            <div class="upload-option" onclick="triggerFileUpload('image')">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                                    <circle cx="9" cy="9" r="2"/>
                                    <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>
                                </svg>
                                Upload Image
                            </div>
                            <div class="upload-option" onclick="triggerFileUpload('document')">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                    <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                                    <polyline points="14,2 14,8 20,8"/>
                                </svg>
                                Upload Document
                            </div>
                            <div class="upload-option" onclick="triggerFileUpload('video')">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                    <polygon points="23 7 16 12 23 17 23 7"/>
                                    <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
                                </svg>
                                Upload Video
                            </div>
                        </div>
                    </div>

                    <textarea class="message-input" id="message-input" placeholder="Ask anything" rows="1"></textarea>

                    <button class="send-button" id="send-button" disabled>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M22 2L11 13"/>
                            <path d="M22 2l-7 20-4-9-9-4 20-7z"/>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Hidden file inputs -->
    <input type="file" id="image-upload" class="file-input" accept="image/*">
    <input type="file" id="document-upload" class="file-input" accept=".pdf,.doc,.docx,.txt">
    <input type="file" id="video-upload" class="file-input" accept="video/*">

    <script>
        const messageInput = document.getElementById('message-input');
        const sendButton = document.getElementById('send-button');
        const chatMessages = document.getElementById('chat-messages');
        const welcomeScreen = document.getElementById('welcome-screen');
        const newChatBtn = document.getElementById('new-chat-btn');
        const uploadBtn = document.getElementById('upload-btn');
        const uploadDropdown = document.getElementById('upload-dropdown');

        let chatStarted = false;

        // Auto-resize textarea
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';

            // Enable/disable send button
            sendButton.disabled = !this.value.trim();
        });

        // Upload dropdown toggle
        uploadBtn.addEventListener('click', function() {
            uploadDropdown.classList.toggle('show');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!uploadBtn.contains(e.target) && !uploadDropdown.contains(e.target)) {
                uploadDropdown.classList.remove('show');
            }
        });

        // File upload functions
        function triggerFileUpload(type) {
            const fileInput = document.getElementById(type + '-upload');
            fileInput.click();
            uploadDropdown.classList.remove('show');
        }

        // Handle file uploads
        ['image', 'document', 'video'].forEach(type => {
            document.getElementById(type + '-upload').addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    addMessage(`📎 Uploaded: ${file.name}`, 'user');
                    setTimeout(() => {
                        addMessage(`I can see you've uploaded a ${type}. How can I help you with this file?`, 'ai');
                    }, 1000);
                }
            });
        });

        // Send message function
        function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;

            if (!chatStarted) {
                welcomeScreen.classList.add('hidden');
                chatMessages.style.display = 'block';
                chatStarted = true;
            }

            // Add user message
            addMessage(message, 'user');

            // Clear input
            messageInput.value = '';
            messageInput.style.height = 'auto';
            sendButton.disabled = true;

            // Simulate AI response
            setTimeout(() => {
                const responses = [
                    "I'd be happy to help you with that! Let me create some educational content for you.",
                    "That's a great question! I can help you develop learning materials around this topic.",
                    "I can assist you with creating engaging educational videos on this subject.",
                    "Let me help you design a comprehensive learning experience for this topic."
                ];
                const randomResponse = responses[Math.floor(Math.random() * responses.length)];
                addMessage(randomResponse, 'ai');
            }, 1000);
        }

        // Add message to chat
        function addMessage(text, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;

            const avatar = document.createElement('div');
            avatar.className = 'message-avatar';
            avatar.textContent = sender === 'ai' ? 'AI' : 'U';

            const content = document.createElement('div');
            content.className = 'message-content';
            content.textContent = text;

            messageDiv.appendChild(avatar);
            messageDiv.appendChild(content);

            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        // Event listeners
        sendButton.addEventListener('click', sendMessage);

        messageInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // New chat button
        newChatBtn.addEventListener('click', function(e) {
            e.preventDefault();
            chatMessages.innerHTML = '';
            chatMessages.style.display = 'none';
            welcomeScreen.classList.remove('hidden');
            chatStarted = false;
        });

        // Chat item clicks
        document.querySelectorAll('.chat-item').forEach(item => {
            item.addEventListener('click', function() {
                document.querySelectorAll('.chat-item').forEach(i => i.classList.remove('active'));
                this.classList.add('active');

                // Simulate loading a chat
                if (!chatStarted) {
                    welcomeScreen.classList.add('hidden');
                    chatMessages.style.display = 'block';
                    chatStarted = true;
                }
            });
        });
    </script>
</body>
</html>
<?php /**PATH D:\Naufal\ITS\SEMESTER 5\Pemrograman Berbasis Kerangka Kerja\FP_PBKK\FP\fp_pbkk\resources\views/chat.blade.php ENDPATH**/ ?>