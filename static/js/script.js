// static/js/script.js

document.addEventListener('DOMContentLoaded', function () {
    const fileInput = document.getElementById('file');
    const uploadForm = document.getElementById('upload-form');

    fileInput.addEventListener('change', function () {
        if (fileInput.files.length > 0) {
            const fileName = document.createElement('small');
            fileName.classList.add('form-text', 'text-muted');
            fileName.textContent = `Selected file: ${fileInput.files[0].name}`;
            // Remove previous file name if exists
            const existingFileName = document.querySelector('.file-name');
            if (existingFileName) {
                existingFileName.remove();
            }
            fileName.classList.add('file-name');
            fileInput.parentNode.appendChild(fileName);
        }
    });
});
