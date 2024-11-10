function submitScheduleForm(event) {
    event.preventDefault(); // Prevent default form submission

    const formData = new FormData(document.getElementById('schedulerForm'));
    const scheduleData = Object.fromEntries(formData.entries());

    fetch('/', {
        method: 'POST',
        body: new URLSearchParams(scheduleData),
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Schedule added successfully:', data);
        // Optionally, update the UI or reset the form here
    })
    .catch(error => {
        console.error('Error adding schedule:', error);
    });
}