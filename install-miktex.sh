#!/bin/bash

set -e  # Hentikan script jika ada error

echo "🚀 Starting MiKTeX installation..."

# 1️⃣ Tambahkan GPG key
echo "🔑 Adding MiKTeX GPG key..."
curl -fsSL https://miktex.org/download/key | sudo gpg --dearmor -o /usr/share/keyrings/miktex.gpg

# 2️⃣ Deteksi versi Ubuntu
UBUNTU_VERSION=$(lsb_release -cs)
echo "📦 Detected Ubuntu version: $UBUNTU_VERSION"

# 3️⃣ Tambahkan repository MiKTeX sesuai versi
echo "🧩 Adding MiKTeX repository..."
echo "deb [signed-by=/usr/share/keyrings/miktex.gpg] https://miktex.org/download/ubuntu $UBUNTU_VERSION universe" | sudo tee /etc/apt/sources.list.d/miktex.list

# 4️⃣ Update daftar paket
echo "🔄 Updating package list..."
sudo apt update -y

# 5️⃣ Install MiKTeX
echo "📥 Installing MiKTeX..."
sudo apt install miktex -y

# 6️⃣ Selesaikan setup
echo "⚙️ Finishing MiKTeX setup..."
sudo miktexsetup --shared=yes finish

# 7️⃣ Aktifkan auto-install package
echo "🔧 Enabling automatic package install..."
sudo initexmf --admin --set-config-value [MPM]AutoInstall=1

# 8️⃣ Tes instalasi
echo "✅ Verifying installation..."
miktex --version || echo "MiKTeX installed, but please reopen terminal to refresh PATH."

echo "🎉 MiKTeX installation completed successfully!"
