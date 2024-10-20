document.addEventListener('DOMContentLoaded', function() {
    const submitButton = document.getElementById('submitBtn');
    const responseDiv = document.getElementById('results'); // Change to 'results'

    submitButton.addEventListener('click', function(event) {
        event.preventDefault(); // Prevent the default button behavior

        // Retrieve values from your form inputs
        const samplingPointID = document.getElementById('sampling').value; // Match IDs
        const testID = document.getElementById('test').value; // Match IDs
        const expertiseLevelID = document.getElementById('expertise').value; // Match IDs

        // Create the request body
        const requestData = {
            SamplingPointID: samplingPointID,
            TestID: testID,
            ExpertiseLevelID: expertiseLevelID
        };

        // Make the fetch call
        fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData) // Send the JSON body
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json(); // Parse JSON response
        })
        .then(data => {
            responseDiv.innerHTML = ''; // Clear previous response
            for (let i = 1; i <= Object.keys(data).length / 2; i++) {
                responseDiv.innerHTML += `<p>${data[`Prediction ${i}`]}: ${data[`Confidence ${i}`]}</p>`;
            }
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
            responseDiv.innerHTML = `<p>Error: ${error.message}</p>`;
        });
    });
});
