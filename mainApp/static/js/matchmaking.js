document.addEventListener('DOMContentLoaded', function () {
    const startMatchButton = document.getElementById('start-match-button');
    const quickPlayButton = document.getElementById('quick-match-button');
    const form = document.getElementById('question-form');
    const waitingPopup = document.getElementById('waiting-popup');
    const matchFoundPopup = document.getElementById('match-found-popup');
    const vsScreenPopup = document.getElementById('vs-screen-popup');
    const player1Name = document.getElementById('player1-name');
    const player2Name = document.getElementById('player2-name');

    if (startMatchButton) {
        startMatchButton.addEventListener('click', function () {
            console.log("Button has been clicked!");

            // Show "Waiting for player..." popup
            waitingPopup.style.display = 'flex';

            fetch('/start-match/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const roomId = data.room_id;

                    const checkRoomStatus = setInterval(() => {
                        fetch('/check-room-status/', {
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': getCookie('csrftoken'),
                                'Content-Type': 'application/json'
                            }
                        })
                        .then(response => response.json())
                        .then(statusData => {
                            if (statusData.status === 'ready') {
                                console.log(statusData)
                                clearInterval(checkRoomStatus);

                                // Hide "Waiting for player..." popup
                                waitingPopup.style.display = 'none';

                                // Show "Match Found!" popup
                                matchFoundPopup.style.display = 'flex';

                                setTimeout(() => {
                                    matchFoundPopup.style.display = 'none';

                                    // Set player names for "Vs" screen
                                    // If statusData contains player_username and opponent_username, use them. Else, use them from data
                                    player1Name.textContent = statusData.player_username || data.player_username;
                                    player2Name.textContent = statusData.opponent_username || data.opponent_username;

                                    // Show "Vs" screen popup
                                    vsScreenPopup.style.display = 'flex';

                                    setTimeout(() => {
                                        window.location.href = statusData.redirect_url;
                                    }, 3000); // Wait for 3 seconds before redirecting
                                }, 2000); // Wait for 2 seconds before showing "Vs" screen
                            }
                        });
                    }, 5000); // Check every 5 seconds
                }
            });
        });
    }

    if (form) {
        form.addEventListener('submit', function (event) {
            console.log("This is 2nd match");
            event.preventDefault();  // Prevent default form submission

            const formData = new FormData(form);
            formData.append('room_id', getRoomId());  // Add room_id to form data

            fetch('/submit-answer/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                statusText.textContent = data.message;
                if (data.status === 'success') {
                    // Redirect or perform other actions on success
                    setTimeout(() => {
                        window.location.href = '/home/'; // Redirect to home or other page
                    }, 2000); // Wait for 2 seconds before redirecting
                }
            });
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function getRoomId() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('room_id');
    }
});


if (quickPlayButton) {
    quickPlayButton.addEventListener('click', function () {
        console.log("Quick Play button has been clicked!");

        // Show "Waiting for player..." popup
        waitingPopup.style.display = 'flex';

        fetch('/quick-play/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Hide "Waiting for player..." popup immediately since it's a solo match
                waitingPopup.style.display = 'none';

                // Show "Match Found!" popup immediately
                matchFoundPopup.style.display = 'flex';

                setTimeout(() => {
                    matchFoundPopup.style.display = 'none';

                    // Set player names for "Vs" screen
                    player1Name.textContent = data.player_username || "Player 1";
                    player2Name.textContent = "AI Opponent"; // or any placeholder name for the opponent

                    // Show "Vs" screen popup
                    vsScreenPopup.style.display = 'flex';

                    setTimeout(() => {
                        window.location.href = data.redirect_url; // Redirect to the match
                    }, 3000); // Wait for 3 seconds before redirecting
                }, 2000); // Wait for 2 seconds before showing "Vs" screen
            }
        });
    });
}
