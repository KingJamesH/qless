document.addEventListener('DOMContentLoaded', function() {
    // restaurants sorted by distance --> goes into restaurant card list
    const restaurantCards = document.querySelectorAll('.restaurant-card');
    const restaurantList = document.querySelector('.restaurant-list');
    const sortedCards = Array.from(restaurantCards).sort((a, b) => {
        const distA = parseFloat(a.querySelector('p').textContent.split(' ')[2]);
        const distB = parseFloat(b.querySelector('p').textContent.split(' ')[2]);
        return distA - distB;
    });
    sortedCards.forEach(card => restaurantList.appendChild(card));

    const selectedRestaurantDiv = document.getElementById('selected-restaurant');
    const noRestaurantMessage = document.getElementById('no-restaurant-message');
    const restaurantNameElement = document.getElementById('restaurant-name');
    const statusTextElement = document.getElementById('status-text');
    const closingTimeElement = document.getElementById('closing-time');
    const employeesStatusElement = document.getElementById('employees-status');
    const tablesStatusElement = document.getElementById('tables-status');
    const queueStatusElement = document.getElementById('queue-status');

    // click selection basically makes the button do stuff
    document.querySelectorAll('.check-availability').forEach(button => {
        button.addEventListener('click', function() {
            // get data
            const parentCard = this.closest('.restaurant-card');
            const restaurantName = this.dataset.name;
            const openingTime = parentCard.dataset.openingTime;
            const closingTime = parentCard.dataset.closingTime;
            
            const now = new Date();
            const currentHour = now.getHours();
            const currentMinute = now.getMinutes();
            
            const [openHour, openMinute] = openingTime.split(':').map(Number);
            const [closeHour, closeMinute] = closingTime.split(':').map(Number);
            
            const isOpen = (currentHour > openHour || (currentHour === openHour && currentMinute >= openMinute)) &&
                          (currentHour < closeHour || (currentHour === closeHour && currentMinute < closeMinute));
            
            if (isOpen) {
                selectedRestaurantDiv.style.display = 'block';
                noRestaurantMessage.style.display = 'none';
                
                restaurantNameElement.textContent = restaurantName;
                
                closingTimeElement.textContent = `Closes at ${closingTime}`;
                
                fetch(`/update-status?restaurant=${encodeURIComponent(restaurantName)}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success && data.status) {
                            statusTextElement.textContent = 'Open';
                            employeesStatusElement.textContent = data.status.employees || 'unknown';
                            tablesStatusElement.textContent = data.status.open_tables || 'unknown';
                            queueStatusElement.textContent = data.status.queue_length || 'unknown';
                            
                            const totalTablesElement = document.getElementById('total-tables-status');
                            if (totalTablesElement) {
                                totalTablesElement.textContent = data.status.total_tables || 'unknown';
                            }
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching restaurant status:', error);
                        // error just shows unknown instead of crashing stuff
                        statusTextElement.textContent = 'Open';
                        employeesStatusElement.textContent = 'unknown';
                        tablesStatusElement.textContent = 'unknown';
                        queueStatusElement.textContent = 'unknown';
                        
                        const totalTablesElement = document.getElementById('total-tables-status');
                        if (totalTablesElement) {
                            totalTablesElement.textContent = 'unknown';
                        }
                    });
            } else {
                selectedRestaurantDiv.style.display = 'block';
                noRestaurantMessage.style.display = 'none';
                
                restaurantNameElement.textContent = restaurantName;
                statusTextElement.textContent = 'Closed';
                closingTimeElement.textContent = `Opens at ${openingTime}`;
                
                employeesStatusElement.textContent = 'unknown';
                tablesStatusElement.textContent = 'unknown';
                queueStatusElement.textContent = 'unknown';
                
                const totalTablesElement = document.getElementById('total-tables-status');
                if (totalTablesElement) {
                    totalTablesElement.textContent = 'unknown';
                }
            }
        });
    });
});
