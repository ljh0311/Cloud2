/**
 * Social Media Analyzer - Visualizations
 * Handles loading and displaying visualizations of analysis results
 */

class VisualizationManager {
    constructor() {
        // Chart objects
        this.charts = {
            sentiment: null,
            trend: null,
            traffic: null,
            location: null,
            topics: null
        };
        
        // DOM elements
        this.elements = {
            analysisSelect: document.getElementById('analysis-select'),
            vizTypeSelect: document.getElementById('viz-type-select'),
            timeframeSelect: document.getElementById('timeframe-select'),
            loadingIndicator: document.getElementById('loading-indicator'),
            noDataMessage: document.getElementById('no-data-message'),
            visualizationsContainer: document.getElementById('visualizations-container'),
            vizCards: document.querySelectorAll('.viz-card')
        };
        
        // Status message elements
        this.statusElements = {
            analysisInfo: document.getElementById('analysis-file-info'),
            lastUpdated: document.getElementById('last-updated'),
            datasetInfo: document.getElementById('dataset-info')
        };
        
        // Initialize
        this.init();
    }
    
    /**
     * Initialize the visualization manager
     */
    init() {
        // Initialize tooltips
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        if (tooltips.length > 0) {
            [...tooltips].map(tooltipEl => new bootstrap.Tooltip(tooltipEl));
        }
        
        // Initialize charts
        this.initCharts();
        
        // Load analysis files
        this.loadAnalysisFiles();
        
        // Add event listeners
        if (this.elements.analysisSelect) {
            this.elements.analysisSelect.addEventListener('change', () => this.loadVisualizations());
        }
        
        if (this.elements.vizTypeSelect) {
            this.elements.vizTypeSelect.addEventListener('change', () => this.filterVisualizations());
        }
        
        if (this.elements.timeframeSelect) {
            this.elements.timeframeSelect.addEventListener('change', () => this.loadVisualizations());
        }
        
        // Handle refresh button
        const refreshBtn = document.getElementById('refresh-analyses-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadAnalysisFiles());
        }
    }
    
    /**
     * Initialize chart objects
     */
    initCharts() {
        // Sentiment Chart (Pie)
        const sentimentCtx = document.getElementById('sentiment-chart');
        if (sentimentCtx) {
            this.charts.sentiment = new Chart(sentimentCtx.getContext('2d'), {
                type: 'pie',
                data: {
                    labels: ['Positive', 'Neutral', 'Negative'],
                    datasets: [{
                        data: [0, 0, 0],
                        backgroundColor: ['#51cf66', '#339af0', '#ff6b6b']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right'
                        },
                        title: {
                            display: true,
                            text: 'Sentiment Distribution'
                        }
                    }
                }
            });
        }
        
        // Trend Chart (Line)
        const trendCtx = document.getElementById('trend-chart');
        if (trendCtx) {
            this.charts.trend = new Chart(trendCtx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'Posts',
                            data: [],
                            borderColor: '#339af0',
                            backgroundColor: 'rgba(51, 154, 240, 0.1)',
                            tension: 0.2,
                            fill: true
                        },
                        {
                            label: 'Comments',
                            data: [],
                            borderColor: '#51cf66',
                            backgroundColor: 'rgba(81, 207, 102, 0.1)',
                            tension: 0.2,
                            fill: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Count'
                            }
                        }
                    }
                }
            });
        }
        
        // Traffic Chart (Bar)
        const trafficCtx = document.getElementById('traffic-chart');
        if (trafficCtx) {
            this.charts.traffic = new Chart(trafficCtx.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Incidents',
                        data: [],
                        backgroundColor: '#ff6b6b'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Incident Type'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Count'
                            }
                        }
                    }
                }
            });
        }
        
        // Location Chart (Polar Area)
        const locationCtx = document.getElementById('location-chart');
        if (locationCtx) {
            this.charts.location = new Chart(locationCtx.getContext('2d'), {
                type: 'polarArea',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.7)',
                            'rgba(54, 162, 235, 0.7)',
                            'rgba(255, 206, 86, 0.7)',
                            'rgba(75, 192, 192, 0.7)',
                            'rgba(153, 102, 255, 0.7)',
                            'rgba(255, 159, 64, 0.7)',
                            'rgba(199, 199, 199, 0.7)',
                            'rgba(83, 102, 255, 0.7)',
                            'rgba(40, 159, 64, 0.7)',
                            'rgba(210, 199, 199, 0.7)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right'
                        }
                    }
                }
            });
        }
        
        // Topic Distribution Chart (Doughnut)
        const topicsCtx = document.getElementById('topic-distribution-chart');
        if (topicsCtx) {
            this.charts.topics = new Chart(topicsCtx.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: [
                            '#4bc0c0',
                            '#ff6384',
                            '#ffcd56',
                            '#537bc4',
                            '#96a2b4',
                            '#f7931e',
                            '#36a2eb',
                            '#f44336',
                            '#9c27b0',
                            '#2196f3'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right'
                        }
                    }
                }
            });
        }
    }
    
    /**
     * Load available analysis files
     */
    loadAnalysisFiles() {
        if (this.elements.loadingIndicator) {
            this.elements.loadingIndicator.style.display = 'block';
        }
        
        if (this.elements.noDataMessage) {
            this.elements.noDataMessage.style.display = 'none';
        }
        
        fetch('/api/get-analysis-files')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                this.handleAnalysisFilesResponse(data);
            })
            .catch(error => {
                console.error('Error loading analysis files:', error);
                this.showError(`Failed to load analysis files: ${error.message}`);
            })
            .finally(() => {
                if (this.elements.loadingIndicator) {
                    this.elements.loadingIndicator.style.display = 'none';
                }
            });
    }
    
    /**
     * Handle the response from the analysis files API
     */
    handleAnalysisFilesResponse(response) {
        if (!this.elements.analysisSelect) return;
        
        if (response.status === 'success' && response.files && response.files.length) {
            // Clear dropdown
            this.elements.analysisSelect.innerHTML = '';
            
            // Add default option
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Select an analysis...';
            this.elements.analysisSelect.appendChild(defaultOption);
            
            // Group files by dataset
            const filesByDataset = {};
            response.files.forEach(file => {
                const dataset = file.filename.split('_')[0] || 'Unknown';
                if (!filesByDataset[dataset]) {
                    filesByDataset[dataset] = [];
                }
                filesByDataset[dataset].push(file);
            });
            
            // Add options grouped by dataset
            Object.keys(filesByDataset).forEach(dataset => {
                const optgroup = document.createElement('optgroup');
                optgroup.label = dataset.charAt(0).toUpperCase() + dataset.slice(1);
                
                filesByDataset[dataset].forEach(file => {
                    const option = document.createElement('option');
                    option.value = file.path;
                    
                    // Extract date from filename or use creation date
                    let dateDisplay = new Date(file.created * 1000).toLocaleDateString();
                    const dateMatch = file.filename.match(/(\d{8})_(\d{6})/);
                    if (dateMatch) {
                        const year = dateMatch[1].substring(0, 4);
                        const month = dateMatch[1].substring(4, 6);
                        const day = dateMatch[1].substring(6, 8);
                        const hour = dateMatch[2].substring(0, 2);
                        const minute = dateMatch[2].substring(2, 4);
                        dateDisplay = `${year}-${month}-${day} ${hour}:${minute}`;
                    }
                    
                    option.textContent = `${file.filename} (${dateDisplay})`;
                    option.dataset.created = file.created;
                    option.dataset.size = file.size;
                    optgroup.appendChild(option);
                });
                
                this.elements.analysisSelect.appendChild(optgroup);
            });
            
            // If there's at least one file, select it and load visualizations
            if (response.files.length > 0) {
                this.elements.analysisSelect.value = response.files[0].path;
                this.loadVisualizations();
            }
        } else {
            // No files found
            this.elements.analysisSelect.innerHTML = '<option value="">No analysis files found</option>';
            this.showNoData('No analysis files available. Run an analysis first.');
        }
    }
    
    /**
     * Load visualizations for the selected analysis file
     */
    loadVisualizations() {
        const filePath = this.elements.analysisSelect ? this.elements.analysisSelect.value : null;
        const vizType = this.elements.vizTypeSelect ? this.elements.vizTypeSelect.value : 'all';
        const timeframe = this.elements.timeframeSelect ? this.elements.timeframeSelect.value : '30d';
        
        if (!filePath) {
            this.showNoData('Select an analysis file to view visualizations.');
            // Hide file info section if no file selected
            const fileInfoSection = document.getElementById('file-info-section');
            if (fileInfoSection) {
                fileInfoSection.style.display = 'none';
            }
            return;
        }
        
        // Show loading indicator
        if (this.elements.loadingIndicator) {
            this.elements.loadingIndicator.style.display = 'block';
        }
        
        if (this.elements.noDataMessage) {
            this.elements.noDataMessage.style.display = 'none';
        }
        
        if (this.elements.visualizationsContainer) {
            this.elements.visualizationsContainer.style.display = 'none';
        }
        
        // Update file info if available
        this.updateFileInfo();
        
        // Fetch visualization data
        fetch(`/api/get-visualizations?file=${filePath}&type=${vizType}&timeframe=${timeframe}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                this.handleVisualizationDataResponse(data);
            })
            .catch(error => {
                console.error('Error loading visualizations:', error);
                this.showError(`Failed to load visualizations: ${error.message}`);
            })
            .finally(() => {
                if (this.elements.loadingIndicator) {
                    this.elements.loadingIndicator.style.display = 'none';
                }
            });
    }
    
    /**
     * Handle the response from the visualization data API
     */
    handleVisualizationDataResponse(response) {
        if (response.status === 'success' && response.data) {
            this.updateCharts(response.data);
            this.filterVisualizations();
            
            if (this.elements.visualizationsContainer) {
                this.elements.visualizationsContainer.style.display = 'block';
            }
        } else {
            const errorMsg = response.message || 'No visualization data available.';
            this.showError(errorMsg);
        }
    }
    
    /**
     * Update charts with new data
     */
    updateCharts(data) {
        // Update Sentiment Chart
        if (data.sentiment_analysis && this.charts.sentiment) {
            const sentimentData = data.sentiment_analysis;
            const positive = sentimentData.positive || 0;
            const neutral = sentimentData.neutral || 0;
            const negative = sentimentData.negative || 0;
            
            this.charts.sentiment.data.datasets[0].data = [positive, neutral, negative];
            this.charts.sentiment.update();
        }
        
        // Update Trend Chart
        if (data.trend_analysis && this.charts.trend) {
            const trendData = data.trend_analysis;
            const labels = trendData.dates || [];
            const postCounts = trendData.post_counts || [];
            const commentCounts = trendData.comment_counts || [];
            
            this.charts.trend.data.labels = labels;
            this.charts.trend.data.datasets[0].data = postCounts;
            this.charts.trend.data.datasets[1].data = commentCounts;
            this.charts.trend.update();
        }
        
        // Update Traffic Chart
        if (data.traffic_analysis && this.charts.traffic) {
            const trafficData = data.traffic_analysis;
            const incidentTypes = trafficData.incident_types || [];
            const incidentCounts = trafficData.incident_counts || [];
            
            this.charts.traffic.data.labels = incidentTypes;
            this.charts.traffic.data.datasets[0].data = incidentCounts;
            this.charts.traffic.update();
        }
        
        // Update Location Chart
        if (data.location_analysis && this.charts.location) {
            const locationData = data.location_analysis;
            const locations = locationData.locations || [];
            const locationCounts = locationData.counts || [];
            
            this.charts.location.data.labels = locations;
            this.charts.location.data.datasets[0].data = locationCounts;
            this.charts.location.update();
        }
        
        // Update Topic Distribution Chart
        if (data.topic_analysis && this.charts.topics) {
            const topicData = data.topic_analysis;
            const topics = topicData.topics || [];
            const topicCounts = topicData.counts || [];
            
            this.charts.topics.data.labels = topics.map((t, i) => `Topic ${i+1}`);
            this.charts.topics.data.datasets[0].data = topicCounts;
            this.charts.topics.update();
            
            // Update topic keywords
            const topicKeywordsEl = document.getElementById('topic-keywords');
            if (topicKeywordsEl && topicData.keywords) {
                topicKeywordsEl.innerHTML = '';
                
                topics.forEach((topic, i) => {
                    const keywords = topicData.keywords[i] || [];
                    
                    const topicDiv = document.createElement('div');
                    topicDiv.className = 'mb-3';
                    
                    const topicHeading = document.createElement('h6');
                    topicHeading.textContent = `Topic ${i+1}`;
                    topicDiv.appendChild(topicHeading);
                    
                    const keywordsList = document.createElement('div');
                    keywordsList.className = 'topic-keywords small';
                    
                    keywords.forEach(keyword => {
                        const badge = document.createElement('span');
                        badge.className = 'badge bg-light text-dark me-1 mb-1';
                        badge.textContent = keyword;
                        keywordsList.appendChild(badge);
                    });
                    
                    topicDiv.appendChild(keywordsList);
                    topicKeywordsEl.appendChild(topicDiv);
                });
            }
        }
    }
    
    /**
     * Filter visualizations based on selected type
     */
    filterVisualizations() {
        const vizType = this.elements.vizTypeSelect ? this.elements.vizTypeSelect.value : 'all';
        
        if (this.elements.vizCards) {
            this.elements.vizCards.forEach(card => {
                const cardType = card.getAttribute('data-viz-type');
                if (vizType === 'all' || vizType === cardType) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }
    }
    
    /**
     * Update file information display
     */
    updateFileInfo() {
        const fileInfoSection = document.getElementById('file-info-section');
        if (!this.elements.analysisSelect) return;
        
        const select = this.elements.analysisSelect;
        const option = select.options[select.selectedIndex];
        
        if (option && option.value) {
            const filename = option.textContent.split(' (')[0];
            const created = option.dataset.created;
            const size = option.dataset.size;
            
            // Extract dataset name
            const datasetMatch = filename.match(/^([a-zA-Z]+)_/);
            const dataset = datasetMatch ? datasetMatch[1] : 'Unknown';
            
            // Format file size
            const formattedSize = this.formatFileSize(size);
            
            // Format date
            const createdDate = created ? new Date(created * 1000).toLocaleString() : 'Unknown';
            
            // Update elements
            if (this.statusElements.analysisInfo) {
                this.statusElements.analysisInfo.textContent = filename;
            }
            
            if (this.statusElements.lastUpdated) {
                this.statusElements.lastUpdated.textContent = createdDate;
            }
            
            if (this.statusElements.datasetInfo) {
                this.statusElements.datasetInfo.textContent = dataset.charAt(0).toUpperCase() + dataset.slice(1);
            }
            
            // Show the file info section
            if (fileInfoSection) {
                fileInfoSection.style.display = 'block';
            }
        } else {
            // No file selected
            if (this.statusElements.analysisInfo) {
                this.statusElements.analysisInfo.textContent = 'No file selected';
            }
            
            if (this.statusElements.lastUpdated) {
                this.statusElements.lastUpdated.textContent = 'N/A';
            }
            
            if (this.statusElements.datasetInfo) {
                this.statusElements.datasetInfo.textContent = 'N/A';
            }
            
            // Hide the file info section
            if (fileInfoSection) {
                fileInfoSection.style.display = 'none';
            }
        }
    }
    
    /**
     * Format file size for display
     */
    formatFileSize(size) {
        if (!size) return 'Unknown';
        
        const kb = size / 1024;
        if (kb < 1024) {
            return `${kb.toFixed(2)} KB`;
        } else {
            const mb = kb / 1024;
            return `${mb.toFixed(2)} MB`;
        }
    }
    
    /**
     * Show error message
     */
    showError(message) {
        if (this.elements.noDataMessage) {
            this.elements.noDataMessage.className = 'alert alert-danger text-center my-5';
            this.elements.noDataMessage.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
            this.elements.noDataMessage.style.display = 'block';
        }
        
        if (this.elements.visualizationsContainer) {
            this.elements.visualizationsContainer.style.display = 'none';
        }
    }
    
    /**
     * Show no data message
     */
    showNoData(message) {
        if (this.elements.noDataMessage) {
            this.elements.noDataMessage.className = 'alert alert-info text-center my-5';
            this.elements.noDataMessage.innerHTML = `<i class="fas fa-info-circle"></i> ${message}`;
            this.elements.noDataMessage.style.display = 'block';
        }
        
        if (this.elements.visualizationsContainer) {
            this.elements.visualizationsContainer.style.display = 'none';
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize visualization manager if on visualizations page
    if (window.location.pathname === '/visualizations' || 
        window.location.pathname.endsWith('/visualizations.html')) {
        window.vizManager = new VisualizationManager();
    }
}); 