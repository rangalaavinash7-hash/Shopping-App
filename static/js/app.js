/**
 * ShopFinder: Global Application Logic
 * Handles theme toggling (Dark/Light), toast notifications,
 * wishlist interactions, and local compare tray.
 */

document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    initGlobalListeners();
    updateCompareTrayBadge();
});

// -------------------------------------------------------------
// Dark / Light Theme Toggle
// -------------------------------------------------------------
function initTheme() {
    const savedTheme = localStorage.getItem("shopfinder_theme") || "light";
    document.documentElement.setAttribute("data-theme", savedTheme);
    updateThemeIcon(savedTheme);

    const themeToggleBtn = document.getElementById("themeToggleBtn");
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", () => {
            const current = document.documentElement.getAttribute("data-theme");
            const newTheme = current === "dark" ? "light" : "dark";
            document.documentElement.setAttribute("data-theme", newTheme);
            localStorage.setItem("shopfinder_theme", newTheme);
            updateThemeIcon(newTheme);
            showToast(`Switched to ${newTheme} theme`, "info");
        });
    }
}

function updateThemeIcon(theme) {
    const icon = document.getElementById("themeToggleIcon");
    if (icon) {
        if (theme === "dark") {
            icon.className = "bi bi-sun-fill text-warning";
        } else {
            icon.className = "bi bi-moon-stars-fill";
        }
    }
}

// -------------------------------------------------------------
// Toast Notification Engine
// -------------------------------------------------------------
function showToast(message, type = "info") {
    let container = document.getElementById("toastContainer");
    if (!container) {
        container = document.createElement("div");
        container.id = "toastContainer";
        container.className = "toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;

    let iconClass = "bi-info-circle-fill text-primary";
    if (type === "success") iconClass = "bi-check-circle-fill text-success";
    if (type === "error") iconClass = "bi-exclamation-triangle-fill text-danger";

    toast.innerHTML = `
        <i class="bi ${iconClass}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(100%)";
        toast.style.transition = "all 0.3s ease";
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// -------------------------------------------------------------
// Wishlist Global Helper
// -------------------------------------------------------------
async function toggleWishlist(productId, btnElement) {
    try {
        const response = await fetch("/api/wishlist", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ product_id: productId })
        });

        if (response.status === 401) {
            showToast("Please login to save items to your wishlist.", "error");
            setTimeout(() => {
                window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`;
            }, 1000);
            return;
        }

        const data = await response.json();
        if (response.ok) {
            showToast(data.message, "success");
            if (btnElement) {
                btnElement.classList.toggle("active");
                btnElement.querySelector("i")?.classList.replace("bi-heart", "bi-heart-fill");
            }
        } else {
            showToast(data.error || "Failed to update wishlist", "error");
        }
    } catch (err) {
        console.error("Wishlist error:", err);
        showToast("Network error. Please try again.", "error");
    }
}

// -------------------------------------------------------------
// Side-by-Side Compare Tray (LocalStorage)
// -------------------------------------------------------------
function getCompareList() {
    try {
        return JSON.parse(localStorage.getItem("shopfinder_compare_items") || "[]");
    } catch (e) {
        return [];
    }
}

function addToCompare(productId, productName) {
    let list = getCompareList();
    if (list.includes(productId)) {
        showToast(`"${productName || 'Product'}" is already in comparison!`, "info");
        return;
    }
    if (list.length >= 4) {
        showToast("You can compare up to 4 products at once.", "error");
        return;
    }
    list.push(productId);
    localStorage.setItem("shopfinder_compare_items", JSON.stringify(list));
    updateCompareTrayBadge();
    showToast(`Added to compare! (${list.length}/4 items)`, "success");
}

function removeFromCompare(productId) {
    let list = getCompareList().filter(id => id !== productId);
    localStorage.setItem("shopfinder_compare_items", JSON.stringify(list));
    updateCompareTrayBadge();
}

function updateCompareTrayBadge() {
    const badge = document.getElementById("compareTrayCount");
    if (badge) {
        const count = getCompareList().length;
        badge.textContent = count;
        badge.style.display = count > 0 ? "flex" : "none";
    }
}

// -------------------------------------------------------------
// Global Listeners & Fallbacks
// -------------------------------------------------------------
function initGlobalListeners() {
    // Image fallback error listener
    document.addEventListener("error", (e) => {
        if (e.target.tagName.toLowerCase() === "img") {
            e.target.src = "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500";
        }
    }, true);
}
