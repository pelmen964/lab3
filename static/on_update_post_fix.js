
function submitForm(token) {
    const formData = new FormData();

    const radios = document.querySelectorAll('input[name="name_op"]');
    let radioValue;
    radios.forEach(radio => {
        if (radio.checked) {
            radioValue = radio.value;
        }
    });

    formData.append('g_recaptcha_response',token)
    formData.append('name_op', radioValue)
    formData.append('file', document.querySelector('input[type="file"]').files);

    fetch('/image_form', {
        method: 'POST',
        body: formData,
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            // Обработка ответа от сервера
        })
        .catch(error => {
            // Обработка ошибки
        });
}