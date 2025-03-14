// Update current time in the header
function updateTime() {
    const timeElement = document.getElementById('current-time');
    const now = new Date();
    timeElement.textContent = now.toLocaleTimeString();
}

// Update time every second
setInterval(updateTime, 1000);
updateTime();

// Handle analysis form submission
function runAnalysis() {
    const button = document.querySelector('#run-analysis-btn');
    const statusElement = document.querySelector('#analysis-status');
    
    if (button) {
        button.addEventListener('click', async () => {
            try {
                button.disabled = true;
                button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running Analysis...';
                statusElement.innerHTML = 'Analysis in progress...';
                
                const response = await fetch('/api/run-analysis', {
                    method: 'POST'
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    statusElement.innerHTML = '<div class="alert alert-success">Analysis completed successfully!</div>';
                } else {
                    throw new Error(result.message);
                }
            } catch (error) {
                statusElement.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
            } finally {
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-play"></i> Run Analysis';
            }
        });
    }
}

// Load visualizations
async function loadVisualizations() {
    const container = document.querySelector('#visualizations-container');
    
    if (container) {
        try {
            container.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin fa-3x"></i></div>';
            
            const response = await fetch('/api/get-visualizations');
            const result = await response.json();
            
            if (result.status === 'success') {
                // Render visualizations using the data
                renderVisualizations(result.data);
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            container.innerHTML = `<div class="alert alert-danger">Error loading visualizations: ${error.message}</div>`;
        }
    }
}

// Initialize page-specific features
document.addEventListener('DOMContentLoaded', () => {
    // Initialize analysis page features
    runAnalysis();
    
    // Initialize visualizations page features
    if (window.location.pathname === '/visualizations') {
        loadVisualizations();
    }
    
    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
}); 