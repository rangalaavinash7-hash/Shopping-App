/**
 * ShopFinder: User Wishlist Controller
 * Manages fetching, rendering, and removing saved wishlist products.
 */

document.addEventListener("DOMContentLoaded", () => {
    loadUserWishlist();
});

async function loadUserWishlist() {
    const container = document.getElementById("wishlistContainer");
    if (!container) return;

    container.innerHTML = `
        <div style="text-align: center; padding: 3rem 1rem;">
            <div class="spinner-border text-primary" role="status" style="width: 2.5rem; height: 2.5rem;"></div>
            <p style="margin-top: 1rem; color: var(--text-muted);">Loading your saved items...</p>
        </div>
    `;

    try {
        const res = await fetch("/api/wishlist");
        if (res.status === 401) {
            window.location.href = "/login?next=/wishlist";
            return;
        }

        const data = await res.json();
        const items = data.wishlist || [];

        if (items.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-heartbreak empty-state-icon text-muted"></i>
                    <h3>Your Wishlist is Empty</h3>
                    <p>You haven't saved any products yet. Browse through our catalog and click the heart icon on any product to save it here for price monitoring!</p>
                    <a href="/products" class="btn btn-primary">Start Shopping</a>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="products-grid">
                ${items.map(p => `
                    <div class="product-card">
                        <div class="product-thumb-wrap">
                            <img src="${p.image_url}" alt="${p.product_name}" class="product-thumb">
                            <button class="wishlist-btn-overlay active remove-wishlist-btn" data-id="${p.wishlist_id}" title="Remove from Wishlist">
                                <i class="bi bi-trash-fill text-danger"></i>
                            </button>
                        </div>
                        <div class="product-content">
                            <div class="product-meta-row">
                                <span class="product-brand">${p.brand}</span>
                                <div class="product-rating">
                                    <i class="bi bi-star-fill"></i>
                                    <span>${p.best_rating || '4.2'}</span>
                                </div>
                            </div>
                            <h3 class="product-title">${p.product_name}</h3>
                            <div class="product-prices">
                                <span class="current-price">₹${Number(p.min_price).toLocaleString('en-IN')}</span>
                            </div>
                            <div class="product-actions" style="margin-top: 1rem;">
                                <a href="/compare?product_id=${p.id}" class="btn btn-primary btn-sm" style="grid-column: 1 / -1;">
                                    Compare Platform Deals <i class="bi bi-arrow-right"></i>
                                </a>
                            </div>
                        </div>
                    </div>
                `).join("")}
            </div>
        `;

        // Attach removal listeners
        container.querySelectorAll(".remove-wishlist-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                const wid = btn.getAttribute("data-id");
                try {
                    const delRes = await fetch(`/api/wishlist/${wid}`, { method: "DELETE" });
                    if (delRes.ok) {
                        showToast("Item removed from wishlist", "info");
                        loadUserWishlist();
                    } else {
                        showToast("Failed to remove item", "error");
                    }
                } catch (e) {
                    showToast("Network error", "error");
                }
            });
        });

    } catch (err) {
        console.error("Wishlist fetch error:", err);
        container.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-exclamation-triangle empty-state-icon text-danger"></i>
                <h3>Unable to Load Wishlist</h3>
                <p>Please try logging in again or refresh the page.</p>
                <a href="/login" class="btn btn-primary">Login</a>
            </div>
        `;
    }
}
