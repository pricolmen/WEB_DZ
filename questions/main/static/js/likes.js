document.addEventListener('DOMContentLoaded', function() {
    console.log('Unified likes script loaded');
    
    // Функция для получения CSRF токена
    function getCSRFToken() {
        // Пробуем найти в форме
        const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (tokenInput) return tokenInput.value;
        
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith('csrftoken=')) {
                return cookie.substring('csrftoken='.length);
            }
        }
        return null;
    }
    
    // Обработчик кликов
    document.addEventListener('click', function(e) {
        const target = e.target;
        
        //проверка это ли кнопка лайка/дизлайка
        if (target.classList.contains('like-btn') || target.classList.contains('dislike-btn')) {
            e.preventDefault();
            
            const type = target.dataset.type;
            const id = target.dataset.id;
            const value = parseInt(target.dataset.value);
            
            console.log('Data:', { type, id, value });

            if (target.disabled) {
                console.log('Button disabled');
                return;
            }
            
            // URL endpoint
            let url;
            let dataKey;
            
            if (type === 'question') {
                url = '/ajax/like/question/';
                dataKey = 'question_id';
            } else {
                url = '/ajax/like/answer/';
                dataKey = 'answer_id';
            }
            
            // CSRF токен
            const csrfToken = getCSRFToken();
            console.log('CSRF token:', csrfToken);
            
            if (!csrfToken) {
                alert('CSRF token not found. Please refresh the page.');
                return;
            }
            
            // JSON данные
            const jsonData = {
                [dataKey]: id,
                'value': value
            };
            
            console.log('Sending JSON:', jsonData);

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(jsonData),
                credentials: 'same-origin'
            })
            .then(response => {
                console.log('Response status:', response.status);
                return response.json().then(data => ({
                    status: response.status,
                    ok: response.ok,
                    data: data
                }));
            })
            .then(result => {
                console.log('Response data:', result.data);
                
                if (result.ok) {
                    if (result.data.success) {
                        const counter = document.getElementById(`${type}-rating-${id}`);
                        if (counter) {
                            counter.textContent = result.data.rating;
                            console.log(`Updated ${type} ${id} to:`, result.data.rating);
                        }

                        updateButtonStyles(type, id, result.data.user_vote);
                        
                        console.log('=== REQUEST SUCCESS ===');
                    } else {
                        alert('Error: ' + (result.data.error || 'Unknown error'));
                    }
                } else {
                    alert(`Error ${result.status}: ${result.data.error || 'Server error'}`);
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                alert('Network error: ' + error.message);
            });
        }
    });

    function updateButtonStyles(type, id, userVote) {
        const upButton = document.querySelector(`.like-btn[data-type="${type}"][data-id="${id}"]`);
        const downButton = document.querySelector(`.dislike-btn[data-type="${type}"][data-id="${id}"]`);
        
        if (!upButton || !downButton) {
            console.log(`Buttons not found for ${type} ${id}`);
            return;
        }
        
        console.log(`Setting styles for vote: ${userVote}`);

        upButton.classList.remove('btn-success');
        upButton.classList.add('btn-outline-success');
        
        downButton.classList.remove('btn-danger');
        downButton.classList.add('btn-outline-danger');
 
        if (userVote === 1) {
            upButton.classList.remove('btn-outline-success');
            upButton.classList.add('btn-success');
        } else if (userVote === -1) {
            downButton.classList.remove('btn-outline-danger');
            downButton.classList.add('btn-danger');
        }
    }

    console.log('Found buttons:', 
        document.querySelectorAll('.like-btn, .dislike-btn').length);
});