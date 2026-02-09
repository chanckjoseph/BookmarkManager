javascript: (function () {
    const data = {
        title: document.title,
        url: window.location.href
    };

    const API_URL = 'http://localhost:5000/add';

    fetch(API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
        .then(response => response.json())
        .then(result => {
            console.log('BookmarkManager Success:', result);
            alert('Saved to BookmarkManager: ' + data.title);
        })
        .catch((error) => {
            console.error('BookmarkManager Error:', error);
            alert('Failed to save bookmark. Is the API running?');
        });
})();
