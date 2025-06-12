
function setupCartObservers(){
    document.addEventListener('cartUpdated', updateCartDisplay);

    setInterval(updateCartDisplay, 30000);

    updateCartDisplay();
}

function triggerCartUpdate() {
    document.dispatchEvent(new CustomEvent('cartUpdated'));
}

function addToCart(productId, quantity) {

    fetch('/add_to_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            'product_id': parseInt(productId),
            'quantity': parseInt(quantity)
        })
    })
    .then(response => response.json())
    .then(data => {
        updateCartDisplay();

        triggerCartUpdate();

        const messageDiv = document.getElementById('cart-message');
        messageDiv.textContent = 'Added to cart!';
        messageDiv.style.display = 'block';
        messageDiv.style.color = 'green';

        setTimeout(() =>{
            messageDiv.style.display = 'none';}
            , 3000);
    })
    .catch(error => {
        console.error('Error', error);
        const messageDiv = document.getElementById('cart-message');
        messageDiv.textContent = 'Error adding to cart';
        messageDiv.style.display = 'block';
        messageDiv.style.color = 'red';
                setTimeout(() =>{
            messageDiv.style.display = 'none';}
            , 3000);
    });

}

function updateCartDisplay(){
    fetch('/cart_summary')
    .then(response => {
        if (!response.ok) throw new Error('Network Error');
        return response.json();
    })
    .then(data => {
        const cartLink = document.querySelector('.cart-link');
        if (cartLink) {
            let countBadge = document.querySelector('.cart-count');
            if (!countBadge && data.cart_count > 0) {
                countBadge = document.createElement('span');
                countBadge.className = 'cart-count';
                cartLink.appendChild(countBadge)
            }

            if (countBadge) { 
                if (data.cart_count > 0) {
                    countBadge.textContent = `(${data.cart_count})`;
                } else {
                    countBadge.remove();
                }
            }
        }

    })
    .catch(error => {
        console.error('Error fetching cart count:', error);
    });
}

async function updateCartItem(itemId, newQuantity){
    input = document.querySelector(`.cart-quantity[data-item-id="${itemId}"]`);
    originalQuantity = input.dataset.originalQuantity;

    try {
        if (isNaN(newQuantity) || newQuantity < 1 || newQuantity > parseInt(input.max)) {
            input.value = originalQuantity;
            throw new Error('Invalid Quantity');
        }

        const response = await fetch('/update_cart_item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                item_id: itemId,
                quantity: newQuantity,
            })
        });

        const data = await response.json();

        if (data.status == 'success') {
            const totalElement = document.querySelector(`[data-item-id="${itemId}"] .item-total`);
            const row = document.querySelector(`[data-item-id="${itemId}"]`);

            input.dataset.originalQuantity = newQuantity;

            if (totalElement) {
                totalElement.textContent = `$${data.new_total.toFixed(2)}`;
            }

            if (data.grand_total) {
                document.querySelector('.cart-grand-total').textContent = `$${data.grand_total.toFixed(2)}`;
            }

            updateCartCount(data.cart_count);

            row.classList.add('updated');
            setTimeout(() => row.classList.remove('updated'), 500);
        } else {
            input.value = originalQuantity;
            throw new Error(data.message || 'Update failed')
        }
    } catch (error) {
        input.value = originalQuantity;
        console.error('Error updating cart:', error)
    }
}

function updateCartCount(newCount) {
    const countBadge = document.querySelector('.cart-count');
    if (!countBadge && newCount > 0) {
        countBadge = document.createElement('span');
        countBadge.className = 'cart-count';
        cartLink.appendChild(countBadge)
    }

    if (countBadge) { 
        if (newCount > 0) {
            countBadge.textContent = `(${newCount})`;
        } else {
            countBadge.remove();
        }
    }
}

async function removeCartItem(itemId){
    const row = document.querySelector(`[data-item-id="${itemId}"]`);
    try {
        const btn = row.querySelector('button');
        btn.disabled = true;
        btn.textContent = 'Removing...';

        const response = await fetch('/remove_cart_item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                item_id: itemId
            })
        });
        const data = await response.json();
        const cartTable = document.querySelector('.cart-table');
        
        if (data.status == 'success') {
            row.style.transition = 'all 0.3s';
            row.style.opacity = '0';

            triggerCartUpdate();

            setTimeout(() => {
                if (row) row.remove();

                if (data.grand_total !== undefined) {
                    document.querySelector('.cart-grand-total').textContent = `$${data.grand_total.toFixed(2)}`;
                }

                if (data.is_cart_empty) {
                    cartTable.style.display = 'none';
                    document.querySelector('.cart-table').insertAdjacentHTML('afterend',
                         '<div class="empty-cart-message">Your cart is empty</div>');
                }
            }, 300);
        }
    } catch (error) {
        console.error('Error:', error);
        const btn = row.querySelector('button');
        btn.disabled = false;
        btn.textContent = 'Remove';
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'cart-error';
        errorDiv.textContent = error.message;
        row.appendChild(errorDiv);
        
        setTimeout(() => errorDiv.remove(), 3000);
    }
}

let cartInitialized = false;

function initializeCart() {
    if (cartInitialized) return;
    cartInitialized = true;

    // Setup cart observers
    setupCartObservers();

    // Add to cart button
    const addButton = document.getElementById('add-to-cart-button');
    if (addButton) {
        addButton.addEventListener('click', function(e) {
            const productId = document.querySelector('input[name="product_id"]').value;
            const quantity = document.querySelector('input[name="quantity"]').value;
            addToCart(productId, quantity);
        });
    }

    // Cart table event delegation (better than individual listeners)
    const cartTable = document.getElementById('cart-table');
    if (cartTable) {
        // Use named functions for proper removal
        function handleCartChange(e) {
            if (e.target.classList.contains('cart-quantity')) {
                const itemId = e.target.dataset.itemId;
                const newQuantity = e.target.value;
                updateCartItem(itemId, newQuantity);
            }
        }

        function handleCartClick(e) {
            if (e.target.classList.contains('remove-item')) {
                const itemId = e.target.dataset.itemId;
                removeCartItem(itemId);
            }
        }

        cartTable.addEventListener('change', handleCartChange);
        cartTable.addEventListener('click', handleCartClick);

        // Store references for cleanup
        cartTable._cartHandlers = { 
            change: handleCartChange, 
            click: handleCartClick 
        };
    }
}

// Cleanup function for SPA/turbo pages
function cleanupCart() {
    const cartTable = document.getElementById('cart-table');
    if (cartTable && cartTable._cartHandlers) {
        cartTable.removeEventListener('change', cartTable._cartHandlers.change);
        cartTable.removeEventListener('click', cartTable._cartHandlers.click);
        delete cartTable._cartHandlers;
    }
    cartInitialized = false;
}

// Standard initialization
document.addEventListener('DOMContentLoaded', initializeCart);

// TurboDrive compatibility
if (typeof Turbo !== 'undefined') {
    document.addEventListener('turbo:load', function() {
        cleanupCart();
        initializeCart();
    });
    document.addEventListener('turbo:before-render', cleanupCart);
}