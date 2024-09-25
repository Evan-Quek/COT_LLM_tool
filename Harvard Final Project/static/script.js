document.getElementById('query').addEventListener('keydown', function(event) {
    // Check if only Enter is pressed (without Shift or Ctrl)
    if (event.key === 'Enter' && !event.shiftKey && !event.ctrlKey) {
        event.preventDefault();  // Prevent default behavior of adding a new line
        document.getElementById('submitQuery').click();  // Trigger form submission
    }
    // If Shift + Enter or Ctrl + Enter, allow the new line
    else if (event.key === 'Enter' && (event.shiftKey || event.ctrlKey)) {
        // Do nothing, this will allow the new line (default behavior)
    }
});

document.getElementById('submitQuery').addEventListener('click', function() {
    const query = document.getElementById('query').value;
    const responseDiv = document.getElementById('response');
    const documentDiv = document.getElementById('document-content');
    const loadingDiv = document.getElementById('loading');
    const selectedModel = document.getElementById('modelSelect').value;
    const csvTableDiv = document.getElementById('csvTable');  // Add reference to the CSV table container

    // Clear previous response and CSV table
    responseDiv.textContent = '';
    csvTableDiv.innerHTML = '';  // Clear the previous CSV table
    responseDiv.classList.remove('alert-success', 'alert-danger');
    responseDiv.classList.add('alert-info');
    responseDiv.textContent = 'Fetching response...';
    loadingDiv.style.display = 'block';

    // Check if query is empty
    if (!query.trim()) {
        responseDiv.textContent = 'Please enter a query.';
        responseDiv.classList.add('alert-danger');
        loadingDiv.style.display = 'none';
        return;
    }

    // Make the API request
    fetch('http://127.0.0.1:5000/rag-model', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query: query,
            model: selectedModel
        }),
    })
    .then(response => response.json())
    .then(data => {
        loadingDiv.style.display = 'none';  // Hide loading spinner
        if (data.response) {
            // Display the generated response in the chat area
            responseDiv.textContent = data.response;
            responseDiv.classList.remove('alert-info');
            responseDiv.classList.add('alert-success');

            // If a CSV table is provided, display it
            if (data.table) {
                csvTableDiv.innerHTML = data.table;  // Insert the table HTML into the div
            }
        } else {
            responseDiv.textContent = 'An error occurred: ' + (data.error || 'Unknown error.');
            responseDiv.classList.remove('alert-info');
            responseDiv.classList.add('alert-danger');
        }
    })
    .catch(error => {
        loadingDiv.style.display = 'none';  // Hide loading spinner
        responseDiv.textContent = 'An error occurred: ' + error.message;
        responseDiv.classList.remove('alert-info');
        responseDiv.classList.add('alert-danger');
        console.error('Error:', error);
    });
});
