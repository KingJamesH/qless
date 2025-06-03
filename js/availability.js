document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.check-availability').forEach(button => {
        button.addEventListener('click', function() {
            const restaurantName = this.dataset.name;
            const statusDiv = this.nextElementSibling;
            
            statusDiv.style.display = 'block';
            
            // get restaurant data
            const parentCard = this.closest('.restaurant-card');
            const data = parentCard.dataset;
            
            // get times
            const openingTime = data.openingTime;
            const closingTime = data.closingTime;
            
            // get current time --- like datetime module but for js
            const now = new Date();
            const currentHour = now.getHours();
            const currentMinute = now.getMinutes();
            const [openHour, openMinute] = openingTime.split(':').map(Number);
            const [closeHour, closeMinute] = closingTime.split(':').map(Number);
            
            const isOpen = (currentHour > openHour || (currentHour === openHour && currentMinute >= openMinute)) &&
                          (currentHour < closeHour || (currentHour === closeHour && currentMinute < closeMinute));
            
            // update text with above info
            const statusText = statusDiv.querySelector('.status-text');
            const closingTimeText = statusDiv.querySelector('.closing-time');
            
            if (isOpen) {
                statusText.textContent = 'Open';
                closingTimeText.textContent = `Closes at ${closingTime}`;
            } else {
                statusText.textContent = 'Closed';
                closingTimeText.textContent = `Opens at ${openingTime}`;
            }
        });
    });
});
