/**
 * ShopFinder: Product Comparison & Price History Engine
 * Manages side-by-side platform offers, multi-product matrix,
 * difference highlighting, and price trend charting.
 */

let priceChartInstance = null;

document.addEventListener("DOMContentLoaded", () => {
    initComparePage();
});

async function initComparePage() {
    const urlParams = new URLSearchParams(window.location.search);
    const singleProductId = urlParams.get("product_id");
    const multiProductIds = urlParams.get("ids");

    if (singleProductId) {
        // Mode 1: Single Product across Shopping Platforms (Amazon, Flipkart, etc.)
        await loadPlatformOfferComparison(singleProductId);
    } else if (multiProductIds) {
        // Mode 2: Multi-product side-by-side
        await loadMultiProductComparison(multiProductIds.split(","));
    } else {
        // Mode 3: Check LocalStorage compare tray
        const stored = getCompareList();
        if (stored.length > 0) {
            await loadMultiProductComparison(stored);
        } else {
            showEmptyCompareState();
        }
    }
}

function showEmptyCompareState() {
    const container = document.getElementById("compareContentArea");
    if (!container) return;

    container.innerHTML = `
        <div class="empty-state">
            <i class="bi bi-arrow-left-right empty-state-icon"></i>
            <h3>No Products Selected for Comparison</h3>
            <p>Search for any product and click the "Compare" button on product cards, or pick a featured product below to see real-time price comparisons across shopping platforms.</p>
            <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
                <a href="/products" class="btn btn-primary">Browse All Products</a>
                <a href="/compare?product_id=1" class="btn btn-outline">Compare boAt Airdopes 141</a>
                <a href="/compare?product_id=3" class="btn btn-outline">Compare iPhone 15</a>
            </div>
        </div>
    `;
}

// -------------------------------------------------------------
// Mode 1: Single Product Offers Comparison Across Platforms
// -------------------------------------------------------------
async function loadPlatformOfferComparison(productId) {
    const container = document.getElementById("compareContentArea");
    if (!container) return;

    container.innerHTML = `
        <div style="text-align: center; padding: 4rem 1rem;">
            <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem; color: var(--primary-600);"></div>
            <p style="margin-top: 1rem; color: var(--text-muted); font-weight: 600;">Comparing live platform offers across Amazon, Flipkart, Meesho, Croma...</p>
        </div>
    `;

    try {
        const res = await fetch(`/api/offers/compare?product_id=${productId}`);
        if (!res.ok) throw new Error("Product comparison failed");
        const data = await res.json();

        renderPlatformOffersView(container, data);
        if (data.offers && data.offers.length > 0) {
            loadPriceHistoryChart(data.offers[0].id);
        }
    } catch (err) {
        console.error("Compare error:", err);
        container.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-exclamation-triangle empty-state-icon text-danger"></i>
                <h3>Unable to Load Comparison</h3>
                <p>Failed to retrieve pricing data. Please try again.</p>
                <a href="/products" class="btn btn-primary">Back to Catalog</a>
            </div>
        `;
    }
}

function renderPlatformOffersView(container, data) {
    const bestDeal = data.best_deal;
    const offers = data.offers;

    container.innerHTML = `
        <!-- Product Header Bar -->
        <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: var(--radius-lg); padding: 1.5rem; margin-bottom: 2rem; display: flex; align-items: center; justify-content: space-between; gap: 1.5rem; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 1.25rem;">
                <img src="${data.image_url}" alt="${data.product_name}" style="width: 75px; height: 75px; border-radius: var(--radius-md); object-fit: cover;">
                <div>
                    <span style="font-size: 0.8rem; font-weight: 700; color: var(--primary-600); text-transform: uppercase;">${data.brand}</span>
                    <h2 style="font-size: 1.35rem; margin-top: 0.15rem;">${data.product_name}</h2>
                    <span style="font-size: 0.85rem; color: var(--text-muted);">${offers.length} Platform Offers Verified</span>
                </div>
            </div>

            ${data.total_savings > 0 ? `
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid var(--accent-emerald); border-radius: var(--radius-md); padding: 0.75rem 1.25rem; text-align: right;">
                    <div style="font-size: 0.8rem; color: var(--text-muted); font-weight: 600;">Maximum Price Difference</div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: var(--accent-emerald);">Save ₹${data.total_savings.toLocaleString('en-IN')} (${data.savings_percentage}%)</div>
                </div>
            ` : ''}
        </div>

        <!-- Offers Cards Grid -->
        <h3 style="font-size: 1.25rem; margin-bottom: 1.25rem;">Live Platform Offers Side-by-Side</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.25rem; margin-bottom: 3rem;">
            ${offers.map(offer => {
                const isBest = (bestDeal && offer.id === bestDeal.id);
                return `
                    <div style="background: var(--bg-surface); border: 2px solid ${isBest ? 'var(--accent-emerald)' : 'var(--border-color)'}; border-radius: var(--radius-lg); padding: 1.5rem; position: relative; box-shadow: ${isBest ? 'var(--shadow-lg)' : 'var(--shadow-sm)'}; display: flex; flex-direction: column;">
                        
                        ${isBest ? `
                            <div style="position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: var(--gradient-badge); color: #fff; font-size: 0.75rem; font-weight: 700; padding: 0.25rem 0.75rem; border-radius: var(--radius-full); box-shadow: 0 4px 10px rgba(16, 185, 129, 0.4); display: flex; align-items: center; gap: 0.3rem;">
                                <i class="bi bi-trophy-fill"></i> LOWEST VERIFIED PRICE
                            </div>
                        ` : ''}

                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; margin-top: ${isBest ? '0.5rem' : '0'};">
                            <span style="font-size: 1.15rem; font-weight: 800; color: var(--text-main);">${offer.platform_name}</span>
                            <span style="font-size: 0.75rem; background: var(--bg-surface-hover); padding: 0.2rem 0.5rem; border-radius: var(--radius-sm); color: var(--text-muted); font-weight: 600;">
                                ${offer.data_source}
                            </span>
                        </div>

                        <div style="margin-bottom: 1rem;">
                            <div style="font-size: 1.75rem; font-weight: 800; font-family: 'Outfit', sans-serif;">
                                ₹${offer.current_price.toLocaleString('en-IN')}
                            </div>
                            <div style="font-size: 0.85rem; color: var(--text-light); text-decoration: line-through;">
                                MRP ₹${offer.original_price.toLocaleString('en-IN')} (${offer.discount_percentage}% OFF)
                            </div>
                        </div>

                        <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem; display: flex; justify-content: space-between;">
                            <span>Delivery:</span>
                            <span style="font-weight: 600; color: ${offer.delivery_charge === 0 ? 'var(--accent-emerald)' : 'var(--text-main)'};">
                                ${offer.delivery_charge === 0 ? 'FREE Delivery' : '₹' + offer.delivery_charge}
                            </span>
                        </div>

                        <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1.25rem; display: flex; justify-content: space-between;">
                            <span>Total Verified Cost:</span>
                            <span style="font-weight: 800; color: ${isBest ? 'var(--accent-emerald)' : 'var(--text-main)'};">
                                ₹${offer.total_cost.toLocaleString('en-IN')}
                            </span>
                        </div>

                        <div style="margin-top: auto; display: flex; flex-direction: column; gap: 0.5rem;">
                            <a href="${offer.product_url}" target="_blank" rel="noopener noreferrer" class="btn ${isBest ? 'btn-primary' : 'btn-outline'} btn-sm" style="width: 100%;">
                                View on ${offer.platform_name} <i class="bi bi-box-arrow-up-right"></i>
                            </a>
                            <button class="btn btn-outline btn-sm set-alert-btn" data-offer-id="${offer.id}" data-current-price="${offer.current_price}" style="font-size: 0.78rem;">
                                <i class="bi bi-bell"></i> Set Price Alert
                            </button>
                        </div>
                    </div>
                `;
            }).join("")}
        </div>

        <!-- Historical Price Chart Section -->
        <div class="price-chart-card">
            <div class="chart-header">
                <div>
                    <h3 style="font-size: 1.25rem;">Price History & Trend Analysis</h3>
                    <p style="font-size: 0.85rem; color: var(--text-muted);">Timestamped price observations over the past 30 days</p>
                </div>
                <div id="priceTrendIndicator" class="price-drop-indicator">
                    <i class="bi bi-graph-down-arrow"></i> Historical Tracking Active
                </div>
            </div>
            <div style="position: relative; height: 280px; width: 100%;">
                <canvas id="priceHistoryCanvas"></canvas>
            </div>
        </div>
    `;

    // Attach Alert listeners
    attachAlertListeners();
}

// -------------------------------------------------------------
// Mode 2: Multi-Product Side-by-Side Comparison
// -------------------------------------------------------------
async function loadMultiProductComparison(productIds) {
    const container = document.getElementById("compareContentArea");
    if (!container) return;

    container.innerHTML = `
        <div style="text-align: center; padding: 4rem 1rem;">
            <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;"></div>
            <p style="margin-top: 1rem; color: var(--text-muted); font-weight: 600;">Executing Algorithmic Value-for-Money Analysis...</p>
        </div>
    `;

    try {
        const res = await fetch(`/api/products/compare-multiple?ids=${productIds.join(",")}`);
        if (!res.ok) throw new Error("Comparison failed");
        const data = await res.json();

        renderMultiProductTable(container, data);
    } catch (err) {
        console.error("Multi-product compare error:", err);
        showEmptyCompareState();
    }
}

function renderMultiProductTable(container, data) {
    const products = data.products;
    const winnerId = data.winner_product_id;

    container.innerHTML = `
        <!-- Algorithmic Recommendation Banner -->
        ${data.winner_name ? `
            <div style="background: linear-gradient(135deg, rgba(124, 58, 237, 0.12) 0%, rgba(79, 70, 229, 0.08) 100%); border: 1.5px solid var(--primary-500); border-radius: var(--radius-lg); padding: 1.25rem 1.75rem; margin-bottom: 2rem; display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap;">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="width: 44px; height: 44px; border-radius: 50%; background: var(--gradient-hero); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 1.25rem;">
                        <i class="bi bi-award-fill"></i>
                    </div>
                    <div>
                        <span style="font-size: 0.8rem; font-weight: 700; color: var(--primary-600); text-transform: uppercase;">ShopFinder Recommendation Engine</span>
                        <h3 style="font-size: 1.15rem; margin-top: 0.1rem;">Top Pick: ${data.winner_name}</h3>
                        <p style="font-size: 0.85rem; color: var(--text-muted);">${data.winner_reason}</p>
                    </div>
                </div>
            </div>
        ` : ''}

        <!-- Comparison Table -->
        <div class="compare-matrix-wrapper">
            <table class="compare-table">
                <thead>
                    <tr>
                        <th class="compare-attr-header">Product Attribute</th>
                        ${products.map(p => `
                            <th style="min-width: 240px; text-align: center; ${p.id === winnerId ? 'background: rgba(124, 58, 237, 0.05);' : ''}">
                                <img src="${p.image_url}" alt="${p.product_name}" style="width: 120px; height: 120px; margin: 0 auto 0.75rem; object-fit: cover; border-radius: var(--radius-md);">
                                <h4 style="font-size: 1rem; margin-bottom: 0.25rem;">${p.product_name}</h4>
                                <span style="font-size: 0.8rem; color: var(--text-muted);">${p.brand}</span>
                                ${p.id === winnerId ? `
                                    <div class="lowest-verified-badge"><i class="bi bi-star-fill"></i> Best Overall Value</div>
                                ` : ''}
                            </th>
                        `).join("")}
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="compare-attr-header">Lowest Verified Price</td>
                        ${products.map(p => `
                            <td style="text-align: center; font-size: 1.25rem; font-weight: 800; color: var(--text-main); ${p.id === winnerId ? 'background: rgba(124, 58, 237, 0.05);' : ''}">
                                ₹${p.min_price.toLocaleString('en-IN')}
                            </td>
                        `).join("")}
                    </tr>
                    <tr>
                        <td class="compare-attr-header">Best Platform Offer</td>
                        ${products.map(p => `
                            <td style="text-align: center; font-weight: 600; color: var(--primary-600); ${p.id === winnerId ? 'background: rgba(124, 58, 237, 0.05);' : ''}">
                                ${p.best_platform || 'Multiple'}
                            </td>
                        `).join("")}
                    </tr>
                    <tr>
                        <td class="compare-attr-header">Rating & Reviews</td>
                        ${products.map(p => `
                            <td style="text-align: center; font-weight: 600; ${p.id === winnerId ? 'background: rgba(124, 58, 237, 0.05);' : ''}">
                                ★ ${p.best_rating || '4.2'} / 5.0
                            </td>
                        `).join("")}
                    </tr>
                    <tr>
                        <td class="compare-attr-header">Verified Max Discount</td>
                        ${products.map(p => `
                            <td style="text-align: center; font-weight: 700; color: var(--accent-emerald); ${p.id === winnerId ? 'background: rgba(124, 58, 237, 0.05);' : ''}">
                                ${p.best_discount || 0}% OFF
                            </td>
                        `).join("")}
                    </tr>
                    <tr>
                        <td class="compare-attr-header">Specifications</td>
                        ${products.map(p => `
                            <td style="font-size: 0.85rem; color: var(--text-muted); ${p.id === winnerId ? 'background: rgba(124, 58, 237, 0.05);' : ''}">
                                ${p.specifications || p.description}
                            </td>
                        `).join("")}
                    </tr>
                    <tr>
                        <td class="compare-attr-header">Action</td>
                        ${products.map(p => `
                            <td style="text-align: center; ${p.id === winnerId ? 'background: rgba(124, 58, 237, 0.05);' : ''}">
                                <a href="/compare?product_id=${p.id}" class="btn btn-primary btn-sm">
                                    View All Platform Deals <i class="bi bi-arrow-right"></i>
                                </a>
                            </td>
                        `).join("")}
                    </tr>
                </tbody>
            </table>
        </div>
    `;
}

// -------------------------------------------------------------
// Chart.js Historical Price Renderer
// -------------------------------------------------------------
async function loadPriceHistoryChart(offerId) {
    try {
        const res = await fetch(`/api/price-history/${offerId}`);
        const data = await res.json();

        const canvas = document.getElementById("priceHistoryCanvas");
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        const labels = data.history.map(h => h.recorded_at.split(" ")[0]);
        const prices = data.history.map(h => h.recorded_price);

        if (priceChartInstance) {
            priceChartInstance.destroy();
        }

        // Check if Chart.js is loaded from CDN
        if (typeof Chart !== "undefined") {
            priceChartInstance = new Chart(ctx, {
                type: "line",
                data: {
                    labels: labels,
                    datasets: [{
                        label: `${data.product_name} (${data.platform_name}) Price (₹)`,
                        data: prices,
                        borderColor: "#7c3aed",
                        backgroundColor: "rgba(124, 58, 237, 0.1)",
                        fill: true,
                        tension: 0.35,
                        pointBackgroundColor: "#7c3aed",
                        pointRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: true }
                    },
                    scales: {
                        y: {
                            ticks: {
                                callback: function(val) { return "₹" + val; }
                            }
                        }
                    }
                }
            });
        }
    } catch (err) {
        console.error("Price history error:", err);
    }
}

// -------------------------------------------------------------
// Price Alert Modal Integration
// -------------------------------------------------------------
function attachAlertListeners() {
    document.querySelectorAll(".set-alert-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const offerId = btn.getAttribute("data-offer-id");
            const currentPrice = btn.getAttribute("data-current-price");
            openPriceAlertModal(offerId, currentPrice);
        });
    });
}

function openPriceAlertModal(offerId, currentPrice) {
    let modal = document.getElementById("priceAlertModal");
    if (!modal) {
        modal = document.createElement("div");
        modal.id = "priceAlertModal";
        modal.className = "modal-overlay";
        modal.innerHTML = `
            <div class="modal-card">
                <div class="modal-header">
                    <h3 style="font-size: 1.15rem;"><i class="bi bi-bell-fill text-primary"></i> Set Target Price Alert</h3>
                    <button class="btn-icon" id="closeAlertModalBtn"><i class="bi bi-x-lg"></i></button>
                </div>
                <div class="modal-body">
                    <p style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 1.25rem;">
                        Get notified when this item drops below your target budget. Current verified price: <strong>₹${Number(currentPrice).toLocaleString('en-IN')}</strong>.
                    </p>
                    <div class="form-group">
                        <label class="form-label">Your Target Price (₹)</label>
                        <input type="number" id="alertTargetPriceInput" class="form-control" value="${Math.round(currentPrice * 0.9)}">
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-outline" id="cancelAlertModalBtn">Cancel</button>
                    <button class="btn btn-primary" id="saveAlertBtn">Save Price Alert</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        document.getElementById("closeAlertModalBtn").onclick = () => modal.classList.remove("active");
        document.getElementById("cancelAlertModalBtn").onclick = () => modal.classList.remove("active");
    }

    modal.classList.add("active");

    document.getElementById("saveAlertBtn").onclick = async () => {
        const target = document.getElementById("alertTargetPriceInput").value;
        if (!target || Number(target) <= 0) {
            showToast("Please enter a valid target price.", "error");
            return;
        }

        try {
            const res = await fetch("/api/price-alerts", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ offer_id: offerId, target_price: target })
            });

            if (res.status === 401) {
                showToast("Please login to set price alerts.", "error");
                setTimeout(() => window.location.href = "/login", 1000);
                return;
            }

            const data = await res.json();
            modal.classList.remove("active");
            showToast(data.message, "success");
        } catch (e) {
            showToast("Failed to create price alert.", "error");
        }
    };
}
