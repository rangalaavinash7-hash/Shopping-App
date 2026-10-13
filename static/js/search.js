/**
 * ShopFinder: Search & Catalog Filter Engine
 * Integrates Trie auto-complete suggestions and reactive catalog filtering.
 */

let debounceTimer = null;
let currentFilters = {
    q: "",
    category_id: "",
    platform_id: "",
    min_price: "",
    max_price: "",
    min_rating: "",
    sort_by: "relevance",
    sort_order: "asc"
};

document.addEventListener("DOMContentLoaded", () => {
    initSearchInputs();
    initCatalogFilters();
});

// -------------------------------------------------------------
// Trie Autocomplete Search Suggestions
// -------------------------------------------------------------
function initSearchInputs() {
    const searchInputs = document.querySelectorAll(".live-search-input");
    searchInputs.forEach(input => {
        const dropdown = input.closest(".search-container")?.querySelector(".suggestions-dropdown");

        input.addEventListener("input", (e) => {
            const query = e.target.value.trim();
            clearTimeout(debounceTimer);

            if (query.length < 2) {
                if (dropdown) dropdown.classList.remove("active");
                return;
            }

            debounceTimer = setTimeout(async () => {
                try {
                    const res = await fetch(`/api/products/suggestions?q=${encodeURIComponent(query)}`);
                    const data = await res.json();
                    renderSuggestions(dropdown, data.suggestions, input);
                } catch (err) {
                    console.error("Trie suggestions error:", err);
                }
            }, 200);
        });

        // Close suggestions dropdown on outside click
        document.addEventListener("click", (e) => {
            if (!input.contains(e.target) && dropdown && !dropdown.contains(e.target)) {
                dropdown.classList.remove("active");
            }
        });
    });

    // Main search form submissions
    const searchForms = document.querySelectorAll(".search-form");
    searchForms.forEach(form => {
        form.addEventListener("submit", (e) => {
            e.preventDefault();
            const input = form.querySelector(".live-search-input");
            const q = input?.value.trim() || "";
            if (window.location.pathname === "/products") {
                currentFilters.q = q;
                fetchCatalogProducts();
            } else {
                window.location.href = `/products?q=${encodeURIComponent(q)}`;
            }
        });
    });
}

function renderSuggestions(dropdown, suggestions, input) {
    if (!dropdown) return;

    if (!suggestions || suggestions.length === 0) {
        dropdown.classList.remove("active");
        return;
    }

    dropdown.innerHTML = suggestions.map(item => `
        <div class="suggestion-item" data-title="${item.title}" data-id="${item.id || ''}">
            <div class="suggestion-left">
                <i class="bi bi-search suggestion-icon"></i>
                <span class="suggestion-title">${item.title}</span>
            </div>
            <span class="suggestion-badge">${item.category || item.brand || 'Product'}</span>
        </div>
    `).join("");

    dropdown.classList.add("active");

    dropdown.querySelectorAll(".suggestion-item").forEach(el => {
        el.addEventListener("click", () => {
            const title = el.getAttribute("data-title");
            input.value = title;
            dropdown.classList.remove("active");
            if (window.location.pathname === "/products") {
                currentFilters.q = title;
                fetchCatalogProducts();
            } else {
                window.location.href = `/products?q=${encodeURIComponent(title)}`;
            }
        });
    });
}

// -------------------------------------------------------------
// Catalog Filters & Dynamic Rendering (for /products page)
// -------------------------------------------------------------
function initCatalogFilters() {
    const productsContainer = document.getElementById("catalogProductsGrid");
    if (!productsContainer) return;

    // Parse URL Query Params
    const urlParams = new URLSearchParams(window.location.search);
    currentFilters.q = urlParams.get("q") || "";
    currentFilters.category_id = urlParams.get("category_id") || "";
    currentFilters.platform_id = urlParams.get("platform_id") || "";
    currentFilters.min_price = urlParams.get("min_price") || "";
    currentFilters.max_price = urlParams.get("max_price") || "";

    const searchInput = document.getElementById("catalogSearchInput");
    if (searchInput && currentFilters.q) {
        searchInput.value = currentFilters.q;
    }

    // Category Radio/Checkbox listeners
    document.querySelectorAll(".category-filter-item").forEach(radio => {
        if (radio.value === currentFilters.category_id) radio.checked = true;
        radio.addEventListener("change", (e) => {
            currentFilters.category_id = e.target.value;
            fetchCatalogProducts();
        });
    });

    // Platform Filter listener
    document.querySelectorAll(".platform-filter-item").forEach(radio => {
        if (radio.value === currentFilters.platform_id) radio.checked = true;
        radio.addEventListener("change", (e) => {
            currentFilters.platform_id = e.target.value;
            fetchCatalogProducts();
        });
    });

    // Budget Tier Cards in Catalog
    document.querySelectorAll(".catalog-budget-pill").forEach(pill => {
        pill.addEventListener("click", () => {
            document.querySelectorAll(".catalog-budget-pill").forEach(p => p.classList.remove("active"));
            pill.classList.add("active");
            currentFilters.min_price = pill.getAttribute("data-min") || "";
            currentFilters.max_price = pill.getAttribute("data-max") || "";
            fetchCatalogProducts();
        });
    });

    // Custom Min/Max Price Inputs
    const minInput = document.getElementById("customMinPrice");
    const maxInput = document.getElementById("customMaxPrice");
    const applyPriceBtn = document.getElementById("applyPriceFilterBtn");

    if (applyPriceBtn) {
        applyPriceBtn.addEventListener("click", () => {
            currentFilters.min_price = minInput?.value || "";
            currentFilters.max_price = maxInput?.value || "";
            fetchCatalogProducts();
        });
    }

    // Sort Dropdown
    const sortSelect = document.getElementById("catalogSortSelect");
    if (sortSelect) {
        sortSelect.addEventListener("change", (e) => {
            const val = e.target.value;
            if (val === "price_asc") {
                currentFilters.sort_by = "price";
                currentFilters.sort_order = "asc";
            } else if (val === "price_desc") {
                currentFilters.sort_by = "price";
                currentFilters.sort_order = "desc";
            } else if (val === "rating") {
                currentFilters.sort_by = "rating";
                currentFilters.sort_order = "desc";
            } else if (val === "discount") {
                currentFilters.sort_by = "discount";
                currentFilters.sort_order = "desc";
            } else {
                currentFilters.sort_by = "relevance";
                currentFilters.sort_order = "asc";
            }
            fetchCatalogProducts();
        });
    }

    // Clear Filters Button
    const clearBtn = document.getElementById("clearFiltersBtn");
    if (clearBtn) {
        clearBtn.addEventListener("click", () => {
            currentFilters = {
                q: "",
                category_id: "",
                platform_id: "",
                min_price: "",
                max_price: "",
                min_rating: "",
                sort_by: "relevance",
                sort_order: "asc"
            };
            if (searchInput) searchInput.value = "";
            if (minInput) minInput.value = "";
            if (maxInput) maxInput.value = "";
            document.querySelectorAll(".category-filter-item, .platform-filter-item").forEach(r => r.checked = false);
            document.querySelectorAll(".catalog-budget-pill").forEach(p => p.classList.remove("active"));
            fetchCatalogProducts();
        });
    }

    // Initial Fetch
    fetchCatalogProducts();
}

async function fetchCatalogProducts() {
    const grid = document.getElementById("catalogProductsGrid");
    const countBadge = document.getElementById("resultsCountBadge");
    if (!grid) return;

    // Show Skeleton Loader
    grid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 4rem 1rem;">
            <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem; color: var(--primary-600);"></div>
            <p style="margin-top: 1rem; color: var(--text-muted); font-weight: 600;">Searching and comparing deals across platforms...</p>
        </div>
    `;

    // Build Query String
    const params = new URLSearchParams();
    if (currentFilters.q) params.set("q", currentFilters.q);
    if (currentFilters.category_id) params.set("category_id", currentFilters.category_id);
    if (currentFilters.platform_id) params.set("platform_id", currentFilters.platform_id);
    if (currentFilters.min_price) params.set("min_price", currentFilters.min_price);
    if (currentFilters.max_price) params.set("max_price", currentFilters.max_price);
    if (currentFilters.min_rating) params.set("min_rating", currentFilters.min_rating);
    if (currentFilters.sort_by) params.set("sort_by", currentFilters.sort_by);
    if (currentFilters.sort_order) params.set("sort_order", currentFilters.sort_order);

    try {
        const res = await fetch(`/api/products?${params.toString()}`);
        const data = await res.json();

        if (countBadge) {
            countBadge.textContent = `${data.total_count} products found`;
        }

        if (!data.products || data.products.length === 0) {
            grid.innerHTML = `
                <div class="empty-state" style="grid-column: 1 / -1;">
                    <i class="bi bi-search empty-state-icon"></i>
                    <h3>No Matching Products Found</h3>
                    <p>We couldn't find matches for your search filters. Try adjusting your budget, clearing brand filters, or searching for broader terms like "Phone", "Earbuds", or "Shoes".</p>
                    <button class="btn btn-outline" onclick="document.getElementById('clearFiltersBtn')?.click()">Clear All Filters</button>
                </div>
            `;
            return;
        }

        grid.innerHTML = data.products.map(p => renderProductCard(p)).join("");

        // Attach Card Button Listeners
        attachCardListeners();

    } catch (err) {
        console.error("Fetch catalog error:", err);
        grid.innerHTML = `
            <div class="empty-state" style="grid-column: 1 / -1;">
                <i class="bi bi-exclamation-triangle empty-state-icon text-danger"></i>
                <h3>Unable to Load Products</h3>
                <p>Failed to communicate with ShopFinder backend. Please check your connection and retry.</p>
                <button class="btn btn-primary" onclick="fetchCatalogProducts()">Retry</button>
            </div>
        `;
    }
}

function renderProductCard(p) {
    const formattedPrice = Number(p.min_price).toLocaleString("en-IN");
    const highestOffer = p.offers && p.offers.length > 0 ? Math.max(...p.offers.map(o => o.original_price)) : p.min_price * 1.3;
    const formattedOrig = Math.round(highestOffer).toLocaleString("en-IN");

    return `
        <div class="product-card">
            <div class="product-thumb-wrap">
                <img src="${p.image_url}" alt="${p.product_name}" class="product-thumb" loading="lazy">
                
                ${p.best_discount > 0 ? `
                    <div class="discount-badge">${p.best_discount}% OFF</div>
                ` : ''}

                ${p.best_platform ? `
                    <div class="best-deal-badge">
                        <i class="bi bi-patch-check-fill"></i> Best: ${p.best_platform}
                    </div>
                ` : ''}

                <button class="wishlist-btn-overlay" data-id="${p.id}" title="Add to Wishlist">
                    <i class="bi bi-heart"></i>
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

                <h3 class="product-title" title="${p.product_name}">${p.product_name}</h3>

                <div class="product-prices">
                    <span class="current-price">₹${formattedPrice}</span>
                    <span class="original-price">₹${formattedOrig}</span>
                </div>

                <div class="platform-offers-strip">
                    <span class="platform-offers-count">
                        <i class="bi bi-shop"></i> ${p.offers_count || 1} Platform Offers
                    </span>
                    ${p.max_savings > 0 ? `
                        <span class="savings-highlight">Save up to ₹${p.max_savings}</span>
                    ` : ''}
                </div>

                <div class="product-actions">
                    <button class="btn btn-outline btn-sm quick-compare-btn" data-id="${p.id}" data-name="${p.product_name}">
                        <i class="bi bi-arrow-left-right"></i> Compare
                    </button>
                    <a href="/compare?product_id=${p.id}" class="btn btn-primary btn-sm">
                        Deals <i class="bi bi-arrow-right"></i>
                    </a>
                </div>
            </div>
        </div>
    `;
}

function attachCardListeners() {
    // Wishlist Overlay Buttons
    document.querySelectorAll(".wishlist-btn-overlay").forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            const pid = btn.getAttribute("data-id");
            toggleWishlist(pid, btn);
        });
    });

    // Quick Compare Buttons
    document.querySelectorAll(".quick-compare-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            const pid = Number(btn.getAttribute("data-id"));
            const pname = btn.getAttribute("data-name");
            addToCompare(pid, pname);
        });
    });
}
