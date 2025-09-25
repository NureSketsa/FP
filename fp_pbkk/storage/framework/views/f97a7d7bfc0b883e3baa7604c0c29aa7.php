<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LearnVid AI</title>
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
            background: linear-gradient(135deg, #112D4E 0%, #1a3f63 100%);
            color: #F9F7F7;
            overflow-x: hidden;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        /* Navigation */
        nav {
            padding: 20px 0;
            position: relative;
            z-index: 100;
        }

        .nav-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .nav-links {
            display: flex;
            gap: 40px;
            list-style: none;
        }

        .nav-links a {
            color: #DBE2EF;
            text-decoration: none;
            font-size: 16px;
            transition: color 0.3s ease;
        }

        .nav-links a:hover {
            color: #F9F7F7;
        }

        .nav-buttons {
            display: flex;
            gap: 20px;
            align-items: center;
        }

        .register-btn {
            background: #F9F7F7;
            color: #112D4E;
            padding: 12px 24px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            border: 2px solid #F9F7F7;
        }

        .register-btn:hover {
            background: transparent;
            color: #F9F7F7;
        }

        .login-link {
            color: #DBE2EF;
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .login-link:hover {
            color: #F9F7F7;
        }

        /* Hero Section */
        .hero {
            text-align: center;
            padding: 120px 0 80px;
            position: relative;
            z-index: 10;
        }

        .hero h1 {
            font-family: 'Costaline', cursive;
            font-size: 4.5rem;
            font-weight: 400;
            margin-bottom: 30px;
            background: linear-gradient(45deg, #F9F7F7, #DBE2EF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .hero p {
            font-size: 1.2rem;
            color: #DBE2EF;
            max-width: 600px;
            margin: 0 auto 50px;
            line-height: 1.6;
        }

        .start-btn {
            background: #3F72AF;
            color: #F9F7F7;
            padding: 16px 32px;
            border-radius: 30px;
            text-decoration: none;
            font-size: 18px;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            transition: all 0.3s ease;
            border: 2px solid #3F72AF;
            position: relative;
            overflow: hidden;
        }

        .start-btn:before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }

        .start-btn:hover:before {
            left: 100%;
        }

        .start-btn:hover {
            background: #2d5a94;
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(63, 114, 175, 0.3);
        }

        .start-icon {
            width: 20px;
            height: 20px;
        }

        /* Animated Boxes */
        .animated-section {
            padding: 60px 0 40px;
            position: relative;
            overflow: hidden;
        }

        .boxes-container {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            white-space: nowrap;
            width: max-content;
        }

        .animated-box {
            min-width: 280px;
            height: 100px;
            background: rgba(249, 247, 247, 0.1);
            border-radius: 12px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(219, 226, 239, 0.2);
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            flex-shrink: 0;
        }

        .animated-box:hover {
            background: rgba(63, 114, 175, 0.2);
            border-color: rgba(63, 114, 175, 0.4);
            transform: translateY(-2px);
        }

        .box-text {
            color: #DBE2EF;
            font-size: 14px;
            line-height: 1.4;
            white-space: normal;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
        }

        .box-row-1 {
            animation: slideLeft 60s linear infinite;
        }

        .box-row-2 {
            animation: slideRight 70s linear infinite;
        }

        .box-row-3 {
            animation: slideLeft 80s linear infinite;
        }

        @keyframes slideLeft {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }

        @keyframes slideRight {
            0% { transform: translateX(-50%); }
            100% { transform: translateX(0); }
        }

        /* Floating elements */
        .floating-element {
            position: absolute;
            width: 60px;
            height: 60px;
            background: rgba(63, 114, 175, 0.1);
            border-radius: 50%;
            animation: float 6s ease-in-out infinite;
        }

        .floating-element:nth-child(1) {
            top: 20%;
            left: 10%;
            animation-delay: 0s;
        }

        .floating-element:nth-child(2) {
            top: 60%;
            right: 15%;
            animation-delay: 2s;
        }

        .floating-element:nth-child(3) {
            bottom: 30%;
            left: 20%;
            animation-delay: 4s;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .nav-links {
                display: none;
            }

            .hero h1 {
                font-size: 3rem;
            }

            .hero p {
                font-size: 1rem;
                padding: 0 20px;
            }

            .animated-box {
                min-width: 220px;
                height: 90px;
                padding: 15px;
            }

            .box-text {
                font-size: 13px;
            }
        }

        @media (max-width: 480px) {
            .hero h1 {
                font-size: 2.5rem;
            }

            .animated-box {
                min-width: 200px;
                height: 80px;
                padding: 12px;
            }

            .box-text {
                font-size: 12px;
            }
        }
    </style>
</head>
<body>
    <!-- Floating Elements -->
    <div class="floating-element"></div>
    <div class="floating-element"></div>
    <div class="floating-element"></div>

    <!-- Navigation -->
    <nav>
        <div class="container">
            <div class="nav-container">
                <ul class="nav-links">
                    <li><a href="#home">Home</a></li>
                    <li><a href="#features">Features</a></li>
                    <li><a href="#gallery">Gallery</a></li>
                    <li><a href="#how-it-works">How it works</a></li>
                    <li><a href="#faq">FAQ</a></li>
                </ul>
                <div class="nav-buttons">
                    <a href="#register" class="register-btn">Register</a>
                    <a href="#login" class="login-link">Log in</a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <h1>LearnVid AI</h1>
            <p>From lesson plans to learning videos instantly created with AI. Learning has never been this easy.</p>
            <a href="#start" class="start-btn">
                <svg class="start-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
                Start Now
            </a>
        </div>
    </section>

    <!-- Animated Boxes Section -->
    <section class="animated-section">
        <div class="container">
            <!-- Row 1 - Moving Left -->
            <div class="boxes-container box-row-1">
                <div class="animated-box">
                    <div class="box-text">Create a comprehensive lesson plan for teaching fractions to 4th graders</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Help me understand photosynthesis with an engaging video script</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Generate quiz questions about World War II for high school students</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Create an interactive timeline of the American Revolution</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Design a fun way to teach multiplication tables to kids</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Explain climate change in simple terms for middle schoolers</div>
                </div>
                <!-- Duplicate content for seamless loop -->
                <div class="animated-box">
                    <div class="box-text">Create a comprehensive lesson plan for teaching fractions to 4th graders</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Help me understand photosynthesis with an engaging video script</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Generate quiz questions about World War II for high school students</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Create an interactive timeline of the American Revolution</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Design a fun way to teach multiplication tables to kids</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Explain climate change in simple terms for middle schoolers</div>
                </div>
            </div>

            <!-- Row 2 - Moving Right -->
            <div class="boxes-container box-row-2">
                <div class="animated-box">
                    <div class="box-text">Write a Python tutorial for absolute beginners step by step</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Create flashcards for learning Spanish vocabulary effectively</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Develop a chemistry lab experiment about chemical reactions</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Make geometry fun with real-world application examples</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Design a literature analysis worksheet for Romeo and Juliet</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Create an engaging presentation about the solar system</div>
                </div>
                <!-- Duplicate content for seamless loop -->
                <div class="animated-box">
                    <div class="box-text">Write a Python tutorial for absolute beginners step by step</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Create flashcards for learning Spanish vocabulary effectively</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Develop a chemistry lab experiment about chemical reactions</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Make geometry fun with real-world application examples</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Design a literature analysis worksheet for Romeo and Juliet</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Create an engaging presentation about the solar system</div>
                </div>
            </div>

            <!-- Row 3 - Moving Left -->
            <div class="boxes-container box-row-3">
                <div class="animated-box">
                    <div class="box-text">Explain calculus concepts using visual learning techniques</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Generate practice problems for algebra with detailed solutions</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Create a biology study guide for cellular respiration</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Design interactive exercises for learning English grammar</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Make history come alive with storytelling techniques</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Create art projects that teach color theory to students</div>
                </div>
                <!-- Duplicate content for seamless loop -->
                <div class="animated-box">
                    <div class="box-text">Explain calculus concepts using visual learning techniques</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Generate practice problems for algebra with detailed solutions</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Create a biology study guide for cellular respiration</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Design interactive exercises for learning English grammar</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Make history come alive with storytelling techniques</div>
                </div>
                <div class="animated-box">
                    <div class="box-text">Create art projects that teach color theory to students</div>
                </div>
            </div>
        </div>
    </section>

    <script>
        // Add some interactive effects
        document.addEventListener('DOMContentLoaded', function() {
            const boxes = document.querySelectorAll('.animated-box');

            // Add hover effect and pause animation on hover
            boxes.forEach((box, index) => {
                box.addEventListener('mouseenter', function() {
                    this.style.animationPlayState = 'paused';
                    const container = this.parentElement;
                    container.style.animationPlayState = 'paused';
                });

                box.addEventListener('mouseleave', function() {
                    this.style.animationPlayState = 'running';
                    const container = this.parentElement;
                    container.style.animationPlayState = 'running';
                });

                // Add click effect
                box.addEventListener('click', function() {
                    this.style.transform = 'scale(0.98)';
                    setTimeout(() => {
                        this.style.transform = '';
                    }, 150);
                });
            });

            // Add smooth scroll for navigation links
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth'
                        });
                    }
                });
            });
        });
    </script>
</body>
</html>
<?php /**PATH D:\Naufal\ITS\SEMESTER 5\Pemrograman Berbasis Kerangka Kerja\FP_PBKK\FP\fp_pbkk\resources\views/main.blade.php ENDPATH**/ ?>