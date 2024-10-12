document.addEventListener('DOMContentLoaded', function() {
    var questionId = 1; // Replace with the actual question ID

    fetch(`http://localhost:8000/get_question/${questionId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('question-title').textContent = 'Error loading question';
                document.getElementById('question-difficulty').textContent = '';
                document.getElementById('question-content').innerHTML = '';
            } else {
                document.getElementById('question-title').textContent = data.title;
                document.getElementById('question-difficulty').textContent = `Difficulty: ${data.difficulty}`;
                document.getElementById('question-content').innerHTML = data.content;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('question-title').textContent = 'Error loading question';
            document.getElementById('question-difficulty').textContent = '';
            document.getElementById('question-content').innerHTML = '';
        });
});
