// Analysis Page JavaScript

class AnalysisUI {
    constructor() {
        this.initializeComponents();
        this.attachEventListeners();
        this.loadAvailableDatasets();
        this.datasetDateRanges = new Map(); // Store dataset date ranges
        this.dataAvailabilityMap = new Map(); // Store which dates have data
        this.currentDatasetRange = { minDate: null, maxDate: null };
    }

    initializeComponents() {
        // Initialize tooltips
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(el => new bootstrap.Tooltip(el));

        // Data source radio buttons
        this.datasetSourceRadio = document.getElementById('dataset-source');
        this.scraperSourceRadio = document.getElementById('scraper-source');
        
        // Dataset section
        this.datasetSection = document.getElementById('dataset-section');
        this.redditScraperSection = document.getElementById('reddit-scraper-section');
        
        // Dataset elements
        this.datasetListContainer = document.getElementById('dataset-list-container');
        this.selectedDatasetInput = document.getElementById('selected-dataset');
        
        // Reddit scraper elements
        this.redditSort = document.getElementById('reddit-sort');
        this.redditLimit = document.getElementById('reddit-limit');
        this.redditTimeFilter = document.getElementById('reddit-time-filter');
        this.redditIncludeComments = document.getElementById('reddit-include-comments');
        
        // Analysis type cards
        this.analysisTypeCards = document.querySelectorAll('.analysis-type-card');
        
        // Date range elements
        this.dateRangeType = document.getElementById('date-range-type');
        this.dateRangePickerContainer = document.getElementById('date-range-picker-container');
        this.dateRangePicker = document.getElementById('date-range-picker');
        this.datasetDateRangeSpan = document.getElementById('dataset-date-range');
        this.dateRangeWarning = document.getElementById('date-range-warning');
        
        // Form and progress elements
        this.analysisForm = document.getElementById('analysis-form');
        this.progressSection = document.getElementById('progress-section');
    }

    attachEventListeners() {
        // Data source selection
        if (this.datasetSourceRadio) {
            this.datasetSourceRadio.addEventListener('change', () => this.toggleDataSource('dataset'));
        }
        
        if (this.scraperSourceRadio) {
            this.scraperSourceRadio.addEventListener('change', () => this.toggleDataSource('scraper'));
        }

        // Analysis type card selection
        this.analysisTypeCards.forEach(card => {
            card.addEventListener('click', () => this.handleAnalysisTypeSelection(card));
        });

        // Date range change
        if (this.dateRangeType) {
            this.dateRangeType.addEventListener('change', () => this.handleDateRangeTypeChange());
        }

        // Form submission
        if (this.analysisForm) {
            this.analysisForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
    }

    async loadAvailableDatasets() {
        try {
            const response = await fetch('/api/datasets');
            const data = await response.json();
            
            if (data.datasets) {
                this.renderDatasetList(data.datasets);
                this.extractDatasetDateRanges(data.datasets);
            }
        } catch (error) {
            console.error('Error loading datasets:', error);
            this.showErrorMessage({ message: 'Failed to load available datasets' });
        }
    }

    /**
     * Extract date ranges for each dataset and store in a map
     */
    extractDatasetDateRanges(datasets) {
        console.log('Starting date range extraction for datasets:', datasets);
        
        // Process each dataset to extract date ranges
        datasets.forEach(dataset => {
            try {
                console.log('Processing dataset for date range extraction:', dataset);
                
                // First try to use date_range from metadata if available
                if (dataset.date_range && dataset.date_range !== 'All time') {
                    console.log(`Dataset ${dataset.id} has date_range metadata: "${dataset.date_range}"`);
                    let dateRange = this.parseDateRange(dataset.date_range, dataset.path);
                    if (dateRange) {
                        console.log(`Successfully parsed date range metadata for ${dataset.id}`);
                        this.datasetDateRanges.set(dataset.id, dateRange);
                        this.generateDataAvailabilityMap(dataset.id, dateRange);
                        return;
                    }
                    console.log(`Failed to parse date range metadata for ${dataset.id}`);
                }
                
                // Debug logging
                console.log(`Attempting to extract date range from filename for ${dataset.id}: ${dataset.path}`);
                
                // If no date range in metadata, extract from filename
                let dateRange = this.extractDateRangeFromFileName(dataset.path);
                if (dateRange) {
                    console.log(`Successfully extracted date range from filename for ${dataset.id}`);
                    this.datasetDateRanges.set(dataset.id, dateRange);
                    this.generateDataAvailabilityMap(dataset.id, dateRange);
                } else {
                    // If still no date range, create a default one (last 30 days)
                    console.log(`No date range found, using default 30-day range for ${dataset.id}`);
                    const today = new Date();
                    const thirtyDaysAgo = new Date();
                    thirtyDaysAgo.setDate(today.getDate() - 30);
                    
                    const defaultRange = {
                        minDate: thirtyDaysAgo,
                        maxDate: today,
                        isDefault: true
                    };
                    
                    this.datasetDateRanges.set(dataset.id, defaultRange);
                    this.generateDataAvailabilityMap(dataset.id, defaultRange);
                    
                    console.log(`Applied default date range for ${dataset.id}:`, defaultRange);
                }
            } catch (error) {
                console.error(`Error processing dataset for date range extraction:`, dataset, error);
                
                // Create a fallback default range
                const today = new Date();
                const thirtyDaysAgo = new Date();
                thirtyDaysAgo.setDate(today.getDate() - 30);
                
                const fallbackRange = {
                    minDate: thirtyDaysAgo,
                    maxDate: today,
                    isDefault: true,
                    isFallback: true
                };
                
                if (dataset.id) {
                    this.datasetDateRanges.set(dataset.id, fallbackRange);
                    this.generateDataAvailabilityMap(dataset.id, fallbackRange);
                    console.log(`Applied fallback date range for ${dataset.id} due to error:`, fallbackRange);
                }
            }
        });
        
        console.log('Completed date range extraction for all datasets:', this.datasetDateRanges);
    }

    /**
     * Extract date range from filename with improved pattern recognition
     */
    extractDateRangeFromFileName(filePath) {
        if (!filePath) return null;
        
        const fileName = filePath.split('/').pop();
        console.log('Extracting date from filename:', fileName);
        
        // Try different date formats in filenames
        
        // Format 1: Date in format YYYYMMDD like in drivingsg_data_20250318_155441.json
        const dateFormat1Regex = /(\d{8})_\d+/;
        const match1 = fileName.match(dateFormat1Regex);
        if (match1 && match1.length >= 2) {
            try {
                const dateStr = match1[1];
                const year = dateStr.substring(0, 4);
                const month = dateStr.substring(4, 6);
                const day = dateStr.substring(6, 8);
                
                // For this format, use the date as the end date and create a range
                const maxDate = new Date(`${year}-${month}-${day}`);
                if (!isNaN(maxDate.getTime())) {
                    // Create a date range (30 days before until this date)
                    const minDate = new Date(maxDate);
                    minDate.setDate(minDate.getDate() - 30);
                    
                    console.log(`Format 1 match: ${minDate.toISOString()} to ${maxDate.toISOString()}`);
                    return { minDate, maxDate };
                }
            } catch (e) {
                console.error('Error parsing date format 1:', e);
            }
        }
        
        // Format 2: Unix timestamp like in twitter_scraped_singapore_1742189872.csv or reddit_scraped_Singapore_1742185368.csv
        const timestampRegex = /_(\d{10})\.(?:csv|json)$/;
        const match2 = fileName.match(timestampRegex);
        if (match2 && match2.length >= 2) {
            try {
                const timestamp = parseInt(match2[1]);
                const maxDate = new Date(timestamp * 1000); // Convert seconds to milliseconds
                
                if (!isNaN(maxDate.getTime())) {
                    // Create a date range (30 days before until this date)
                    const minDate = new Date(maxDate);
                    minDate.setDate(minDate.getDate() - 30);
                    
                    console.log(`Format 2 match: ${minDate.toISOString()} to ${maxDate.toISOString()}`);
                    return { minDate, maxDate };
                }
            } catch (e) {
                console.error('Error parsing timestamp format:', e);
            }
        }
        
        // Format 3: Date range as YYYYMMDD-YYYYMMDD
        const dateRangeRegex = /(\d{8})-(\d{8})/;
        const match3 = fileName.match(dateRangeRegex);
        if (match3 && match3.length >= 3) {
            try {
                const startDateStr = match3[1];
                const endDateStr = match3[2];
                
                const startYear = startDateStr.substring(0, 4);
                const startMonth = startDateStr.substring(4, 6);
                const startDay = startDateStr.substring(6, 8);
                
                const endYear = endDateStr.substring(0, 4);
                const endMonth = endDateStr.substring(4, 6);
                const endDay = endDateStr.substring(6, 8);
                
                const minDate = new Date(`${startYear}-${startMonth}-${startDay}`);
                const maxDate = new Date(`${endYear}-${endMonth}-${endDay}`);
                
                if (!isNaN(minDate.getTime()) && !isNaN(maxDate.getTime())) {
                    console.log(`Format 3 match: ${minDate.toISOString()} to ${maxDate.toISOString()}`);
                    return { minDate, maxDate };
                }
            } catch (e) {
                console.error('Error parsing date range format:', e);
            }
        }

        // Format 4: Try to match any 8 consecutive digits as a date (YYYYMMDD)
        const anyDateRegex = /(\d{8})/;
        const match4 = fileName.match(anyDateRegex);
        if (match4 && match4.length >= 2) {
            try {
                const dateStr = match4[1];
                const year = dateStr.substring(0, 4);
                const month = dateStr.substring(4, 6);
                const day = dateStr.substring(6, 8);
                
                const maxDate = new Date(`${year}-${month}-${day}`);
                if (!isNaN(maxDate.getTime())) {
                    // Create a min date 30 days before
                    const minDate = new Date(maxDate);
                    minDate.setDate(minDate.getDate() - 30);
                    
                    console.log(`Format 4 match: ${minDate.toISOString()} to ${maxDate.toISOString()}`);
                    return { minDate, maxDate };
                }
            } catch (e) {
                console.error('Error parsing general date format:', e);
            }
        }
        
        // Format 5: Try to detect a Unix timestamp in the filename (any 10-digit number)
        const anyTimestampRegex = /(\d{10})/;
        const match5 = fileName.match(anyTimestampRegex);
        if (match5 && match5.length >= 2) {
            try {
                const timestamp = parseInt(match5[1]);
                // Check if timestamp is in a reasonable range (between 2010 and 2050)
                const year = new Date(timestamp * 1000).getFullYear();
                if (year >= 2010 && year <= 2050) {
                    const maxDate = new Date(timestamp * 1000);
                    
                    if (!isNaN(maxDate.getTime())) {
                        // Create a date range (30 days before until this date)
                        const minDate = new Date(maxDate);
                        minDate.setDate(minDate.getDate() - 30);
                        
                        console.log(`Format 5 match: ${minDate.toISOString()} to ${maxDate.toISOString()}`);
                        return { minDate, maxDate };
                    }
                }
            } catch (e) {
                console.error('Error parsing any timestamp format:', e);
            }
        }
        
        // If we get here, we couldn't extract a date from the filename
        console.log('No date formats matched for:', fileName);
        return null;
    }

    /**
     * Generate data availability map for a dataset
     */
    generateDataAvailabilityMap(datasetId, dateRange) {
        if (!dateRange) return;
        
        // Create a set to store available dates
        const availableDates = new Set();
        
        // Fill in all dates in the range
        const currentDate = new Date(dateRange.minDate);
        while (currentDate <= dateRange.maxDate) {
            const dateStr = currentDate.toISOString().split('T')[0];
            availableDates.add(dateStr);
            currentDate.setDate(currentDate.getDate() + 1);
        }
        
        // Store the availability map
        this.dataAvailabilityMap.set(datasetId, availableDates);
        console.log(`Generated availability map for ${datasetId} with ${availableDates.size} dates`);
    }

    renderDatasetList(datasets) {
        if (!this.datasetListContainer) return;

        // Group datasets by source
        const groupedDatasets = {
            reddit: datasets.filter(d => d.source === 'reddit'),
            twitter: datasets.filter(d => d.source === 'twitter')
        };

        // Create dataset list HTML
        let html = '';

        // Reddit datasets
        if (groupedDatasets.reddit.length > 0) {
            html += `
                <div class="dataset-group">
                    <h5><i class="fa-reddit fab"></i> Reddit Datasets</h5>
                    <div class="dataset-items">
                        ${this.createDatasetItems(groupedDatasets.reddit)}
                    </div>
                </div>
            `;
        }

        // Twitter datasets
        if (groupedDatasets.twitter.length > 0) {
            html += `
                <div class="dataset-group">
                    <h5><i class="fa-twitter fab"></i> Twitter Datasets</h5>
                    <div class="dataset-items">
                        ${this.createDatasetItems(groupedDatasets.twitter)}
                    </div>
                </div>
            `;
        }

        this.datasetListContainer.innerHTML = html || '<p class="text-muted">No datasets available</p>';

        // Add click handlers to dataset items
        const datasetItems = this.datasetListContainer.querySelectorAll('.dataset-item');
        datasetItems.forEach(item => {
            item.addEventListener('click', () => this.selectDataset(item));
        });
    }

    createDatasetItems(datasets) {
        return datasets.map(dataset => `
            <div class="dataset-item" data-dataset-id="${dataset.id}" data-dataset-path="${dataset.path}" data-file-type="${dataset.type}">
                <div class="dataset-item-content">
                    <h6>
                        ${dataset.name.split(' (')[0]}
                        <span class="file-type">${dataset.type.toUpperCase()}</span>
                    </h6>
                    <div class="metadata">
                        <small class="text-muted">
                            <i class="fa-calendar-alt far"></i> ${dataset.date_range || 'All time'}
                        </small>
                        <small class="text-muted">
                            <i class="fa-file-alt far"></i> ${dataset.size}
                        </small>
                        <small class="text-muted">
                            <i class="fa-list-alt far"></i> ${dataset.item_count} items
                        </small>
                    </div>
                </div>
                <div class="dataset-item-select">
                    <i class="fa-check-circle fas"></i>
                </div>
            </div>
        `).join('');
    }

    selectDataset(item) {
        // Make sure dataset source is selected
        if (this.datasetSourceRadio) {
            this.datasetSourceRadio.checked = true;
            this.toggleDataSource('dataset');
        }
        
        // Remove selection from all items
        this.datasetListContainer.querySelectorAll('.dataset-item').forEach(i => {
            i.classList.remove('selected');
        });

        // Select clicked item
        item.classList.add('selected');

        // Update hidden input
        if (this.selectedDatasetInput) {
            this.selectedDatasetInput.value = item.dataset.datasetId;
        }

        // Update date range options based on dataset
        this.updateDateRangeOptions(item.dataset.datasetId);
    }

    updateDateRangeOptions(datasetId) {
        console.log(`Updating date range options for dataset: ${datasetId}`);
        
        // Reset date range type to "All"
        if (this.dateRangeType) {
            this.dateRangeType.value = "all";
        }
        
        // Hide the date range picker initially
        if (this.dateRangePickerContainer) {
            this.dateRangePickerContainer.style.display = 'none';
        }
        
        // Get the date range for this dataset
        const dateRange = this.datasetDateRanges.get(datasetId);
        this.currentDatasetRange = dateRange || { minDate: null, maxDate: null };
        
        console.log(`Current dataset range for ${datasetId}:`, this.currentDatasetRange);
        
        // Update the dataset date range display
        if (this.datasetDateRangeSpan && dateRange) {
            try {
                const formattedMinDate = dateRange.minDate.toLocaleDateString();
                const formattedMaxDate = dateRange.maxDate.toLocaleDateString();
                
                let rangeText = `${formattedMinDate} to ${formattedMaxDate}`;
                
                // Add indicators for default or estimated ranges
                if (dateRange.isDefault && dateRange.isFallback) {
                    rangeText += ' (estimated - fallback)';
                } else if (dateRange.isDefault) {
                    rangeText += ' (estimated)';
                }
                
                this.datasetDateRangeSpan.textContent = rangeText;
                console.log(`Updated date range display to: ${rangeText}`);
            } catch (e) {
                console.error('Error formatting date range for display:', e);
                this.datasetDateRangeSpan.textContent = 'Error displaying date range';
            }
        } else if (this.datasetDateRangeSpan) {
            this.datasetDateRangeSpan.textContent = 'Not available';
            console.log('No date range available for display');
        }
        
        // Initialize or update the date range picker
        this.initDateRangePicker(datasetId);
        
        // Update available options in date range selector
        this.updateDateRangeSelectOptions(dateRange);
    }
    
    /**
     * Update date range select options based on available data range
     */
    updateDateRangeSelectOptions(dateRange) {
        if (!this.dateRangeType || !dateRange) return;
        
        const options = this.dateRangeType.options;
        const now = new Date();
        const diffDays = Math.ceil((now - dateRange.minDate) / (1000 * 60 * 60 * 24));
        
        // Enable/disable options based on date range
        for (let i = 0; i < options.length; i++) {
            const option = options[i];
            
            if (option.value === 'last7' && diffDays < 7) {
                option.disabled = true;
            } else if (option.value === 'last30' && diffDays < 30) {
                option.disabled = true;
            } else if (option.value === 'last90' && diffDays < 90) {
                option.disabled = true;
            } else {
                option.disabled = false;
            }
        }
    }

    /**
     * Initialize date range picker with constraints from dataset
     */
    initDateRangePicker(datasetId) {
        if (!this.dateRangePicker) return;
        
        // Get the date range and available dates for this dataset
        const dateRange = this.datasetDateRanges.get(datasetId);
        const availableDates = this.dataAvailabilityMap.get(datasetId);
        
        console.log('Initializing date picker for dataset:', datasetId);
        console.log('Date range:', dateRange);
        
        if (!dateRange) {
            console.log('No date range available for this dataset');
            return;
        }
        
        try {
            // Destroy existing date picker if it exists
            if (this.dateRangePickerInstance) {
                this.dateRangePickerInstance.remove();
            }
            
            // Initialize the date range picker
            $(this.dateRangePicker).daterangepicker({
                startDate: dateRange.minDate,
                endDate: dateRange.maxDate,
                minDate: dateRange.minDate,
                maxDate: dateRange.maxDate,
                opens: 'center',
                autoApply: true,
                locale: {
                    format: 'YYYY-MM-DD'
                },
                isInvalidDate: (date) => {
                    // If we have availability data, use it to highlight/disable dates
                    if (availableDates) {
                        // Convert date to ISO string format (YYYY-MM-DD)
                        const dateStr = date.format('YYYY-MM-DD');
                        
                        // Return true if date is invalid (doesn't have data)
                        return !availableDates.has(dateStr);
                    }
                    return false;
                }
            });
            
            // Add event listener for date range changes
            $(this.dateRangePicker).on('apply.daterangepicker', (event, picker) => {
                this.checkSelectedDatesAvailability(datasetId);
            });
            
            console.log('Date picker initialized successfully');
        } catch (error) {
            console.error('Error initializing date picker:', error);
        }
    }
    
    /**
     * Check if all dates in the selected range have data
     */
    checkSelectedDatesAvailability(datasetId) {
        if (!this.dateRangePicker || !this.dateRangeWarning) return;
        
        const availableDates = this.dataAvailabilityMap.get(datasetId);
        if (!availableDates) return;
        
        // Get selected date range
        const rangeParts = this.dateRangePicker.value.split(' - ');
        if (rangeParts.length !== 2) return;
        
        try {
            const startDate = new Date(rangeParts[0]);
            const endDate = new Date(rangeParts[1]);
            
            // Check if all dates in range have data
            let allDatesHaveData = true;
            let currentDate = new Date(startDate);
            
            while (currentDate <= endDate) {
                const dateStr = currentDate.toISOString().split('T')[0];
                if (!availableDates.has(dateStr)) {
                    allDatesHaveData = false;
                    break;
                }
                currentDate.setDate(currentDate.getDate() + 1);
            }
            
            // Show/hide warning
            this.dateRangeWarning.style.display = allDatesHaveData ? 'none' : 'block';
        } catch (e) {
            console.error('Error checking date availability:', e);
        }
    }

    handleDateRangeTypeChange() {
        const selectedType = this.dateRangeType.value;
        
        // Show/hide date range picker for custom option
        if (this.dateRangePickerContainer) {
            this.dateRangePickerContainer.style.display = 
                selectedType === 'custom' ? 'block' : 'none';
        }
        
        // For non-custom options, set appropriate date range
        if (selectedType !== 'custom' && this.currentDatasetRange.minDate && this.currentDatasetRange.maxDate) {
            let startDate, endDate;
            
            switch (selectedType) {
                case 'all':
                    startDate = this.currentDatasetRange.minDate;
                    endDate = this.currentDatasetRange.maxDate;
                    break;
                case 'last7':
                    endDate = new Date(this.currentDatasetRange.maxDate);
                    startDate = new Date(endDate);
                    startDate.setDate(startDate.getDate() - 6); // 7 days including today
                    break;
                case 'last30':
                    endDate = new Date(this.currentDatasetRange.maxDate);
                    startDate = new Date(endDate);
                    startDate.setDate(startDate.getDate() - 29); // 30 days including today
                    break;
                case 'last90':
                    endDate = new Date(this.currentDatasetRange.maxDate);
                    startDate = new Date(endDate);
                    startDate.setDate(startDate.getDate() - 89); // 90 days including today
                    break;
            }
            
            // Make sure start date is not before min date
            if (startDate < this.currentDatasetRange.minDate) {
                startDate = new Date(this.currentDatasetRange.minDate);
            }
        }
    }

    handleAnalysisTypeSelection(card) {
        const checkbox = card.querySelector('input[type="checkbox"]');
        checkbox.checked = !checkbox.checked;
        card.classList.toggle('selected', checkbox.checked);
    }

    /**
     * Toggle between dataset selection and Reddit scraper
     */
    toggleDataSource(source) {
        if (source === 'dataset') {
            this.datasetSection.style.display = 'block';
            this.redditScraperSection.style.display = 'none';
        } else if (source === 'scraper') {
            this.datasetSection.style.display = 'none';
            this.redditScraperSection.style.display = 'block';
            
            // Clear any selected dataset
            this.datasetListContainer.querySelectorAll('.dataset-item').forEach(item => {
                item.classList.remove('selected');
            });
            if (this.selectedDatasetInput) {
                this.selectedDatasetInput.value = '';
            }
            
            // Reset date range options
            if (this.datasetDateRangeSpan) {
                this.datasetDateRangeSpan.textContent = 'Not available for Reddit scraper';
            }
            if (this.dateRangeType) {
                this.dateRangeType.value = 'all';
            }
            if (this.dateRangePickerContainer) {
                this.dateRangePickerContainer.style.display = 'none';
            }
        }
    }

    async handleFormSubmit(e) {
        e.preventDefault();

        if (!this.validateForm()) {
            return;
        }

        // Show loading state
        this.showLoadingState();

        try {
            const formData = this.collectFormData();
            const response = await this.submitAnalysis(formData);
            
            if (response.success) {
                this.showSuccessMessage(response);
                this.showProgressSection();
                this.startProgressTracking();
            } else {
                throw new Error(response.message || 'Analysis failed');
            }
        } catch (error) {
            this.showErrorMessage(error);
        }
    }

    validateForm() {
        // Check if a dataset is selected or Reddit scraper is enabled
        const isDatasetSourceSelected = this.datasetSourceRadio && this.datasetSourceRadio.checked;
        const isScraperSourceSelected = this.scraperSourceRadio && this.scraperSourceRadio.checked;
        
        if (isDatasetSourceSelected) {
            const selectedDataset = document.querySelector('.dataset-item.selected');
            if (!selectedDataset) {
                this.showErrorMessage({ message: 'Please select a dataset' });
                return false;
            }
        } else if (!isScraperSourceSelected) {
            this.showErrorMessage({ message: 'Please select a data source' });
            return false;
        }

        // Check if at least one analysis type is selected
        const selectedAnalysisTypes = document.querySelectorAll('input[name="analysis_types[]"]:checked');
        if (selectedAnalysisTypes.length === 0) {
            this.showErrorMessage({ message: 'Please select at least one analysis type' });
            return false;
        }

        // Validate custom date range if selected
        if (this.dateRangeType && this.dateRangeType.value === 'custom') {
            if (!this.dateRangePicker || !this.dateRangePicker.value) {
                this.showErrorMessage({ message: 'Please select a date range' });
                return false;
            }
        }

        return true;
    }

    collectFormData() {
        const formData = new FormData(this.analysisForm);
        
        // Add data source type
        const isScraperSelected = this.scraperSourceRadio && this.scraperSourceRadio.checked;
        formData.append('data_source_type', isScraperSelected ? 'reddit_scraper' : 'existing_dataset');
        
        // Add Reddit scraper options if selected
        if (isScraperSelected) {
            formData.append('reddit_subreddit', 'drivingSG');
            
            // Get values from form fields
            const redditSort = this.redditSort ? this.redditSort.value : 'hot';
            const redditLimit = this.redditLimit ? this.redditLimit.value : '25';
            const redditTimeFilter = this.redditTimeFilter ? this.redditTimeFilter.value : 'day';
            const redditIncludeComments = this.redditIncludeComments ? this.redditIncludeComments.value : 'none';
            
            formData.append('reddit_sort', redditSort);
            formData.append('reddit_limit', redditLimit);
            formData.append('reddit_time_filter', redditTimeFilter);
            formData.append('reddit_include_comments', redditIncludeComments);
        }

        // Add date range info
        if (this.dateRangeType) {
            const dateRangeType = this.dateRangeType.value;
            formData.append('date_range_type', dateRangeType);
            
            if (dateRangeType === 'custom' && this.dateRangePicker) {
                const rangeParts = this.dateRangePicker.value.split(' - ');
                if (rangeParts.length === 2) {
                    formData.append('start_date', rangeParts[0]);
                    formData.append('end_date', rangeParts[1]);
                }
            }
        }
        
        // Get selected analysis types
        const analysisTypes = [];
        document.querySelectorAll('input[name="analysis_types[]"]:checked').forEach(checkbox => {
            analysisTypes.push(checkbox.value);
        });
        
        formData.append('analysis_types', JSON.stringify(analysisTypes));
        
        return formData;
    }

    async submitAnalysis(formData) {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }

        return await response.json();
    }

    showLoadingState() {
        const submitButton = this.analysisForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fa-spin fa-spinner fas"></i> Running Analysis...';
    }

    showSuccessMessage(response) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show';
        alert.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fa-check-circle fas me-2"></i>
                <div>
                    <h5 class="mb-1">Analysis Started Successfully</h5>
                    <p class="mb-0">Your analysis is now running. You can track the progress below.</p>
                </div>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        this.analysisForm.insertAdjacentElement('afterend', alert);
    }

    showErrorMessage(error) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show';
        alert.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fa-exclamation-circle fas me-2"></i>
                <div>
                    <h5 class="mb-1">Analysis Failed</h5>
                    <p class="mb-0">${error.message}</p>
                </div>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        this.analysisForm.insertAdjacentElement('afterend', alert);
        
        // Reset submit button
        const submitButton = this.analysisForm.querySelector('button[type="submit"]');
        submitButton.disabled = false;
        submitButton.innerHTML = '<i class="fa-play-circle fas"></i> Run Analysis';
    }

    showProgressSection() {
        this.progressSection.style.display = 'block';
        this.progressSection.scrollIntoView({ behavior: 'smooth' });
    }

    startProgressTracking() {
        let startTime = Date.now();
        let processedItems = 0;
        let processingRate = 0;
        let lastUpdateTime = Date.now();
        let lastProcessedItems = 0;
        
        // Initialize progress steps
        this.updateProgressStep('step-data-loading', 'active', 'In Progress');
        
        // Update progress every second
        const progressInterval = setInterval(() => {
            // Calculate elapsed time
            const currentTime = Date.now();
            const elapsed = Math.floor((currentTime - startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            document.getElementById('processing-time').textContent = 
                `${minutes}:${seconds.toString().padStart(2, '0')}`;
            
            // Calculate processing rate (items per second)
            const timeSinceLastUpdate = (currentTime - lastUpdateTime) / 1000;
            if (timeSinceLastUpdate >= 1) {
                const itemsSinceLastUpdate = processedItems - lastProcessedItems;
                processingRate = Math.round(itemsSinceLastUpdate / timeSinceLastUpdate);
                document.getElementById('processing-rate').textContent = `${processingRate}/sec`;
                
                lastUpdateTime = currentTime;
                lastProcessedItems = processedItems;
            }
            
            // Simulate progress updates for demonstration
            const progressIncrement = Math.floor(Math.random() * 5) + 1;
            processedItems += progressIncrement;
            
            // Cap at 100 for demonstration purposes
            if (processedItems > 100) processedItems = 100;
            const progressPercentage = Math.min(Math.round((processedItems / 100) * 100), 100);
            
            // Update processed items display
            document.getElementById('processed-items').textContent = processedItems;
            
            // Update progress bar
            const progressBar = this.progressSection.querySelector('.progress-bar');
            progressBar.style.width = `${progressPercentage}%`;
            document.getElementById('progress-percentage').textContent = `${progressPercentage}%`;
            
            // Update analysis type indicator (just for demo)
            if (progressPercentage < 30) {
                document.getElementById('analysis-type-indicator').textContent = 'Loading dataset...';
                this.updateProgressStep('step-data-loading', 'active', 'In Progress');
            } else if (progressPercentage < 60) {
                document.getElementById('analysis-type-indicator').textContent = 'Processing sentiment analysis...';
                this.updateProgressStep('step-data-loading', 'completed', 'Complete');
                this.updateProgressStep('step-processing', 'active', 'In Progress');
            } else if (progressPercentage < 90) {
                document.getElementById('analysis-type-indicator').textContent = 'Generating visualizations...';
                this.updateProgressStep('step-processing', 'completed', 'Complete');
                this.updateProgressStep('step-generating-results', 'active', 'In Progress');
            } else {
                document.getElementById('analysis-type-indicator').textContent = 'Saving results...';
                this.updateProgressStep('step-generating-results', 'completed', 'Complete');
                this.updateProgressStep('step-saving', 'active', 'In Progress');
            }
            
            // Estimate completion time
            if (processingRate > 0 && progressPercentage < 100) {
                const remainingItems = 100 - processedItems;
                const estimatedSecondsRemaining = Math.ceil(remainingItems / processingRate);
                const estMinutes = Math.floor(estimatedSecondsRemaining / 60);
                const estSeconds = estimatedSecondsRemaining % 60;
                document.getElementById('completion-estimate').textContent = 
                    `${estMinutes}:${estSeconds.toString().padStart(2, '0')}`;
            }
            
            // Add log entry with random type
            this.addLogEntry(this.getRandomLogMessage(progressPercentage), this.getRandomLogType());
            
            // Stop when complete
            if (progressPercentage === 100) {
                setTimeout(() => {
                    clearInterval(progressInterval);
                    this.analysisComplete();
                }, 1000);
            }
        }, 1000);
        
        // Set up event handlers for new UI elements
        document.getElementById('cancel-analysis-btn').addEventListener('click', () => {
            clearInterval(progressInterval);
            this.cancelAnalysis();
        });
        
        document.getElementById('clear-log-btn').addEventListener('click', () => {
            document.getElementById('analysis-log').innerHTML = '';
            this.addLogEntry('Log cleared by user', 'info');
        });
    }
    
    updateProgressStep(stepId, state, statusText) {
        const step = document.getElementById(stepId);
        if (!step) return;
        
        // Remove all state classes
        step.classList.remove('active', 'completed', 'error');
        
        // Add the new state class
        step.classList.add(state);
        
        // Update the status text
        const statusElement = step.querySelector('.step-status');
        if (statusElement) {
            statusElement.textContent = statusText;
        }
    }

    addLogEntry(message, level = 'info') {
        const log = document.getElementById('analysis-log');
        const entry = document.createElement('div');
        entry.className = `log-entry log-${level}`;
        
        const timestamp = new Date().toLocaleTimeString();
        entry.innerHTML = `<span class="log-time">[${timestamp}]</span> ${message}`;
        
        log.appendChild(entry);
        log.scrollTop = log.scrollHeight;
    }
    
    getRandomLogMessage(progress) {
        const messages = [
            { message: 'Reading dataset contents...', range: [0, 20] },
            { message: 'Parsing JSON data structure...', range: [10, 30] },
            { message: 'Initializing sentiment analyzer...', range: [20, 40] },
            { message: 'Analyzing post sentiment...', range: [30, 50] },
            { message: 'Processing comment sentiment...', range: [40, 60] },
            { message: 'Detecting trending topics...', range: [50, 70] },
            { message: 'Analyzing temporal patterns...', range: [60, 80] },
            { message: 'Identifying traffic incidents...', range: [70, 85] },
            { message: 'Mapping location references...', range: [80, 90] },
            { message: 'Generating topic models...', range: [85, 95] },
            { message: 'Finalizing analysis results...', range: [90, 100] },
            { message: 'Saving analysis to disk...', range: [95, 100] }
        ];
        
        // Filter messages appropriate for the current progress
        const appropriateMessages = messages.filter(m => 
            progress >= m.range[0] && progress <= m.range[1]
        );
        
        if (appropriateMessages.length > 0) {
            const randomIndex = Math.floor(Math.random() * appropriateMessages.length);
            return appropriateMessages[randomIndex].message;
        }
        
        return 'Processing data...';
    }
    
    getRandomLogType() {
        const types = ['info', 'info', 'info', 'success', 'warning'];
        const randomIndex = Math.floor(Math.random() * types.length);
        return types[randomIndex];
    }

    analysisComplete() {
        // Update status badge
        const statusBadge = document.getElementById('analysis-status-badge');
        statusBadge.classList.remove('bg-info');
        statusBadge.classList.add('bg-success');
        statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Analysis Complete';
        
        // Update progress steps
        this.updateProgressStep('step-saving', 'completed', 'Complete');
        
        // Add completion log entries
        this.addLogEntry('Analysis completed successfully', 'success');
        this.addLogEntry('Results saved to data/analysis directory', 'success');
        
        // Show completion message
        const resultsSection = document.getElementById('analysis-results');
        resultsSection.style.display = 'block';
        setTimeout(() => {
            resultsSection.classList.add('show');
        }, 100);
        
        // Set up download link
        document.getElementById('download-results').addEventListener('click', (e) => {
            e.preventDefault();
            // In a real application, this would be set to the actual file path
            alert('In a real implementation, this would download the analysis file');
        });
        
        // Reset form
        const submitButton = this.analysisForm.querySelector('button[type="submit"]');
        submitButton.disabled = false;
        submitButton.innerHTML = '<i class="fas fa-play-circle"></i> Run Analysis';
    }
    
    cancelAnalysis() {
        // Update status badge
        const statusBadge = document.getElementById('analysis-status-badge');
        statusBadge.classList.remove('bg-info');
        statusBadge.classList.add('bg-warning');
        statusBadge.innerHTML = '<i class="fas fa-times-circle"></i> Analysis Cancelled';
        
        // Add cancellation log entry
        this.addLogEntry('Analysis cancelled by user', 'warning');
        
        // Update current step to error
        const currentStep = document.querySelector('.step.active');
        if (currentStep) {
            this.updateProgressStep(currentStep.id, 'error', 'Cancelled');
        }
        
        // Reset form after a delay
        setTimeout(() => {
            this.progressSection.style.display = 'none';
            
            const submitButton = this.analysisForm.querySelector('button[type="submit"]');
            submitButton.disabled = false;
            submitButton.innerHTML = '<i class="fas fa-play-circle"></i> Run Analysis';
        }, 3000);
    }

    parseDateRange(dateRangeString, filePath) {
        console.log(`Parsing date range: "${dateRangeString}" from ${filePath}`);
        
        if (!dateRangeString) return null;
        
        // Handle common formats
        try {
            // Format: "YYYY-MM-DD to YYYY-MM-DD"
            if (dateRangeString.includes(' to ')) {
                const parts = dateRangeString.split(' to ');
                if (parts.length === 2) {
                    const minDate = new Date(parts[0]);
                    const maxDate = new Date(parts[1]);
                    
                    if (!isNaN(minDate.getTime()) && !isNaN(maxDate.getTime())) {
                        console.log(`Parsed date range successfully: ${minDate.toISOString()} to ${maxDate.toISOString()}`);
                        return { minDate, maxDate };
                    }
                }
            }
            
            // Format: "Month YYYY - Month YYYY" (e.g., "January 2023 - March 2023")
            const monthRangeRegex = /([A-Za-z]+)\s+(\d{4})\s*-\s*([A-Za-z]+)\s+(\d{4})/;
            const monthRangeMatch = dateRangeString.match(monthRangeRegex);
            if (monthRangeMatch) {
                const startMonth = this.getMonthNumber(monthRangeMatch[1]);
                const startYear = parseInt(monthRangeMatch[2]);
                const endMonth = this.getMonthNumber(monthRangeMatch[3]);
                const endYear = parseInt(monthRangeMatch[4]);
                
                if (startMonth !== -1 && endMonth !== -1) {
                    const minDate = new Date(startYear, startMonth, 1);
                    const maxDate = new Date(endYear, endMonth + 1, 0); // Last day of the month
                    
                    if (!isNaN(minDate.getTime()) && !isNaN(maxDate.getTime())) {
                        console.log(`Parsed month range successfully: ${minDate.toISOString()} to ${maxDate.toISOString()}`);
                        return { minDate, maxDate };
                    }
                }
            }
            
            // Single date strings (treat as the end date and create a range of 30 days before)
            if (/^\d{4}-\d{2}-\d{2}$/.test(dateRangeString)) { // YYYY-MM-DD
                const maxDate = new Date(dateRangeString);
                if (!isNaN(maxDate.getTime())) {
                    const minDate = new Date(maxDate);
                    minDate.setDate(minDate.getDate() - 30);
                    
                    console.log(`Parsed single date successfully: ${minDate.toISOString()} to ${maxDate.toISOString()}`);
                    return { minDate, maxDate };
                }
            }
            
            // Last N days/months formats
            const lastNRegex = /Last\s+(\d+)\s+(days|months)/i;
            const lastNMatch = dateRangeString.match(lastNRegex);
            if (lastNMatch) {
                const n = parseInt(lastNMatch[1]);
                const unit = lastNMatch[2].toLowerCase();
                
                const maxDate = new Date(); // Today
                const minDate = new Date();
                
                if (unit === 'days') {
                    minDate.setDate(minDate.getDate() - n);
                } else if (unit === 'months') {
                    minDate.setMonth(minDate.getMonth() - n);
                }
                
                console.log(`Parsed "Last N" format successfully: ${minDate.toISOString()} to ${maxDate.toISOString()}`);
                return { minDate, maxDate };
            }
            
            // Try to extract from file path as a last resort
            if (filePath) {
                const dateRange = this.extractDateRangeFromFileName(filePath);
                if (dateRange) {
                    console.log(`Used filename date extraction as fallback: ${dateRange.minDate.toISOString()} to ${dateRange.maxDate.toISOString()}`);
                    return dateRange;
                }
            }
        } catch (error) {
            console.error('Error parsing date range:', error);
        }
        
        console.log(`Failed to parse date range: "${dateRangeString}"`);
        return null;
    }
    
    /**
     * Convert month name to month number (0-11)
     */
    getMonthNumber(monthName) {
        const months = [
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december'
        ];
        
        const monthNameLower = monthName.toLowerCase();
        return months.findIndex(m => monthNameLower.includes(m));
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    new AnalysisUI();
});

// Hadoop Job Execution Functionality
function initHadoopJobExecution() {
    // File browsing buttons
    document.getElementById('browse-input-btn').addEventListener('click', function() {
        openFileBrowser('input');
    });
    
    document.getElementById('browse-output-btn').addEventListener('click', function() {
        openFileBrowser('output');
    });
    
    // Analysis type selection
    document.getElementById('hadoop-analysis-type').addEventListener('change', function() {
        validateHadoopForm();
    });
    
    // Submit handler modification to include Hadoop job execution
    document.getElementById('analysis-form').addEventListener('submit', function(event) {
        // If we're in Hadoop job mode, handle it differently
        if (document.getElementById('hadoop-job-section').style.display !== 'none') {
            event.preventDefault();
            if (validateHadoopForm()) {
                executeHadoopJob();
            }
        }
    });
    
    // Show the right section based on a tab or option
    const dataSourceTabs = document.querySelectorAll('input[name="data-source"]');
    dataSourceTabs.forEach(tab => {
        tab.addEventListener('change', function() {
            updateDataSourceSection();
        });
    });
    
    // Add Hadoop job radio button
    addHadoopJobOption();
}

function addHadoopJobOption() {
    // Add a new radio button for Hadoop job execution
    const dataSourceGroup = document.querySelector('.btn-group[role="group"][aria-label="Data source"]');
    
    if (dataSourceGroup) {
        const hadoopRadio = document.createElement('input');
        hadoopRadio.type = 'radio';
        hadoopRadio.className = 'btn-check';
        hadoopRadio.name = 'data-source';
        hadoopRadio.id = 'hadoop-job-source';
        hadoopRadio.autocomplete = 'off';
        
        const hadoopLabel = document.createElement('label');
        hadoopLabel.className = 'btn btn-outline-primary';
        hadoopLabel.htmlFor = 'hadoop-job-source';
        hadoopLabel.innerHTML = '<i class="fas fa-cogs"></i> Run Hadoop Job';
        
        dataSourceGroup.appendChild(hadoopRadio);
        dataSourceGroup.appendChild(hadoopLabel);
    }
}

function updateDataSourceSection() {
    const selectedSource = document.querySelector('input[name="data-source"]:checked').id;
    
    // Hide all sections first
    document.getElementById('dataset-section').style.display = 'none';
    document.getElementById('reddit-scraper-section').style.display = 'none';
    document.getElementById('hadoop-job-section').style.display = 'none';
    
    // Show the selected section
    if (selectedSource === 'dataset-source') {
        document.getElementById('dataset-section').style.display = 'block';
    } else if (selectedSource === 'scraper-source') {
        document.getElementById('reddit-scraper-section').style.display = 'block';
    } else if (selectedSource === 'hadoop-job-source') {
        document.getElementById('hadoop-job-section').style.display = 'block';
    }
}

function openFileBrowser(type) {
    // Create a file input element
    const fileInput = document.createElement('input');
    fileInput.type = type === 'input' ? 'file' : 'text';
    
    if (type === 'input') {
        fileInput.accept = '.json';
        
        fileInput.onchange = function() {
            if (fileInput.files.length > 0) {
                const filePath = fileInput.files[0].path || fileInput.value;
                document.getElementById('hadoop-input-file').value = filePath;
                validateHadoopForm();
            }
        };
        
        // Trigger the file browser
        fileInput.click();
    } else {
        // For output directory, we need to use a directory picker
        // Since browser APIs don't directly support this, we'll use a custom approach
        
        // Create a directory browser dialog using window.showDirectoryPicker()
        // This is a modern API that might not be supported in all browsers
        if (window.showDirectoryPicker) {
            window.showDirectoryPicker().then(directoryHandle => {
                // Convert the directory handle to a path
                return directoryHandle.name;
            }).then(directoryPath => {
                document.getElementById('hadoop-output-dir').value = directoryPath;
                validateHadoopForm();
            }).catch(err => {
                console.error('Error selecting directory:', err);
            });
        } else {
            // Fallback for browsers that don't support showDirectoryPicker
            // We'll use a server-side approach
            fetch('/api/browse_directory', {
                method: 'GET'
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    document.getElementById('hadoop-output-dir').value = data.path;
                    validateHadoopForm();
                } else {
                    showNotification('Error selecting directory', 'error');
                }
            })
            .catch(error => {
                console.error('Error calling directory browser API:', error);
                showNotification('Error selecting directory', 'error');
            });
        }
    }
}

function validateHadoopForm() {
    const inputFile = document.getElementById('hadoop-input-file').value;
    const analysisType = document.getElementById('hadoop-analysis-type').value;
    const outputDir = document.getElementById('hadoop-output-dir').value;
    
    let isValid = true;
    let errorMessage = '';
    
    if (!inputFile) {
        isValid = false;
        errorMessage += 'Please select an input file. ';
    } else if (!inputFile.toLowerCase().endsWith('.json')) {
        isValid = false;
        errorMessage += 'Input file must be a JSON file. ';
    }
    
    if (!analysisType) {
        isValid = false;
        errorMessage += 'Please select an analysis type. ';
    }
    
    if (!outputDir) {
        isValid = false;
        errorMessage += 'Please select an output directory. ';
    }
    
    // Show validation message if needed
    if (!isValid && errorMessage) {
        showNotification(errorMessage.trim(), 'error');
    }
    
    return isValid;
}

function executeHadoopJob() {
    // Show progress section
    document.getElementById('progress-section').style.display = 'block';
    
    // Update progress status
    document.getElementById('analysis-status-badge').className = 'badge bg-info';
    document.getElementById('analysis-status-badge').innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Running Hadoop Job';
    document.getElementById('analysis-type-indicator').textContent = 'Executing ' + document.getElementById('hadoop-analysis-type').value + ' analysis...';
    
    // Set steps status
    setStepStatus('step-data-loading', 'In Progress');
    setStepStatus('step-processing', 'Pending');
    setStepStatus('step-generating-results', 'Pending');
    setStepStatus('step-saving', 'Pending');
    
    // Reset progress bar
    updateProgressBar(5);
    
    // Add initial log entry
    appendToLog('Starting Hadoop job execution...', 'info');
    appendToLog('Input File: ' + document.getElementById('hadoop-input-file').value, 'info');
    appendToLog('Analysis Type: ' + document.getElementById('hadoop-analysis-type').value, 'info');
    appendToLog('Output Directory: ' + document.getElementById('hadoop-output-dir').value, 'info');
    
    // Collect parameters
    const params = {
        input_file: document.getElementById('hadoop-input-file').value,
        analysis_type: document.getElementById('hadoop-analysis-type').value,
        output_dir: document.getElementById('hadoop-output-dir').value,
        timerange_start: document.getElementById('hadoop-timerange-start').value,
        timerange_end: document.getElementById('hadoop-timerange-end').value
    };
    
    // Start the timer for elapsed time
    startProcessingTimer();
    
    // Execute the Hadoop job via API
    executeHadoopJobAPI(params);
}

function executeHadoopJobAPI(params) {
    // This is a placeholder for the actual API call to run the Hadoop job
    // In a real implementation, this would call a server-side endpoint
    
    fetch('/api/run_hadoop_job', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(params)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Handle successful job submission
            const jobId = data.job_id;
            appendToLog('Hadoop job submitted successfully. Job ID: ' + jobId, 'success');
            
            // Start polling for job status
            pollJobStatus(jobId);
        } else {
            // Handle job submission failure
            appendToLog('Failed to submit Hadoop job: ' + data.message, 'error');
            setJobFailed(data.message);
        }
    })
    .catch(error => {
        console.error('Error submitting Hadoop job:', error);
        appendToLog('Error submitting Hadoop job: ' + error.message, 'error');
        setJobFailed('Network or server error');
    });
    
    // For demo/testing purposes, simulate a successful job
    simulateHadoopJob(params);
}

function simulateHadoopJob(params) {
    // This is a simulation for testing the UI
    // In a real implementation, this would be replaced by actual API calls
    
    const steps = [
        { name: 'Loading input data', progress: 10, step: 'step-data-loading' },
        { name: 'Preparing Hadoop job', progress: 20, step: 'step-data-loading' },
        { name: 'Submitting to Hadoop cluster', progress: 30, step: 'step-data-loading' },
        { name: 'Starting MapReduce job', progress: 40, step: 'step-processing' },
        { name: 'Running Map phase', progress: 50, step: 'step-processing' },
        { name: 'Running Reduce phase', progress: 60, step: 'step-processing' },
        { name: 'Collecting results', progress: 70, step: 'step-generating-results' },
        { name: 'Generating visualizations', progress: 80, step: 'step-generating-results' },
        { name: 'Saving output files', progress: 90, step: 'step-saving' },
        { name: 'Finalizing', progress: 100, step: 'step-saving' }
    ];
    
    let currentStep = 0;
    
    function processNextStep() {
        if (currentStep < steps.length) {
            const step = steps[currentStep];
            
            // Update progress
            updateProgressBar(step.progress);
            appendToLog(step.name + '...', 'info');
            
            // Update current step status
            setStepStatus(step.step, 'In Progress');
            
            // If moving to a new step, mark previous as complete
            if (currentStep > 0 && steps[currentStep-1].step !== step.step) {
                setStepStatus(steps[currentStep-1].step, 'Complete');
            }
            
            // Update processed items count for demonstration
            document.getElementById('processed-items').textContent = Math.floor(currentStep * 200);
            
            // Update processing rate
            document.getElementById('processing-rate').textContent = Math.floor(10 + Math.random() * 40) + '/sec';
            
            currentStep++;
            
            // Schedule next step
            setTimeout(processNextStep, 1000 + Math.random() * 1000);
        } else {
            // Job complete
            setJobComplete();
        }
    }
    
    // Start the simulation
    setTimeout(processNextStep, 1000);
}

function pollJobStatus(jobId) {
    // This function would poll a server-side endpoint for job status updates
    // It's a placeholder for the actual implementation
    console.log('Polling job status for job ID:', jobId);
}

function setJobComplete() {
    // Stop the timer
    stopProcessingTimer();
    
    // Update UI elements
    document.getElementById('analysis-status-badge').className = 'badge bg-success';
    document.getElementById('analysis-status-badge').innerHTML = '<i class="fas fa-check-circle"></i> Complete';
    document.getElementById('analysis-type-indicator').textContent = 'Analysis completed successfully';
    
    // Mark all steps as complete
    setStepStatus('step-data-loading', 'Complete');
    setStepStatus('step-processing', 'Complete');
    setStepStatus('step-generating-results', 'Complete');
    setStepStatus('step-saving', 'Complete');
    
    // Set progress to 100%
    updateProgressBar(100);
    
    // Add success log entry
    appendToLog('Hadoop job completed successfully!', 'success');
    
    // Show results section
    document.getElementById('analysis-results').style.display = 'block';
}

function setJobFailed(message) {
    // Stop the timer
    stopProcessingTimer();
    
    // Update UI elements
    document.getElementById('analysis-status-badge').className = 'badge bg-danger';
    document.getElementById('analysis-status-badge').innerHTML = '<i class="fas fa-exclamation-circle"></i> Failed';
    document.getElementById('analysis-type-indicator').textContent = 'Analysis failed: ' + message;
    
    // Add error log entry
    appendToLog('Hadoop job failed: ' + message, 'error');
}

function setStepStatus(stepId, status) {
    const step = document.getElementById(stepId);
    const statusElement = step.querySelector('.step-status');
    
    // Remove any existing status classes
    step.classList.remove('active', 'complete', 'error');
    
    switch (status) {
        case 'Pending':
            statusElement.textContent = 'Pending';
            break;
        case 'In Progress':
            statusElement.textContent = 'In Progress';
            step.classList.add('active');
            break;
        case 'Complete':
            statusElement.textContent = 'Complete';
            step.classList.add('complete');
            break;
        case 'Error':
            statusElement.textContent = 'Error';
            step.classList.add('error');
            break;
    }
}

function updateProgressBar(percentage) {
    const progressBar = document.querySelector('.progress-bar');
    const progressPercentage = document.getElementById('progress-percentage');
    
    progressBar.style.width = percentage + '%';
    progressPercentage.textContent = percentage + '%';
}

function appendToLog(message, type) {
    const logContainer = document.getElementById('analysis-log');
    const timestamp = new Date().toLocaleTimeString();
    
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry log-' + type;
    logEntry.innerHTML = `<span class="log-time">[${timestamp}]</span> ${message}`;
    
    logContainer.appendChild(logEntry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

let processingTimer;
let startTime;

function startProcessingTimer() {
    startTime = new Date();
    
    processingTimer = setInterval(function() {
        const currentTime = new Date();
        const elapsedMilliseconds = currentTime - startTime;
        
        // Format elapsed time as MM:SS
        const minutes = Math.floor(elapsedMilliseconds / 60000);
        const seconds = Math.floor((elapsedMilliseconds % 60000) / 1000);
        
        document.getElementById('processing-time').textContent = 
            minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
            
        // Update estimated completion time (simple estimation for demo)
        const progress = parseFloat(document.querySelector('.progress-bar').style.width);
        if (progress > 0 && progress < 100) {
            const totalTimeEstimate = (elapsedMilliseconds * 100) / progress;
            const remainingTime = totalTimeEstimate - elapsedMilliseconds;
            
            // Only show if we have a reasonable estimate
            if (remainingTime > 0) {
                const completionTime = new Date(currentTime.getTime() + remainingTime);
                document.getElementById('completion-estimate').textContent = 
                    completionTime.toLocaleTimeString();
            }
        }
    }, 1000);
}

function stopProcessingTimer() {
    if (processingTimer) {
        clearInterval(processingTimer);
    }
}

// Initialize Hadoop job execution features when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize existing functionality first
    // ...
    
    // Then initialize Hadoop job functionality
    initHadoopJobExecution();
    
    // Update the data source section initially
    updateDataSourceSection();
}); 