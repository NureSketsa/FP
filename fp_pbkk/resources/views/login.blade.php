<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>LearnVid AI - Register</title>
  <link href="https://fonts.googleapis.com/css2?family=Montaga&display=swap" rel="stylesheet"/>
  <script src="https://cdn.lordicon.com/lordicon.js"></script>
  <style>
    body {
      font-family: 'Montaga', serif;
      background: linear-gradient(135deg, #112D4E 0%, #1a3f63 100%);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      position: relative;
    }

    .bg-animations {
      position: absolute;
      inset: 0;
      pointer-events: none;
      z-index: 1;
    }

    .floating-symbol {
      position: absolute;
      font-family: 'Montaga', serif;
      font-weight: bold;
      opacity: 0;
      will-change: transform, opacity;
      filter: drop-shadow(0 0 4px rgba(255,255,255,0.4));
    }

    @keyframes floatRandom {
      0% {
        opacity: 0;
        transform: translate(var(--xStart), var(--yStart)) scale(var(--scaleStart)) rotate(var(--rotateStart));
      }
      15% { opacity: var(--maxOpacity); }
      50% {
        transform: translate(var(--xMid), var(--yMid)) scale(var(--scaleMid)) rotate(var(--rotateMid));
      }
      85% { opacity: var(--maxOpacity); }
      100% {
        opacity: 0;
        transform: translate(var(--xEnd), var(--yEnd)) scale(var(--scaleEnd)) rotate(var(--rotateEnd));
      }
    }

    .register-container {
      background: rgba(249, 247, 247, 0.95);
      backdrop-filter: blur(20px);
      border-radius: 24px;
      padding: 40px;
      box-shadow: 0 20px 60px rgba(17, 45, 78, 0.3);
      width: 100%;
      max-width: 420px;
      text-align: center;
      position: relative;
      z-index: 10;
      animation: slideUp 0.8s ease-out;
      margin-top: 60px;
    }

    @keyframes slideUp {
      from { opacity: 0; transform: translateY(30px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .icon-container {
      position: absolute;
      top: -50px;
      left: 50%;
      transform: translateX(-50%);
      width: 100px;
      height: 100px;
      background: #3F72AF;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 8px 25px rgba(63, 114, 175, 0.3);
    }

    .register-title {
      color: #112D4E;
      font-size: 1.8rem;
      margin: 20px 0 30px;
    }

    .form-group {
      margin-bottom: 20px;
      text-align: left;
    }

    .form-label {
      display: block;
      color: #112D4E;
      font-size: 14px;
      margin-bottom: 6px;
      font-weight: 500;
    }

    .required {
      color: #e74c3c;
    }

    .form-input {
      width: 100%;
      padding: 14px 16px;
      border: 2px solid #DBE2EF;
      border-radius: 12px;
      font-family: 'Montaga', serif;
      font-size: 14px;
      background: #F9F7F7;
      color: #112D4E;
      transition: all 0.3s ease;
      box-sizing: border-box;
      outline: none;
    }

    .form-input:focus {
      border-color: #3F72AF;
      box-shadow: 0 0 0 3px rgba(63,114,175,.1);
      transform: translateY(-2px);
    }

    .form-input.error {
      border-color: #e74c3c;
    }

    .form-input.success {
      border-color: #27ae60;
    }

    .register-btn {
      width: 100%;
      background: #3F72AF;
      color: #F9F7F7;
      padding: 16px;
      border: none;
      border-radius: 12px;
      font-size: 16px;
      font-weight: 500;
      cursor: pointer;
      margin-top: 10px;
      transition: 0.3s;
      box-sizing: border-box;
      font-family: 'Montaga', serif;
    }

    .register-btn:hover {
      background: #2d5a94;
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(63,114,175,0.3);
    }

    .login-link-container {
      margin-top: 25px;
      font-size: 14px;
      color: #112D4E;
    }

    .login-link {
      color: #3F72AF;
      font-weight: 500;
      text-decoration: none;
    }

    .login-link:hover {
      color: #2d5a94;
      text-decoration: underline;
    }
  </style>
</head>
<body>
  <div class="bg-animations"></div>

  <div class="register-container">
    <div class="icon-container">
      <script src="https://cdn.lordicon.com/lordicon.js"></script>
<lord-icon
    src="https://cdn.lordicon.com/urswgamh.json"
    trigger="loop"
    delay="500"
    stroke="bold"
    colors="primary:#f9f7f7,secondary:#f9f7f7"
    style="width:80px;height:80px">
</lord-icon>
    </div>

    <h1 class="register-title">Login</h1>

    <form id="registerForm">
      <div class="form-group">
        <label class="form-label" for="usernameEmail"><span class="required">*</span> Username/Email</label>
        <input id="usernameEmail" type="text" class="form-input" placeholder="Enter your username or email" required />
      </div>
      <div class="form-group">
        <label class="form-label" for="password"><span class="required">*</span> Password</label>
        <input id="password" type="password" class="form-input" placeholder="Enter your password" required />
      </div>
      <div style="text-align: center; margin: 15px 0;">
        <a href="#" class="login-link">Forgot Password?</a>
      </div>
      <button type="submit" class="register-btn" id="registerBtn">Login</button>
    </form>

    <div class="login-link-container">
      don't have an account? <a href="{{ url('/register') }}" class="login-link">Register</a>
    </div>
  </div>

  <script>
    const container = document.querySelector('.bg-animations');
    const symbols = [
      'π','∑','√','∞','△','∫','α','β','θ','μ','∇','≠','≤','≥','∪','∩','∅','±','×','÷','²','³','∠','⊥','∥','φ','ψ','ω'
    ];
    const colors = [
      'rgba(255,255,255,0.3)',
      'rgba(173,216,230,0.35)',
      'rgba(144,238,144,0.35)',
      'rgba(255,182,193,0.35)',
      'rgba(221,160,221,0.35)',
    ];

    function spawnSymbol() {
      const el = document.createElement('div');
      el.className = 'floating-symbol';
      el.textContent = symbols[Math.floor(Math.random() * symbols.length)];
      el.style.fontSize = (1 + Math.random() * 2.5) + 'rem';
      el.style.color = colors[Math.floor(Math.random() * colors.length)];

      // Random start position
      const startX = Math.random() * 100;
      const startY = 100 + Math.random() * 20; // start below screen

      // Mid + end drift
      const driftX = startX + (Math.random() * 40 - 20);
      const driftY = startY - (30 + Math.random() * 60);
      const endX = driftX + (Math.random() * 40 - 20);
      const endY = driftY - (30 + Math.random() * 40);

      // Rotation + scale
      el.style.setProperty('--xStart', startX + 'vw');
      el.style.setProperty('--yStart', startY + 'vh');
      el.style.setProperty('--xMid', driftX + 'vw');
      el.style.setProperty('--yMid', driftY + 'vh');
      el.style.setProperty('--xEnd', endX + 'vw');
      el.style.setProperty('--yEnd', endY + 'vh');

      el.style.setProperty('--rotateStart', (Math.random()*60-30)+'deg');
      el.style.setProperty('--rotateMid', (Math.random()*80-40)+'deg');
      el.style.setProperty('--rotateEnd', (Math.random()*120-60)+'deg');

      el.style.setProperty('--scaleStart', 0.5 + Math.random()*0.3);
      el.style.setProperty('--scaleMid', 1 + Math.random()*0.2);
      el.style.setProperty('--scaleEnd', 1.2 + Math.random()*0.3);

      el.style.setProperty('--maxOpacity', 0.6 + Math.random()*0.3);

      const duration = (5 + Math.random() * 6) + 's';
      el.style.animation = `floatRandom ${duration} ease-in-out forwards`;

      // Depth effect: random z-index + opacity
      el.style.zIndex = Math.random() < 0.3 ? 1 : 2;

      container.appendChild(el);
      setTimeout(() => el.remove(), parseFloat(duration)*1000);
    }

    // Spawning loop
    setInterval(() => {
      const count = 1 + Math.floor(Math.random()*3);
      for (let i=0;i<count;i++) spawnSymbol();
    }, 700);

    // Form validation
    document.getElementById('registerForm').addEventListener('submit', function(e) {
      e.preventDefault();
      const btn = document.getElementById('registerBtn');
      const usernameEmail = document.getElementById('usernameEmail');
      const password = document.getElementById('password');
      let valid = true;
      [usernameEmail, password].forEach(i => i.classList.remove('error','success'));
      if (usernameEmail.value.length < 3) { usernameEmail.classList.add('error'); valid = false; } else usernameEmail.classList.add('success');
      if (password.value.length < 6) { password.classList.add('error'); valid = false; } else password.classList.add('success');
      if (valid) {
        btn.textContent = 'Logging in...'; btn.disabled = true;
        setTimeout(()=>{ btn.textContent='Login Successful!'; btn.style.background='#27ae60';
          setTimeout(()=>{ btn.textContent='Login'; btn.style.background='#3F72AF'; btn.disabled=false; this.reset(); [usernameEmail, password].forEach(i=>i.classList.remove('error','success')); },2000);
        },2000);
      }
    });
  </script>
</body>
</html>
