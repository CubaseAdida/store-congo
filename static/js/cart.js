// Gestion panier frontend avec AJAX - Amélioration badges live
document.addEventListener('DOMContentLoaded', function() {
    // Fonction AJAX générique
    function ajaxPost(url, data, successCallback) {
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams(data)
        })
        .then(response => response.text())
        .then(data => {
            if (successCallback) successCallback(data);
        })
        .catch(error => console.error('Erreur AJAX:', error));
    }

    // Fonction AJAX GET générique
    function ajaxGet(url, successCallback) {
        fetch(url)
        .then(response => response.json())
        .then(data => {
            if (successCallback) successCallback(data);
        })
        .catch(error => console.error('Erreur AJAX GET:', error));
    }

    // Mise à jour tous les badges panier (float + navbar)
    function updateCartBadges(count) {
        // Float badges
        const floatBadges = document.querySelectorAll('.cart-float .cart-badge');
        floatBadges.forEach(badge => {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'flex' : 'none';
        });
        
        // Navbar badges
        const navbarBadges = document.querySelectorAll('.navbar .badge.bg-danger');
        navbarBadges.forEach(badge => {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline-block' : 'none';
        });
        
        // Titles mise à jour
        const floatLinks = document.querySelectorAll('.cart-float');
        floatLinks.forEach(link => {
            const title = count > 0 ? `Panier (${count} articles)` : 'Panier vide';
            link.title = title;
        });
        
        console.log(`🛒 Panier mis à jour: ${count} articles`);
    }

    // Récupérer count panier depuis serveur
    function fetchCartCount() {
        ajaxGet('/cart_count', function(data) {
            updateCartBadges(data.count || 0);
        });
    }

    // Vider panier complet
    window.clearCart = function() {
        ajaxPost('/clear_cart', {}, function() {
            updateCartBadges(0);
        });
    };

    // Mise à jour quantité
    window.updateQty = function(productId, newQty) {
        ajaxPost('/update_cart', {
            product_id: productId,
            quantity: newQty
        }, function() {
            fetchCartCount(); // Live update
        });
    };

    // Boutons + / -
    document.querySelectorAll('.qty-group .qty-minus, .qty-group .qty-plus').forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.parentNode.querySelector('.qty-input');
            const productId = input.dataset.productId;
            let qty = parseInt(input.value);
            if (this.classList.contains('qty-minus')) {
                if (qty > 1) {
                    input.value = qty - 1;
                    updateQty(productId, qty - 1);
                }
            } else {
                input.value = qty + 1;
                updateQty(productId, qty + 1);
            }
        });
    });

    // Input quantité direct
    document.querySelectorAll('.qty-input').forEach(input => {
        input.addEventListener('change', function() {
            const productId = this.dataset.productId;
            const newQty = parseInt(this.value) || 0;
            if (newQty < 0) this.value = 0;
            updateQty(productId, newQty);
        });
    });

    // Boutons supprimer (🗑️)
    document.querySelectorAll('.delete-form button').forEach(btn => {
        btn.textContent = '🗑️ Supprimer';
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            if (confirm('Supprimer cet article du panier ?')) {
                const form = this.closest('form');
                const productId = form.querySelector('input[name="product_id"]').value;
                ajaxPost('/cart', new FormData(form), function() {
                    fetchCartCount();
                });
            }
        });
    });

    // Écouter boutons "Ajouter au panier" partout
    document.addEventListener('click', function(e) {
        if (e.target.closest('a[href*="/add_to_cart"]') || e.target.closest('form[action*="/add_to_cart"]')) {
            setTimeout(fetchCartCount, 500); // Update après redirect/AJAX
        }
    });

    // Initialiser badges au chargement
    fetchCartCount();

    function updateTotal() {
        let total = 0;
        document.querySelectorAll('.item-total').forEach(el => {
            const priceText = el.textContent.replace(/[€,\s]/g, '');
            total += parseFloat(priceText) || 0;
        });
        const totalEl = document.querySelector('.text-success.h5, .text-primary.h2');
        if (totalEl) {
            totalEl.textContent = total.toLocaleString('fr-FR') + ' FCFA';
        }
    }
});
