document.addEventListener('DOMContentLoaded', function() {
    // Handle restaurant selection
    const selectForm = document.getElementById('restaurant-select-form');
    selectForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const restaurant = document.getElementById('restaurant').value.trim();
        if (restaurant) {
            // Show status form
            document.getElementById('restaurant-info').style.display = 'block';
            
            // Fetch current status
            fetch('/get_status', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    restaurant: restaurant
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update form fields with current status
                        document.getElementById('employees').value = data.status.employees || 0;
                        document.getElementById('open-tables').value = data.status.open_tables || 0;
                        document.getElementById('queue-length').value = data.status.queue_length || 0;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error fetching restaurant status.');
                });
        }
    });

    // Handle status form submission
    const statusForm = document.getElementById('status-form');
    if (statusForm) {
        statusForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Get form values and validate
            const restaurant = document.getElementById('restaurant').value;
            const employees = parseInt(document.getElementById('employees').value) || 0;
            const openTables = parseInt(document.getElementById('open-tables').value) || 0;
            const queueLength = parseInt(document.getElementById('queue-length').value) || 0;

            // Validate the values
            if (isNaN(employees) || isNaN(openTables) || isNaN(queueLength)) {
                alert('Please enter valid numbers for all fields');
                return;
            }

            // Send the data to the server
            fetch('/update-status', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    restaurant: restaurant,
                    employees: employees,
                    open_tables: openTables,
                    queue_length: queueLength
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Status updated successfully!');
                    // Update form fields with new status
                    document.getElementById('employees').value = data.status.employees;
                    document.getElementById('open-tables').value = data.status.open_tables;
                    document.getElementById('queue-length').value = data.status.queue_length;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error updating status. Please try again.');
            });
        });
    }
});
