<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SlothKeys - Select Data</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: "Georgia", serif;
            background: linear-gradient(135deg, #f9f7f7 0%, #dbe2ef 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* Header Navigation */
        .header {
            background-color: #3f72af;
            padding: 20px 40px;
            border-radius: 50px;
            margin: 20px 20px 0 20px;
            box-shadow: 0 4px 20px rgba(17, 45, 78, 0.2);
        }

        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }

        .nav-left {
            display: flex;
            gap: 40px;
            align-items: center;
        }

        .nav-left a {
            color: #f9f7f7;
            text-decoration: none;
            font-size: 18px;
            font-weight: 400;
            transition: color 0.3s ease;
        }

        .nav-left a:hover {
            color: #dbe2ef;
        }

        .logo {
            color: #f9f7f7;
            font-size: 32px;
            font-weight: bold;
            letter-spacing: 1px;
        }

        .nav-right {
            display: flex;
            gap: 20px;
            align-items: center;
        }

        .user-profile {
            display: flex;
            align-items: center;
            gap: 10px;
            background-color: rgba(249, 247, 247, 0.1);
            padding: 8px 20px;
            border-radius: 25px;
            transition: background-color 0.3s ease;
        }

        .user-profile:hover {
            background-color: rgba(249, 247, 247, 0.2);
        }

        .username {
            color: #f9f7f7;
            font-size: 16px;
            font-weight: 500;
        }

        .profile-pic {
            width: 35px;
            height: 35px;
            border-radius: 50%;
            background: linear-gradient(45deg, #112d4e, #3f72af);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #f9f7f7;
            font-weight: bold;
        }

        /* Main Content */
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 60px 40px;
            text-align: center;
        }

        .title {
            color: #112d4e;
            font-size: 80px;
            font-weight: bold;
            margin-bottom: 10px;
            letter-spacing: -2px;
        }

        .subtitle {
            color: #3f72af;
            font-size: 24px;
            margin-bottom: 40px;
            font-weight: 400;
        }

        .document-container {
            width: 100%;
            max-width: 800px;
            background-color: #f9f7f7;
            border: 3px solid #3f72af;
            border-radius: 15px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 8px 25px rgba(17, 45, 78, 0.1);
            text-align: left;
            line-height: 1.8;
            font-size: 14px;
            color: #112d4e;
            position: relative;
            user-select: text;
        }

        .document-header {
            text-align: right;
            margin-bottom: 30px;
            color: #3f72af;
            font-style: italic;
        }

        .document-content p {
            margin-bottom: 15px;
            text-align: justify;
        }

        .highlighted {
            background-color: #3f72af;
            color: #f9f7f7;
            padding: 2px 4px;
            border-radius: 3px;
            cursor: pointer;
            position: relative;
            transition: all 0.3s ease;
        }

        .highlighted:hover {
            background-color: #112d4e;
            transform: scale(1.02);
        }

        .highlighted.selected {
            background-color: #112d4e;
            box-shadow: 0 0 10px rgba(17, 45, 78, 0.5);
        }

        .selection-info {
            background-color: #dbe2ef;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
        }

        .selection-list {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            margin: 20px 0;
        }

        .selection-tag {
            background-color: #3f72af;
            color: #f9f7f7;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .remove-tag {
            background: none;
            border: none;
            color: #f9f7f7;
            cursor: pointer;
            font-size: 16px;
            padding: 0;
            margin-left: 5px;
        }

        .remove-tag:hover {
            color: #dbe2ef;
        }

        .instruction-text {
            color: #3f72af;
            font-size: 18px;
            margin-bottom: 20px;
        }

        .confirm-btn {
            background-color: #3f72af;
            color: #f9f7f7;
            padding: 18px 40px;
            border: none;
            border-radius: 30px;
            font-size: 20px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 20px;
        }

        .confirm-btn:hover {
            background-color: #112d4e;
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(17, 45, 78, 0.3);
        }

        .confirm-btn:disabled {
            background-color: #dbe2ef;
            color: #112d4e;
            cursor: not-allowed;
            transform: none;
        }

        /* Footer */
        .footer {
            background-color: #112d4e;
            padding: 30px;
            text-align: center;
            margin: 0;
        }

        .footer-text {
            color: #f9f7f7;
            font-size: 16px;
        }

        /* Modal for labeling */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(17, 45, 78, 0.5);
        }

        .modal-content {
            background-color: #f9f7f7;
            margin: 15% auto;
            padding: 30px;
            border-radius: 15px;
            width: 90%;
            max-width: 500px;
            text-align: center;
        }

        .modal h3 {
            color: #112d4e;
            margin-bottom: 20px;
            font-size: 24px;
        }

        .modal input {
            width: 100%;
            padding: 15px;
            border: 2px solid #dbe2ef;
            border-radius: 10px;
            font-size: 16px;
            margin-bottom: 20px;
            outline: none;
            transition: border-color 0.3s ease;
        }

        .modal input:focus {
            border-color: #3f72af;
        }

        .modal-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
        }

        .modal-btn {
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .modal-btn.primary {
            background-color: #3f72af;
            color: #f9f7f7;
        }

        .modal-btn.primary:hover {
            background-color: #112d4e;
        }

        .modal-btn.secondary {
            background-color: #dbe2ef;
            color: #112d4e;
        }

        .modal-btn.secondary:hover {
            background-color: #b8c5d6;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .title {
                font-size: 50px;
            }

            .subtitle {
                font-size: 20px;
            }

            .document-container {
                padding: 20px;
                margin: 20px;
            }

            .header {
                margin: 10px;
                padding: 15px 20px;
            }

            .nav {
                flex-direction: column;
                gap: 15px;
            }

            .nav-left {
                gap: 20px;
            }

            .logo {
                font-size: 28px;
            }
        }
    </style>
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
                <div class="user-profile">
                    <span class="username">Username</span>
                    <div class="profile-pic">U</div>
                </div>
            </div>
        </nav>
    </header>

    <main class="main-content">
        <h1 class="title">Lazy Inputer</h1>
        <p class="subtitle">Please select the data</p>

        <div class="document-container" id="documentContainer">
            <div class="document-header">
                Penerima :<br>
                Surabaya, 15 Maret 2024,
            </div>

            <div class="document-content">
                <p><strong>Lampiran: 1 halaman CV</strong><br>
                <strong>Perihal: Lamaran Pekerjaan sebagai Social Media Officer</strong></p>

                <p><strong>Kepada Yth.</strong><br>
                HRD PT Bunga Harmonis</p>

                <p><strong>Dengan Hormat,</strong></p>

                <p>Saya yang bertanda tangan di bawah ini:</p>

                <p>
                    <span class="selectable" data-type="name">Nama: Lala Liliana</span><br>
                    <span class="selectable" data-type="birth">Tempat/Tanggal Lahir: Jakarta, 10 April 1999</span><br>
                    <span class="selectable" data-type="education">Pendidikan: S1 Ilmu Komunikasi Universitas Tulip Merah</span><br>
                    <span class="selectable" data-type="address">Domisili: Surabaya</span>
                </p>

                <p>Dengan ini mengajukan lamaran pekerjaan untuk bergabung dalam tim Marketing PT Bunga Harmonis sebagai Social Media Officer yang dilankan di Instagram.</p>

                <p>Selama menjalani pendidikan, saya aktif terlibat dalam berbagai kegiatan ekstrakurikuler yang telah membentuk keterampilan kepemimpinan, kerja sama tim, dan kemampuan komunikasi saya. Saya juga telah menyelesaikan beberapa magang di berbagai perusahaan yang berbeda, salah satunya adalah:</p>

                <ul>
                    <li><span class="selectable" data-type="experience">Magang sebagai Asisten Marketing di PT Burung Manyar, di mana saya terlibat dalam penyusunan strategi pemasaran online melalui media sosial perusahaan.</span></li>
                </ul>

                <p>Saya juga berhasil mencapai beberapa prestasi, salah satunya sebagai Mahasiswa Berprestasi Universitas Tulip Merah tahun 2023. Saya percaya bahwa kombinasi pengalaman kerja magang, kemampuan, dan pencapaian akademis saya dapat menjadi nilai tambah bagi perusahaan Anda.</p>

                <p>Saya sangat antusias untuk membahas bagaimana saya dapat berkontribusi melalui wawancara lebih lanjut. Atas perhatian dan kesempatan yang diberikan, saya mengucapkan terima kasih.</p>

                <p><strong>Hormat saya,</strong></p>

                <p><span class="selectable" data-type="signature">Lala Liliana</span></p>
            </div>
        </div>

        <div class="selection-info">
            <p class="instruction-text">Click here if all the data has been selected</p>
            <div class="selection-list" id="selectionList"></div>
        </div>

        <button class="confirm-btn" id="confirmBtn" onclick="confirmData()" disabled>
            Confirm Data
        </button>
    </main>

    <footer class="footer">
        <p class="footer-text">© Slothkeys 2025</p>
    </footer>

    <!-- Modal for labeling selected text -->
    <div id="labelModal" class="modal">
        <div class="modal-content">
            <h3>Label Selected Text</h3>
            <p id="selectedText"></p>
            <input type="text" id="labelInput" placeholder="Enter label (e.g., Name, Address, Phone)" maxlength="50">
            <div class="modal-buttons">
                <button class="modal-btn primary" onclick="saveLabel()">Save</button>
                <button class="modal-btn secondary" onclick="closeModal()">Cancel</button>
            </div>
        </div>
    </div>

    <script>
        let selections = [];
        let currentSelection = null;

        // Add click event listeners to selectable elements
        document.addEventListener('DOMContentLoaded', function() {
            const selectableElements = document.querySelectorAll('.selectable');

            selectableElements.forEach(element => {
                element.addEventListener('click', function() {
                    selectText(this);
                });
            });

            // Also allow text selection and right-click labeling
            document.addEventListener('mouseup', handleTextSelection);
        });

        function selectText(element) {
            const text = element.textContent.trim();
            const suggestedType = element.getAttribute('data-type') || '';

            currentSelection = {
                element: element,
                text: text,
                suggestedType: suggestedType
            };

            document.getElementById('selectedText').textContent = `"${text}"`;
            document.getElementById('labelInput').value = suggestedType;
            document.getElementById('labelModal').style.display = 'block';
            document.getElementById('labelInput').focus();
        }

        function handleTextSelection() {
            const selection = window.getSelection();
            if (selection.toString().length > 2) {
                const range = selection.getRangeAt(0);
                const selectedText = selection.toString().trim();

                // Create a temporary element to hold selection
                currentSelection = {
                    range: range,
                    text: selectedText,
                    suggestedType: ''
                };

                document.getElementById('selectedText').textContent = `"${selectedText}"`;
                document.getElementById('labelInput').value = '';
                document.getElementById('labelModal').style.display = 'block';
                document.getElementById('labelInput').focus();
            }
        }

        function saveLabel() {
            const label = document.getElementById('labelInput').value.trim();

            if (!label) {
                alert('Please enter a label for the selected text');
                return;
            }

            if (currentSelection) {
                // Check if this label already exists
                const existingIndex = selections.findIndex(s => s.label.toLowerCase() === label.toLowerCase());

                if (existingIndex > -1) {
                    // Replace existing selection
                    if (selections[existingIndex].element) {
                        selections[existingIndex].element.classList.remove('highlighted', 'selected');
                    }
                    selections[existingIndex] = {
                        text: currentSelection.text,
                        label: label,
                        element: currentSelection.element || null
                    };
                } else {
                    // Add new selection
                    selections.push({
                        text: currentSelection.text,
                        label: label,
                        element: currentSelection.element || null
                    });
                }

                // Highlight the element if it exists
                if (currentSelection.element) {
                    currentSelection.element.classList.add('highlighted', 'selected');
                } else if (currentSelection.range) {
                    // Handle free text selection
                    const span = document.createElement('span');
                    span.className = 'highlighted selected';
                    try {
                        currentSelection.range.surroundContents(span);
                        selections[selections.length - 1].element = span;
                    } catch (e) {
                        console.log('Could not highlight complex selection');
                    }
                }

                updateSelectionDisplay();
                closeModal();
            }
        }

        function closeModal() {
            document.getElementById('labelModal').style.display = 'none';
            document.getElementById('labelInput').value = '';
            currentSelection = null;
            window.getSelection().removeAllRanges();
        }

        function updateSelectionDisplay() {
            const selectionList = document.getElementById('selectionList');
            const confirmBtn = document.getElementById('confirmBtn');

            selectionList.innerHTML = '';

            selections.forEach((selection, index) => {
                const tag = document.createElement('div');
                tag.className = 'selection-tag';
                tag.innerHTML = `
                    <strong>${selection.label}:</strong> ${selection.text.substring(0, 30)}${selection.text.length > 30 ? '...' : ''}
                    <button class="remove-tag" onclick="removeSelection(${index})">×</button>
                `;
                selectionList.appendChild(tag);
            });

            // Enable confirm button if there are selections
            confirmBtn.disabled = selections.length === 0;
        }

        function removeSelection(index) {
            const selection = selections[index];
            if (selection.element) {
                selection.element.classList.remove('highlighted', 'selected');
            }
            selections.splice(index, 1);
            updateSelectionDisplay();
        }

        function confirmData() {
            if (selections.length === 0) {
                alert('Please select some data first');
                return;
            }

            // Create CSV content
            let csvContent = 'data:text/csv;charset=utf-8,';

            // Add headers
            const headers = selections.map(s => s.label);
            csvContent += headers.join(',') + '\n';

            // Add data row
            const dataRow = selections.map(s => `"${s.text.replace(/"/g, '""')}"`);
            csvContent += dataRow.join(',');

            // Create and trigger download
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement('a');
            link.setAttribute('href', encodedUri);
            link.setAttribute('download', 'extracted_data.csv');
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            alert(`Successfully extracted ${selections.length} data fields to CSV!`);
        }

        // Handle Enter key in modal
        document.getElementById('labelInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                saveLabel();
            }
        });

        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('labelModal');
            if (event.target === modal) {
                closeModal();
            }
        }
    </script>
</body>
</html>
<?php /**PATH D:\Naufal\ITS\SEMESTER 5\Pemrograman Berbasis Kerangka Kerja\FP_PBKK\FP\fp_pbkk\resources\views/highlight.blade.php ENDPATH**/ ?>