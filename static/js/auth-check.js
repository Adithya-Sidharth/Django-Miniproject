document.addEventListener("DOMContentLoaded", function() {
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    const buyNowButtons = document.querySelectorAll('.buy-now');
    const loggedIn = document.body.dataset.loggedIn === 'true';  // Check if logged in

    addToCartButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            if (!loggedIn) {
                alert('You must log in to add items to the cart.');
                window.location.href = '/login/?next=' + window.location.pathname;  // Redirect to login
            }
        });
    });

    buyNowButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            if (!loggedIn) {
                alert('You must log in to buy now.');
                window.location.href = '/login/?next=' + window.location.pathname;  // Redirect to login
            }
        });
    });
});
