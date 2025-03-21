/**
 * Datasets.js - Handles loading and displaying social media datasets
 */

class DatasetBrowser {
    constructor() {
        this.redditDatasets = [];
        this.twitterDatasets = [];
        this.currentRedditDataset = null;
        this.currentTwitterDataset = null;
        this.redditPosts = [];
        this.twitterPosts = [];
        this.redditCurrentPage = 1;
        this.twitterCurrentPage = 1;
        this.postsPerPage = 10;
        
        this.initComponents();
        this.attachEventListeners();
        this.loadAvailableDatasets();
    }
    
    initComponents() {
        // Reddit elements
        this.redditDatasetSelect = document.getElementById('reddit-dataset-select');
        this.redditPostsContainer = document.getElementById('reddit-posts');
        this.redditPagination = document.getElementById('reddit-pagination');
        this.redditSort = document.getElementById('reddit-sort');
        this.redditSearch = document.getElementById('reddit-search');
        this.redditSearchBtn = document.getElementById('reddit-search-btn');
        this.downloadRedditBtn = document.getElementById('download-reddit-dataset');
        
        // Reddit filter elements
        this.redditKeywordFilter = document.getElementById('reddit-keyword-filter');
        this.redditApplyFilter = document.getElementById('reddit-apply-filter');
        this.redditClearFilter = document.getElementById('reddit-clear-filter');
        this.redditFilterBadges = document.getElementById('reddit-filter-badges');
        this.redditFilteredCount = document.getElementById('reddit-filtered-count');
        this.redditFilterMatchAny = document.getElementById('reddit-filter-match-any');
        this.redditQuickFilters = document.querySelectorAll('#reddit-content .quick-filter');
        
        // Twitter elements
        this.twitterDatasetSelect = document.getElementById('twitter-dataset-select');
        this.twitterPostsContainer = document.getElementById('twitter-posts');
        this.twitterPagination = document.getElementById('twitter-pagination');
        this.twitterSort = document.getElementById('twitter-sort');
        this.twitterSearch = document.getElementById('twitter-search');
        this.twitterSearchBtn = document.getElementById('twitter-search-btn');
        this.downloadTwitterBtn = document.getElementById('download-twitter-dataset');
        
        // Twitter filter elements
        this.twitterKeywordFilter = document.getElementById('twitter-keyword-filter');
        this.twitterApplyFilter = document.getElementById('twitter-apply-filter');
        this.twitterClearFilter = document.getElementById('twitter-clear-filter');
        this.twitterFilterBadges = document.getElementById('twitter-filter-badges');
        this.twitterFilteredCount = document.getElementById('twitter-filtered-count');
        this.twitterFilterMatchAny = document.getElementById('twitter-filter-match-any');
        this.twitterQuickFilters = document.querySelectorAll('#twitter-content .quick-filter');
        
        // Initialize filter keyword arrays
        this.redditFilterKeywords = [];
        this.twitterFilterKeywords = [];
        
        // Overview elements - Reddit
        this.redditSubreddit = document.getElementById('reddit-subreddit');
        this.redditFileType = document.getElementById('reddit-file-type');
        this.redditFileSize = document.getElementById('reddit-file-size');
        this.redditPostCount = document.getElementById('reddit-post-count');
        this.redditDateRange = document.getElementById('reddit-date-range');
        this.redditLastUpdated = document.getElementById('reddit-last-updated');
        
        // Overview elements - Twitter
        this.twitterTopic = document.getElementById('twitter-topic');
        this.twitterFileType = document.getElementById('twitter-file-type');
        this.twitterFileSize = document.getElementById('twitter-file-size');
        this.twitterTweetCount = document.getElementById('twitter-tweet-count');
        this.twitterDateRange = document.getElementById('twitter-date-range');
        this.twitterLastUpdated = document.getElementById('twitter-last-updated');
    }
    
    attachEventListeners() {
        // Reddit events
        if (this.redditDatasetSelect) {
            this.redditDatasetSelect.addEventListener('change', () => this.handleRedditDatasetChange());
        }
        
        if (this.redditSort) {
            this.redditSort.addEventListener('change', () => this.renderRedditPosts());
        }
        
        if (this.redditSearchBtn) {
            this.redditSearchBtn.addEventListener('click', () => this.renderRedditPosts());
        }
        
        if (this.redditSearch) {
            this.redditSearch.addEventListener('keyup', (e) => {
                if (e.key === 'Enter') {
                    this.renderRedditPosts();
                }
            });
        }
        
        if (this.downloadRedditBtn) {
            this.downloadRedditBtn.addEventListener('click', () => this.downloadDataset('reddit'));
        }
        
        // Reddit filter events
        if (this.redditApplyFilter) {
            this.redditApplyFilter.addEventListener('click', () => this.applyRedditFilter());
        }
        
        if (this.redditKeywordFilter) {
            this.redditKeywordFilter.addEventListener('keyup', (e) => {
                if (e.key === 'Enter') {
                    this.applyRedditFilter();
                }
            });
        }
        
        if (this.redditClearFilter) {
            this.redditClearFilter.addEventListener('click', () => this.clearRedditFilter());
        }
        
        if (this.redditFilterMatchAny) {
            this.redditFilterMatchAny.addEventListener('change', () => {
                if (this.redditFilterKeywords.length > 0) {
                    this.renderRedditPosts();
                }
            });
        }
        
        // Reddit quick filter events
        this.redditQuickFilters.forEach(button => {
            button.addEventListener('click', () => {
                const keyword = button.dataset.keyword;
                this.addRedditFilterKeyword(keyword);
                button.classList.add('active');
            });
        });
        
        // Twitter events
        if (this.twitterDatasetSelect) {
            this.twitterDatasetSelect.addEventListener('change', () => this.handleTwitterDatasetChange());
        }
        
        if (this.twitterSort) {
            this.twitterSort.addEventListener('change', () => this.renderTwitterPosts());
        }
        
        if (this.twitterSearchBtn) {
            this.twitterSearchBtn.addEventListener('click', () => this.renderTwitterPosts());
        }
        
        if (this.twitterSearch) {
            this.twitterSearch.addEventListener('keyup', (e) => {
                if (e.key === 'Enter') {
                    this.renderTwitterPosts();
                }
            });
        }
        
        if (this.downloadTwitterBtn) {
            this.downloadTwitterBtn.addEventListener('click', () => this.downloadDataset('twitter'));
        }
        
        // Twitter filter events
        if (this.twitterApplyFilter) {
            this.twitterApplyFilter.addEventListener('click', () => this.applyTwitterFilter());
        }
        
        if (this.twitterKeywordFilter) {
            this.twitterKeywordFilter.addEventListener('keyup', (e) => {
                if (e.key === 'Enter') {
                    this.applyTwitterFilter();
                }
            });
        }
        
        if (this.twitterClearFilter) {
            this.twitterClearFilter.addEventListener('click', () => this.clearTwitterFilter());
        }
        
        if (this.twitterFilterMatchAny) {
            this.twitterFilterMatchAny.addEventListener('change', () => {
                if (this.twitterFilterKeywords.length > 0) {
                    this.renderTwitterPosts();
                }
            });
        }
        
        // Twitter quick filter events
        this.twitterQuickFilters.forEach(button => {
            button.addEventListener('click', () => {
                const keyword = button.dataset.keyword;
                this.addTwitterFilterKeyword(keyword);
                button.classList.add('active');
            });
        });
    }
    
    async loadAvailableDatasets() {
        try {
            const response = await fetch('/api/datasets');
            const data = await response.json();
            
            if (data.success && data.datasets) {
                // Filter datasets by source
                this.redditDatasets = data.datasets.filter(d => d.source === 'reddit');
                this.twitterDatasets = data.datasets.filter(d => d.source === 'twitter');
                
                this.populateDatasetSelects();
            }
        } catch (error) {
            console.error('Error loading datasets:', error);
            this.showErrorMessage('Failed to load available datasets');
        }
    }
    
    populateDatasetSelects() {
        // Populate Reddit dropdown
        if (this.redditDatasetSelect) {
            this.redditDatasetSelect.innerHTML = '';
            
            if (this.redditDatasets.length > 0) {
                this.redditDatasetSelect.innerHTML = '<option value="">Select a Reddit dataset...</option>';
                
                this.redditDatasets.forEach(dataset => {
                    const option = document.createElement('option');
                    option.value = dataset.id;
                    option.textContent = dataset.name;
                    this.redditDatasetSelect.appendChild(option);
                });
                
                // Load the first dataset by default
                this.redditDatasetSelect.value = this.redditDatasets[0].id;
                this.handleRedditDatasetChange();
            } else {
                this.redditDatasetSelect.innerHTML = '<option value="">No Reddit datasets available</option>';
                this.showEmptyState(this.redditPostsContainer, 'reddit');
            }
        }
        
        // Populate Twitter dropdown
        if (this.twitterDatasetSelect) {
            this.twitterDatasetSelect.innerHTML = '';
            
            if (this.twitterDatasets.length > 0) {
                this.twitterDatasetSelect.innerHTML = '<option value="">Select a Twitter dataset...</option>';
                
                this.twitterDatasets.forEach(dataset => {
                    const option = document.createElement('option');
                    option.value = dataset.id;
                    option.textContent = dataset.name;
                    this.twitterDatasetSelect.appendChild(option);
                });
                
                // Load the first dataset by default
                this.twitterDatasetSelect.value = this.twitterDatasets[0].id;
                this.handleTwitterDatasetChange();
            } else {
                this.twitterDatasetSelect.innerHTML = '<option value="">No Twitter datasets available</option>';
                this.showEmptyState(this.twitterPostsContainer, 'twitter');
            }
        }
    }
    
    async handleRedditDatasetChange() {
        const datasetId = this.redditDatasetSelect.value;
        if (!datasetId) return;
        
        const dataset = this.redditDatasets.find(d => d.id === datasetId);
        if (!dataset) return;
        
        this.currentRedditDataset = dataset;
        this.updateRedditOverview(dataset);
        
        // Show loading state
        this.redditPostsContainer.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3">Loading posts...</p>
            </div>
        `;
        
        try {
            await this.loadRedditPosts(dataset);
            this.renderRedditPosts();
        } catch (error) {
            console.error('Error loading Reddit posts:', error);
            this.showErrorMessage('Failed to load Reddit posts', this.redditPostsContainer);
        }
    }
    
    async handleTwitterDatasetChange() {
        const datasetId = this.twitterDatasetSelect.value;
        if (!datasetId) return;
        
        const dataset = this.twitterDatasets.find(d => d.id === datasetId);
        if (!dataset) return;
        
        this.currentTwitterDataset = dataset;
        this.updateTwitterOverview(dataset);
        
        // Show loading state
        this.twitterPostsContainer.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3">Loading tweets...</p>
            </div>
        `;
        
        try {
            await this.loadTwitterPosts(dataset);
            this.renderTwitterPosts();
        } catch (error) {
            console.error('Error loading Twitter posts:', error);
            this.showErrorMessage('Failed to load Twitter posts', this.twitterPostsContainer);
        }
    }
    
    updateRedditOverview(dataset) {
        const subreddit = dataset.id.includes('_') ? 
            dataset.id.split('_')[1] || 'Unknown' : 'Unknown';
        
        this.redditSubreddit.textContent = subreddit;
        this.redditFileType.textContent = dataset.type.toUpperCase();
        this.redditFileSize.textContent = dataset.size;
        this.redditPostCount.textContent = dataset.item_count || 'Unknown';
        this.redditDateRange.textContent = dataset.date_range || 'All time';
        this.redditLastUpdated.textContent = new Date(dataset.date).toLocaleDateString();
    }
    
    updateTwitterOverview(dataset) {
        const topic = dataset.id.includes('_') ? 
            dataset.id.split('_')[2] || 'Unknown' : 'Unknown';
        
        this.twitterTopic.textContent = topic;
        this.twitterFileType.textContent = dataset.type.toUpperCase();
        this.twitterFileSize.textContent = dataset.size;
        this.twitterTweetCount.textContent = dataset.item_count || 'Unknown';
        this.twitterDateRange.textContent = dataset.date_range || 'All time';
        this.twitterLastUpdated.textContent = new Date(dataset.date).toLocaleDateString();
    }
    
    async loadRedditPosts(dataset) {
        // For CSV files
        if (dataset.type === 'csv') {
            const response = await fetch(dataset.path);
            const csvText = await response.text();
            
            // Parse CSV
            const lines = csvText.split('\n');
            const headers = lines[0].split(',');
            
            this.redditPosts = [];
            
            for (let i = 1; i < lines.length; i++) {
                if (!lines[i].trim()) continue;
                
                const values = lines[i].split(',');
                const post = {};
                
                headers.forEach((header, index) => {
                    post[header] = values[index];
                });
                
                this.redditPosts.push(post);
            }
        } 
        // For JSON files
        else if (dataset.type === 'json') {
            const response = await fetch(dataset.path);
            this.redditPosts = await response.json();
            
            // If the response is an object with a data property
            if (!Array.isArray(this.redditPosts) && this.redditPosts.data) {
                this.redditPosts = this.redditPosts.data;
            }
            
            // Debug the structure of posts
            if (this.redditPosts.length > 0) {
                console.log('Reddit post structure:', this.redditPosts[0]);
            }
        }
    }
    
    async loadTwitterPosts(dataset) {
        // For CSV files
        if (dataset.type === 'csv') {
            const response = await fetch(dataset.path);
            const csvText = await response.text();
            
            // Parse CSV
            const lines = csvText.split('\n');
            const headers = lines[0].split(',');
            
            this.twitterPosts = [];
            
            for (let i = 1; i < lines.length; i++) {
                if (!lines[i].trim()) continue;
                
                const values = lines[i].split(',');
                const tweet = {};
                
                headers.forEach((header, index) => {
                    tweet[header] = values[index];
                });
                
                this.twitterPosts.push(tweet);
            }
        } 
        // For JSON files
        else if (dataset.type === 'json') {
            const response = await fetch(dataset.path);
            this.twitterPosts = await response.json();
            
            // If the response is an object with a data property
            if (!Array.isArray(this.twitterPosts) && this.twitterPosts.data) {
                this.twitterPosts = this.twitterPosts.data;
            }
        }
    }
    
    renderRedditPosts() {
        if (!this.redditPosts || this.redditPosts.length === 0) {
            this.showEmptyState(this.redditPostsContainer, 'reddit');
            return;
        }
        
        // Apply search filter
        let filteredPosts = this.redditPosts;
        if (this.redditSearch && this.redditSearch.value.trim()) {
            const searchTerm = this.redditSearch.value.trim().toLowerCase();
            filteredPosts = filteredPosts.filter(post => 
                (post.title && post.title.toLowerCase().includes(searchTerm)) || 
                (post.text && post.text.toLowerCase().includes(searchTerm)) ||
                (post.author && post.author.toLowerCase().includes(searchTerm))
            );
        }
        
        // Apply keyword filters if any are set
        if (this.redditFilterKeywords.length > 0) {
            const matchAny = this.redditFilterMatchAny && this.redditFilterMatchAny.checked;
            
            filteredPosts = filteredPosts.filter(post => {
                const title = post.title ? post.title.toLowerCase() : '';
                const text = post.text ? post.text.toLowerCase() : '';
                const combinedText = title + ' ' + text;
                
                if (matchAny) {
                    // Match if ANY keyword is found
                    return this.redditFilterKeywords.some(keyword => 
                        combinedText.includes(keyword.toLowerCase())
                    );
                } else {
                    // Match if ALL keywords are found
                    return this.redditFilterKeywords.every(keyword => 
                        combinedText.includes(keyword.toLowerCase())
                    );
                }
            });
            
            // Update filtered count
            if (this.redditFilteredCount) {
                this.redditFilteredCount.textContent = filteredPosts.length;
            }
        }
        
        // Apply sorting
        if (this.redditSort) {
            const sortOption = this.redditSort.value;
            
            switch (sortOption) {
                case 'date-desc':
                    filteredPosts.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
                    break;
                case 'date-asc':
                    filteredPosts.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
                    break;
                case 'score-desc':
                    filteredPosts.sort((a, b) => this.getNumericValue(b.upvotes) - this.getNumericValue(a.upvotes));
                    break;
                case 'comments-desc':
                    filteredPosts.sort((a, b) => this.getCommentCount(b.comments) - this.getCommentCount(a.comments));
                    break;
            }
        }
        
        // Pagination
        const totalPages = Math.ceil(filteredPosts.length / this.postsPerPage);
        const startIndex = (this.redditCurrentPage - 1) * this.postsPerPage;
        const paginatedPosts = filteredPosts.slice(startIndex, startIndex + this.postsPerPage);
        
        // Log the first post data for debugging
        if (paginatedPosts.length > 0) {
            const firstPost = paginatedPosts[0];
            console.log('First Reddit post:', firstPost);
            console.log('Comments type:', typeof firstPost.comments);
            console.log('Comments value:', firstPost.comments);
            console.log('Upvotes type:', typeof firstPost.upvotes);
            console.log('Upvotes value:', firstPost.upvotes);
        }
        
        // Render posts
        this.redditPostsContainer.innerHTML = '';
        
        if (paginatedPosts.length === 0) {
            this.redditPostsContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-search"></i>
                    <h4>No posts found</h4>
                    <p>Try adjusting your search criteria</p>
                </div>
            `;
            this.redditPagination.innerHTML = '';
            return;
        }
        
        paginatedPosts.forEach(post => {
            const postElement = document.createElement('div');
            postElement.className = 'reddit-post';
            
            const sentimentClass = this.getSentimentClass(post.sentiment);
            const formattedDate = this.formatDate(post.timestamp);
            
            // Get properly formatted upvotes and comments count
            const upvotes = this.getNumericValue(post.upvotes);
            const commentCount = this.getCommentCount(post.comments);
            
            postElement.innerHTML = `
                <div class="reddit-post-header">
                    <div>
                        <h3 class="reddit-post-title">${post.title || 'Untitled Post'}</h3>
                        <div class="reddit-post-meta">
                            <div class="reddit-post-author">
                                <i class="fas fa-user"></i> ${post.author || 'Anonymous'}
                            </div>
                            <div class="reddit-post-date">
                                <i class="far fa-calendar"></i> ${formattedDate}
                            </div>
                            <div class="badge ${sentimentClass}">
                                ${this.getSentimentIcon(post.sentiment)} ${post.sentiment || 'unknown'}
                            </div>
                        </div>
                    </div>
                    <span class="reddit-post-subreddit">r/${this.currentRedditDataset.id.split('_')[1] || 'subreddit'}</span>
                </div>
                <div class="reddit-post-content">
                    ${post.text || 'No content available'}
                </div>
                <div class="reddit-post-stats">
                    <div class="reddit-post-score">
                        <i class="fas fa-arrow-up"></i> ${upvotes} upvotes
                    </div>
                    <div class="reddit-post-comments">
                        <i class="fas fa-comment"></i> ${commentCount} comments
                    </div>
                </div>
            `;
            
            this.redditPostsContainer.appendChild(postElement);
        });
        
        // Render pagination
        this.renderPagination(totalPages, this.redditCurrentPage, this.redditPagination, (page) => {
            this.redditCurrentPage = page;
            this.renderRedditPosts();
        });
    }
    
    renderTwitterPosts() {
        if (!this.twitterPosts || this.twitterPosts.length === 0) {
            this.showEmptyState(this.twitterPostsContainer, 'twitter');
            return;
        }
        
        // Apply search filter
        let filteredPosts = this.twitterPosts;
        if (this.twitterSearch && this.twitterSearch.value.trim()) {
            const searchTerm = this.twitterSearch.value.trim().toLowerCase();
            filteredPosts = filteredPosts.filter(tweet => 
                (tweet.text && tweet.text.toLowerCase().includes(searchTerm)) ||
                (tweet.user && tweet.user.toLowerCase().includes(searchTerm))
            );
        }
        
        // Apply keyword filters if any are set
        if (this.twitterFilterKeywords.length > 0) {
            const matchAny = this.twitterFilterMatchAny && this.twitterFilterMatchAny.checked;
            
            filteredPosts = filteredPosts.filter(tweet => {
                const text = tweet.text ? tweet.text.toLowerCase() : '';
                
                if (matchAny) {
                    // Match if ANY keyword is found
                    return this.twitterFilterKeywords.some(keyword => 
                        text.includes(keyword.toLowerCase())
                    );
                } else {
                    // Match if ALL keywords are found
                    return this.twitterFilterKeywords.every(keyword => 
                        text.includes(keyword.toLowerCase())
                    );
                }
            });
            
            // Update filtered count
            if (this.twitterFilteredCount) {
                this.twitterFilteredCount.textContent = filteredPosts.length;
            }
        }
        
        // Apply sorting
        if (this.twitterSort) {
            const sortOption = this.twitterSort.value;
            
            switch (sortOption) {
                case 'date-desc':
                    filteredPosts.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
                    break;
                case 'date-asc':
                    filteredPosts.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
                    break;
                case 'likes-desc':
                    filteredPosts.sort((a, b) => this.getNumericValue(b.likes) - this.getNumericValue(a.likes));
                    break;
                case 'retweets-desc':
                    filteredPosts.sort((a, b) => this.getNumericValue(b.retweets) - this.getNumericValue(a.retweets));
                    break;
            }
        }
        
        // Pagination
        const totalPages = Math.ceil(filteredPosts.length / this.postsPerPage);
        const startIndex = (this.twitterCurrentPage - 1) * this.postsPerPage;
        const paginatedPosts = filteredPosts.slice(startIndex, startIndex + this.postsPerPage);
        
        // Render posts
        this.twitterPostsContainer.innerHTML = '';
        
        if (paginatedPosts.length === 0) {
            this.twitterPostsContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-search"></i>
                    <h4>No tweets found</h4>
                    <p>Try adjusting your search criteria</p>
                </div>
            `;
            this.twitterPagination.innerHTML = '';
            return;
        }
        
        paginatedPosts.forEach(tweet => {
            const tweetElement = document.createElement('div');
            tweetElement.className = 'twitter-post';
            
            const sentimentClass = this.getSentimentClass(tweet.sentiment);
            const formattedDate = this.formatDate(tweet.timestamp);
            const formattedText = this.formatTwitterText(tweet.text);
            
            // Get numeric values for stats
            const likes = this.getNumericValue(tweet.likes);
            const retweets = this.getNumericValue(tweet.retweets);
            const replies = this.getNumericValue(tweet.replies);
            
            tweetElement.innerHTML = `
                <div class="twitter-post-header">
                    <div class="twitter-post-user">
                        <div class="twitter-post-avatar">
                            <i class="fas fa-user fa-2x"></i>
                        </div>
                        <div class="twitter-post-user-info">
                            <div class="twitter-post-name">@${tweet.user || 'anonymous'}</div>
                            <div class="twitter-post-username text-muted">User</div>
                        </div>
                    </div>
                    <div>
                        <span class="badge ${sentimentClass}">
                            ${this.getSentimentIcon(tweet.sentiment)} ${tweet.sentiment || 'unknown'}
                        </span>
                    </div>
                </div>
                <div class="twitter-post-content">
                    ${formattedText || 'No content available'}
                </div>
                <div class="twitter-post-date">
                    <i class="far fa-clock"></i> ${formattedDate}
                </div>
                <div class="twitter-post-stats">
                    <div class="twitter-post-likes">
                        <i class="fas fa-heart"></i> ${likes}
                    </div>
                    <div class="twitter-post-retweets">
                        <i class="fas fa-retweet"></i> ${retweets}
                    </div>
                    <div class="twitter-post-replies">
                        <i class="fas fa-reply"></i> ${replies}
                    </div>
                </div>
            `;
            
            this.twitterPostsContainer.appendChild(tweetElement);
        });
        
        // Render pagination
        this.renderPagination(totalPages, this.twitterCurrentPage, this.twitterPagination, (page) => {
            this.twitterCurrentPage = page;
            this.renderTwitterPosts();
        });
    }
    
    renderPagination(totalPages, currentPage, paginationElement, callback) {
        if (!paginationElement) return;
        
        paginationElement.innerHTML = '';
        
        if (totalPages <= 1) return;
        
        // Previous button
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
        prevLi.innerHTML = `
            <a class="page-link" href="#" aria-label="Previous">
                <span aria-hidden="true">&laquo;</span>
            </a>
        `;
        if (currentPage > 1) {
            prevLi.addEventListener('click', (e) => {
                e.preventDefault();
                callback(currentPage - 1);
            });
        }
        paginationElement.appendChild(prevLi);
        
        // Page numbers
        const maxPages = 5;
        const startPage = Math.max(1, currentPage - Math.floor(maxPages / 2));
        const endPage = Math.min(totalPages, startPage + maxPages - 1);
        
        for (let i = startPage; i <= endPage; i++) {
            const pageLi = document.createElement('li');
            pageLi.className = `page-item ${i === currentPage ? 'active' : ''}`;
            pageLi.innerHTML = `<a class="page-link" href="#">${i}</a>`;
            
            pageLi.addEventListener('click', (e) => {
                e.preventDefault();
                callback(i);
            });
            
            paginationElement.appendChild(pageLi);
        }
        
        // Next button
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
        nextLi.innerHTML = `
            <a class="page-link" href="#" aria-label="Next">
                <span aria-hidden="true">&raquo;</span>
            </a>
        `;
        if (currentPage < totalPages) {
            nextLi.addEventListener('click', (e) => {
                e.preventDefault();
                callback(currentPage + 1);
            });
        }
        paginationElement.appendChild(nextLi);
    }
    
    showEmptyState(container, type) {
        if (!container) return;
        
        let message = type === 'reddit' ? 'No Reddit posts available' : 'No Tweets available';
        let icon = type === 'reddit' ? 'fa-reddit' : 'fa-twitter';
        
        container.innerHTML = `
            <div class="empty-state">
                <i class="fab ${icon}"></i>
                <h4>${message}</h4>
                <p>Select a dataset to view posts</p>
            </div>
        `;
    }
    
    showErrorMessage(message, container = null) {
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger mt-3">
                    <i class="fas fa-exclamation-circle me-2"></i> ${message}
                </div>
            `;
        } else {
            const alertElement = document.createElement('div');
            alertElement.className = 'alert alert-danger alert-dismissible fade show';
            alertElement.innerHTML = `
                <i class="fas fa-exclamation-circle me-2"></i> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            document.querySelector('.datasets-container').prepend(alertElement);
            
            setTimeout(() => {
                alertElement.remove();
            }, 5000);
        }
    }
    
    getSentimentClass(sentiment) {
        if (!sentiment) return 'bg-secondary';
        
        switch (sentiment.toLowerCase()) {
            case 'positive':
                return 'bg-success';
            case 'negative':
                return 'bg-danger';
            case 'neutral':
                return 'bg-info';
            default:
                return 'bg-secondary';
        }
    }
    
    getSentimentIcon(sentiment) {
        if (!sentiment) return '<i class="fas fa-question-circle"></i>';
        
        switch (sentiment.toLowerCase()) {
            case 'positive':
                return '<i class="fas fa-smile"></i>';
            case 'negative':
                return '<i class="fas fa-frown"></i>';
            case 'neutral':
                return '<i class="fas fa-meh"></i>';
            default:
                return '<i class="fas fa-question-circle"></i>';
        }
    }
    
    formatDate(dateString) {
        if (!dateString) return 'Unknown date';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleString();
        } catch (e) {
            return dateString;
        }
    }
    
    formatTwitterText(text) {
        if (!text) return '';
        
        // Format hashtags
        return text.replace(/#(\w+)/g, '<span class="hashtag">#$1</span>');
    }
    
    downloadDataset(type) {
        const dataset = type === 'reddit' ? this.currentRedditDataset : this.currentTwitterDataset;
        
        if (!dataset) {
            this.showErrorMessage(`No ${type} dataset selected`);
            return;
        }
        
        // Create download link
        const a = document.createElement('a');
        a.href = dataset.path;
        a.download = `${dataset.id}.${dataset.type}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
    
    /**
     * Helper method to extract a numeric value from various data types
     * @param {*} value - The value to convert to a number
     * @returns {number} The numeric value or 0 if not convertible
     */
    getNumericValue(value) {
        if (value === undefined || value === null) return 0;
        
        // If value is already a number
        if (typeof value === 'number') return value;
        
        // If value is a string
        if (typeof value === 'string') {
            const parsed = parseInt(value);
            return isNaN(parsed) ? 0 : parsed;
        }
        
        // If value is an array
        if (Array.isArray(value)) {
            return value.length;
        }
        
        // If value is an object
        if (typeof value === 'object') {
            // Look for common count properties
            const possibleProps = ['count', 'value', 'total'];
            
            for (const prop of possibleProps) {
                if (value[prop] !== undefined) {
                    const parsed = parseInt(value[prop]);
                    return isNaN(parsed) ? 0 : parsed;
                }
            }
            
            // Try to convert the object itself
            try {
                const parsed = parseInt(value.toString());
                return isNaN(parsed) ? 0 : parsed;
            } catch (e) {
                return 0;
            }
        }
        
        return 0;
    }
    
    /**
     * Special method for handling comment counts which might be
     * in various formats (number, string, array, nested objects)
     * @param {*} comments - Comment data in various formats
     * @returns {number} The comment count
     */
    getCommentCount(comments) {
        // If comment is undefined/null
        if (comments === undefined || comments === null) return 0;
        
        // If comments is an array, return its length
        if (Array.isArray(comments)) {
            return comments.length;
        }
        
        // If comments is a simple value
        if (typeof comments === 'number') return comments;
        if (typeof comments === 'string') {
            const parsed = parseInt(comments);
            return isNaN(parsed) ? 0 : parsed;
        }
        
        // If comments is an object
        if (typeof comments === 'object') {
            // First try to check if it has a length property
            if ('length' in comments) {
                return this.getNumericValue(comments.length);
            }
            
            // Look for a count property
            const possibleProps = ['count', 'total', 'num', 'number'];
            for (const prop of possibleProps) {
                if (comments[prop] !== undefined) {
                    return this.getNumericValue(comments[prop]);
                }
            }
            
            // If it's a complex nested structure like the one in the screenshot,
            // just count the number of keys and hope that's close to the comment count
            try {
                return Object.keys(comments).length;
            } catch (e) {
                return 0;
            }
        }
        
        return 0;
    }
    
    // Add new filter methods
    applyRedditFilter() {
        if (!this.redditKeywordFilter) return;
        
        const keywords = this.redditKeywordFilter.value.trim();
        if (!keywords) return;
        
        // Split by commas and process each keyword
        const keywordArray = keywords.split(',')
            .map(k => k.trim())
            .filter(k => k.length > 0);
        
        // Add each keyword
        keywordArray.forEach(keyword => this.addRedditFilterKeyword(keyword));
        
        // Clear the input
        this.redditKeywordFilter.value = '';
    }
    
    addRedditFilterKeyword(keyword) {
        if (!keyword || this.redditFilterKeywords.includes(keyword)) return;
        
        // Add to keywords array
        this.redditFilterKeywords.push(keyword);
        
        // Create and add badge
        this.renderRedditFilterBadges();
        
        // Re-render posts with filter
        this.renderRedditPosts();
    }
    
    renderRedditFilterBadges() {
        if (!this.redditFilterBadges) return;
        
        this.redditFilterBadges.innerHTML = '';
        
        this.redditFilterKeywords.forEach(keyword => {
            const badge = document.createElement('div');
            badge.className = 'filter-badge';
            badge.innerHTML = `
                <span class="badge-text">${keyword}</span>
                <span class="badge-remove" data-keyword="${keyword}">
                    <i class="fas fa-times"></i>
                </span>
            `;
            
            // Add click handler for removing
            badge.querySelector('.badge-remove').addEventListener('click', () => {
                this.removeRedditFilterKeyword(keyword);
            });
            
            this.redditFilterBadges.appendChild(badge);
        });
        
        // Update quick filter buttons
        this.redditQuickFilters.forEach(button => {
            const buttonKeyword = button.dataset.keyword;
            button.classList.toggle('active', this.redditFilterKeywords.includes(buttonKeyword));
        });
    }
    
    removeRedditFilterKeyword(keyword) {
        this.redditFilterKeywords = this.redditFilterKeywords.filter(k => k !== keyword);
        this.renderRedditFilterBadges();
        this.renderRedditPosts();
    }
    
    clearRedditFilter() {
        this.redditFilterKeywords = [];
        this.renderRedditFilterBadges();
        this.renderRedditPosts();
        
        // Update count display
        if (this.redditFilteredCount) {
            this.redditFilteredCount.textContent = this.redditPosts ? this.redditPosts.length : 0;
        }
    }
    
    applyTwitterFilter() {
        if (!this.twitterKeywordFilter) return;
        
        const keywords = this.twitterKeywordFilter.value.trim();
        if (!keywords) return;
        
        // Split by commas and process each keyword
        const keywordArray = keywords.split(',')
            .map(k => k.trim())
            .filter(k => k.length > 0);
        
        // Add each keyword
        keywordArray.forEach(keyword => this.addTwitterFilterKeyword(keyword));
        
        // Clear the input
        this.twitterKeywordFilter.value = '';
    }
    
    addTwitterFilterKeyword(keyword) {
        if (!keyword || this.twitterFilterKeywords.includes(keyword)) return;
        
        // Add to keywords array
        this.twitterFilterKeywords.push(keyword);
        
        // Create and add badge
        this.renderTwitterFilterBadges();
        
        // Re-render posts with filter
        this.renderTwitterPosts();
    }
    
    renderTwitterFilterBadges() {
        if (!this.twitterFilterBadges) return;
        
        this.twitterFilterBadges.innerHTML = '';
        
        this.twitterFilterKeywords.forEach(keyword => {
            const badge = document.createElement('div');
            badge.className = 'filter-badge';
            badge.innerHTML = `
                <span class="badge-text">${keyword}</span>
                <span class="badge-remove" data-keyword="${keyword}">
                    <i class="fas fa-times"></i>
                </span>
            `;
            
            // Add click handler for removing
            badge.querySelector('.badge-remove').addEventListener('click', () => {
                this.removeTwitterFilterKeyword(keyword);
            });
            
            this.twitterFilterBadges.appendChild(badge);
        });
        
        // Update quick filter buttons
        this.twitterQuickFilters.forEach(button => {
            const buttonKeyword = button.dataset.keyword;
            button.classList.toggle('active', this.twitterFilterKeywords.includes(buttonKeyword));
        });
    }
    
    removeTwitterFilterKeyword(keyword) {
        this.twitterFilterKeywords = this.twitterFilterKeywords.filter(k => k !== keyword);
        this.renderTwitterFilterBadges();
        this.renderTwitterPosts();
    }
    
    clearTwitterFilter() {
        this.twitterFilterKeywords = [];
        this.renderTwitterFilterBadges();
        this.renderTwitterPosts();
        
        // Update count display
        if (this.twitterFilteredCount) {
            this.twitterFilteredCount.textContent = this.twitterPosts ? this.twitterPosts.length : 0;
        }
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    new DatasetBrowser();
});