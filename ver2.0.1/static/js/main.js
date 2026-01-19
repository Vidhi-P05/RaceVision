// F1 Analytics Platform - Main JavaScript

// Global season selector functionality
document.addEventListener('DOMContentLoaded', function() {
    const seasonSelector = document.getElementById('globalSeasonSelector');
    
    if (seasonSelector) {
        seasonSelector.addEventListener('change', function() {
            const selectedSeason = this.value;
            console.log('Season changed to:', selectedSeason);
            
            // You can add logic here to update charts dynamically
            // For example, fetch new data via AJAX
            updateChartsForSeason(selectedSeason);
        });
    }
});

// Function to update charts when season changes
function updateChartsForSeason(season) {
    // This would typically make an AJAX call to your Flask backend
    console.log('Updating charts for season:', season);
    
    // Example: fetch data and update Plotly charts
    // fetch(`/api/season-data/${season}`)
    //     .then(response => response.json())
    //     .then(data => {
    //         // Update your Plotly charts here
    //         Plotly.react('yourChartId', data.chartData);
    //     });
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add loading animation to cards on page load
function animateCards() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'all 0.5s ease';
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 50);
        }, index * 50);
    });
}

// Initialize animations when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', animateCards);
} else {
    animateCards();
}

// Utility function for formatting numbers
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Utility function for creating responsive Plotly charts
function createResponsivePlotlyChart(elementId, data, layout, config = {}) {
    const defaultConfig = {
        responsive: true,
        displayModeBar: false,
        ...config
    };
    
    const defaultLayout = {
        template: 'plotly_dark',
        paper_bgcolor: '#161A20',
        plot_bgcolor: '#0F1115',
        font: { color: '#EAEAEA' },
        ...layout
    };
    
    Plotly.newPlot(elementId, data, defaultLayout, defaultConfig);
}

// Handle form submissions with loading states
function handleFormSubmit(formId, callback) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Processing...';
        
        callback(new FormData(form))
            .then(() => {
                submitBtn.innerHTML = '<i class="bi bi-check-circle me-2"></i>Success!';
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 2000);
            })
            .catch(error => {
                console.error('Error:', error);
                submitBtn.innerHTML = '<i class="bi bi-x-circle me-2"></i>Error';
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 2000);
            });
    });
}

// Toast notification system
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// Export functions for use in other scripts
window.F1Analytics = {
    updateChartsForSeason,
    formatNumber,
    createResponsivePlotlyChart,
    handleFormSubmit,
    showToast
};
