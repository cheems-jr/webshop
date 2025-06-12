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
        return response.json()
    })
    .then(data => {
        const count = document.getElementById('cart_count');
        if (count) count.textContent = data.cart_count || 0;
    })
    .catch(error => {
        console.error('Error fetching cart count:', error);
    });
}

async function updateCartItem(itemId, newQuantity){
    try {
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

            if (totalElement) {
                totalElement.textContent = `$${data.new_total.toFixed(2)}`;
            }

            if (data.grand_total) {
                document.querySelector('.cart-grand-total').textContent = `$${data.grand_total.toFixed(2)}`;
            }

            row.classList.add('updated');
            setTimeout(() => row.classList.remove('updated'), 500);
        }
    } catch (error) {
        console.error('Error updating cart:', error)
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
        
        if (data.status == 'success') {
            row.style.transition = 'all 0.3s';
            row.style.opacity = '0';

            setTimeout(() => {
                if (row) row.remove();

                if (data.is_cart_empty) {
                    document.querySelector('.cart-table').insertAdjacentHTML('afterend',
                         '<div class="empty-cart-message">Your cart is empty</div>');
                }
                if (data.grand_total) {
                    document.querySelector('tfoot td:nth-child(2)')
                        .textContent = `$${data.grand_total.toFixed(2)}`;
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

document.addEventListener('DOMContentLoaded', updateCartDisplay)

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('cart-table').addEventListener('change', function(e) {
        if (e.target.classList.contains('cart-quantity')) {
            const itemId = e.target.dataset.itemId;
            const newQuantity = e.target.value;
            updateCartItem(itemId, newQuantity);
        }
    });
    document.getElementById('cart-table').addEventListener('click', function(e){
        if (e.target.classList.contains('remove-item')) {
            const itemId = e.target.dataset.itemId;
            removeCartItem(itemId);
        }
    });
  });
document.addEventListener('DOMContentLoaded', function() {
    const addButton = document.getElementById('add-to-cart-button');
    
    if (addButton) {  // Safety check
      addButton.addEventListener('click', function() {
        const productId = document.querySelector('input[name="product_id"]').value;
        const quantity = document.querySelector('input[name="quantity"]').value;
        addToCart(productId, quantity);
      });
    }
  });