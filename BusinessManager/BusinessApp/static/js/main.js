// ===== Modern Business Manager JavaScript =====

// Initialize when DOM is loaded
$(document).ready(function() {
    // Initialize all components
    initializeNavigation();
    initializeCharts();
    initializeDataTables();
    initializeFormValidation();
    initializeDashboard();
    initializeNotifications();
    initializeProductSearch();
    initializeSalesForm();
    
    // Temporarily disable AOS animations to fix disappearing content
    // if (typeof AOS !== 'undefined') {
    //     AOS.init({
    //         duration: 800,
    //         easing: 'ease-in-out',
    //         once: true
    //     });
    // }
});

// ===== Navigation Functions =====
function initializeNavigation() {
    // Mobile sidebar toggle
    $('.navbar-toggler').on('click', function(e) {
        e.preventDefault();
        toggleMobileSidebar();
    });
    
    // Close sidebar when clicking close button
    $('#sidebarClose').on('click', function() {
        closeMobileSidebar();
    });
    
    // Close sidebar when clicking overlay
    $('#sidebarOverlay').on('click', function() {
        closeMobileSidebar();
    });
    
    // Close sidebar when clicking outside
    $(document).on('click', function(e) {
        if (!$(e.target).closest('#mobileSidebar, .navbar-toggler').length) {
            closeMobileSidebar();
        }
        
        // Close search field when clicking outside
        if (!$(e.target).closest('.search-container').length) {
            closeSearchField();
        }
    });
    
    // Search toggle functionality
    $('#searchToggle').on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        toggleSearchField();
    });
    
    // Close search field when pressing Escape
    $(document).on('keydown', function(e) {
        if (e.key === 'Escape') {
            closeSearchField();
        }
    });
    
    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        const target = $(this.getAttribute('href'));
        if (target.length) {
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 80
            }, 600);
        }
    });
}

// Mobile Sidebar Functions
function toggleMobileSidebar() {
    const sidebar = $('#mobileSidebar');
    const overlay = $('#sidebarOverlay');
    
    if (sidebar.hasClass('active')) {
        closeMobileSidebar();
    } else {
        openMobileSidebar();
    }
}

function openMobileSidebar() {
    $('#mobileSidebar').addClass('active');
    $('#sidebarOverlay').addClass('active');
    $('body').addClass('sidebar-open');
}

function closeMobileSidebar() {
    $('#mobileSidebar').removeClass('active');
    $('#sidebarOverlay').removeClass('active');
    $('body').removeClass('sidebar-open');
}

function toggleSidebar() {
    $('.modern-sidebar').toggleClass('show');
}

function closeSidebar() {
    $('.modern-sidebar').removeClass('show');
}

// Search Field Functions
function toggleSearchField() {
    const searchField = $('#searchField');
    const searchInput = $('#productSearch');
    
    if (searchField.hasClass('active')) {
        closeSearchField();
    } else {
        openSearchField();
    }
}

function openSearchField() {
    $('#searchField').addClass('active');
    setTimeout(() => {
        $('#productSearch').focus();
    }, 100);
}

function closeSearchField() {
    $('#searchField').removeClass('active');
    $('#searchResults').hide();
}

// ===== Dashboard Functions =====
function initializeDashboard() {
    if ($('#dashboard').length) {
        loadDashboardData();
        
        // Refresh dashboard data every 5 minutes
        setInterval(loadDashboardData, 300000);
    }
}

function loadDashboardData() {
    $.ajax({
        url: '/api/dashboard-data/',
        method: 'GET',
        success: function(data) {
            updateDashboardStats(data);
            updateSalesChart(data.sales_data);
            
            // Update low stock notification
            if (data.low_stock_count > 0) {
                showNotification('warning', `${data.low_stock_count} products are running low on stock!`);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error loading dashboard data:', error);
        }
    });
}

function updateDashboardStats(data) {
    // Animate stat cards
    $('.stat-value').each(function() {
        const $this = $(this);
        const finalValue = $this.text();
        
        $({ value: 0 }).animate({ value: finalValue }, {
            duration: 1000,
            step: function() {
                $this.text(Math.floor(this.value));
            },
            complete: function() {
                $this.text(finalValue);
            }
        });
    });
}

// ===== Chart Functions =====
function initializeCharts() {
    // Only initialize charts that don't already exist
    if ($('#salesChart').length && !window.salesChart) {
        console.log('Creating sales chart from initializeCharts');
        createSalesChart();
    }
    
    if ($('#revenueChart').length && !window.revenueChart) {
        createRevenueChart();
    }
    
    if ($('#expenseChart').length && !window.expenseChart) {
        createExpenseChart();
    }
}

function createSalesChart() {
    const ctx = document.getElementById('salesChart');
    if (!ctx) {
        console.log('Sales chart canvas not found');
        return;
    }
    
    // Destroy existing chart if it exists and has destroy method
    if (window.salesChart && typeof window.salesChart.destroy === 'function') {
        console.log('Destroying existing chart');
        window.salesChart.destroy();
        window.salesChart = null;
    }
    
    try {
        window.salesChart = new Chart(ctx.getContext('2d'), {
            type: 'line',
            data: {
                labels: ['Loading...'],
                datasets: [
                    {
                        label: 'Daily Sales (Tsh)',
                        data: [0],
                        borderColor: 'rgb(99, 102, 241)',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: 'rgb(99, 102, 241)',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }
                ]
            },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#6b7280',
                        font: {
                            size: 12
                        },
                        callback: function(value) {
                            return 'Tsh ' + value.toLocaleString();
                        }
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#6b7280',
                        font: {
                            size: 12
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#374151',
                        font: {
                            size: 13,
                            weight: '500'
                        },
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(17, 24, 39, 0.9)',
                    titleColor: '#f9fafb',
                    bodyColor: '#f9fafb',
                    borderColor: 'rgba(99, 102, 241, 0.3)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        title: function(context) {
                            return 'Date: ' + context[0].label;
                        },
                        label: function(context) {
                            return 'Sales: Tsh ' + context.parsed.y.toLocaleString();
                        }
                    }
                }
            },
            elements: {
                point: {
                    hoverBackgroundColor: 'rgb(99, 102, 241)',
                    hoverBorderColor: '#fff'
                }
            }
        }
    });
    
    console.log('Sales chart created successfully');
    
    // Load initial chart data with a small delay to ensure chart is fully ready
    setTimeout(function() {
        console.log('Loading initial chart data for 30 days...');
        loadSalesChartData(30);
    }, 200);
    
    } catch (error) {
        console.error('Error creating sales chart:', error);
        // Show error message in chart container
        const chartContainer = $('#salesChart').closest('.modern-card-body');
        chartContainer.html(`
            <div class="text-center py-4">
                <i class="fas fa-exclamation-triangle text-warning" style="font-size: 3rem;"></i>
                <p class="text-muted mt-3">Failed to create chart</p>
                <button class="btn btn-primary btn-sm" onclick="createSalesChart()">Retry</button>
            </div>
        `);
    }
}

function loadSalesChartData(days = 30) {
    console.log('Loading sales chart data for', days, 'days');
    
    // Update active button
    $('.btn-group .btn').removeClass('active');
    $(`.btn-group .btn[onclick="loadSalesChartData(${days})"]`).addClass('active');
    
    // Show loading state
    const chartContainer = $('#salesChart').closest('.modern-card-body');
    const loadingHtml = '<div class="chart-loading text-center p-4"><i class="fas fa-spinner fa-spin fa-2x text-primary"></i><p class="mt-2 text-muted">Loading chart data...</p></div>';
    
    // Remove existing loading/error messages
    chartContainer.find('.chart-loading, .alert').remove();
    chartContainer.append(loadingHtml);
    
    $.ajax({
        url: '/api/sales-chart/',
        method: 'GET',
        data: { days: days },
        success: function(data) {
            console.log('Sales chart data received:', data);
            
            // Remove loading state
            chartContainer.find('.chart-loading').remove();
            
            if (data.error) {
                console.error('API returned error:', data.error);
                // Show error message and try to display empty chart
                const errorHtml = `
                    <div class="alert alert-warning alert-dismissible fade show" role="alert">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Error loading data: ${data.error}. Showing empty chart.
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                `;
                chartContainer.prepend(errorHtml);
                updateSalesChart(data.data || []);
            } else {
                console.log('Successfully received chart data:', data.data);
                console.log('Chart data length:', data.data ? data.data.length : 0);
                
                // If we have data, use it; otherwise create sample data for visualization
                let chartData = data.data;
                if (!chartData || chartData.length === 0) {
                    console.log('No data received, creating sample data for demo');
                    chartData = createSampleChartData(days);
                } else {
                    // Check if all sales values are zero and create sample data if so
                    const totalSales = chartData.reduce((sum, item) => sum + parseFloat(item.sales || 0), 0);
                    if (totalSales === 0) {
                        console.log('All sales data is zero, creating sample data for demo');
                        chartData = createSampleChartData(days);
                    }
                }
                
                updateSalesChart(chartData);
                
                // No need to call updateChartSummary separately since updateSalesChart now handles stats
            }
        },
        error: function(xhr, status, error) {
            // Remove loading state
            chartContainer.find('.chart-loading').remove();
            console.error('Error loading sales chart data:', error);
            console.error('Response:', xhr.responseText);
            
            // Show empty chart with error message
            updateSalesChart([]);
            
            // Show user-friendly message
            const errorHtml = `
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Unable to load chart data. Please check your connection and try again.
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            chartContainer.prepend(errorHtml);
        }
    });
}

function updateSalesChart(salesData) {
    console.log('updateSalesChart called with:', salesData);
    
    if (!window.salesChart) {
        console.log('Sales chart not initialized, cannot update');
        return;
    }
    
    // Check if chart data structure exists
    if (!window.salesChart.data) {
        console.log('Chart data structure not ready, recreating chart...');
        createSalesChart();
        return;
    }
    
    // Check if datasets exist
    if (!window.salesChart.data.datasets || window.salesChart.data.datasets.length === 0) {
        console.log('Chart datasets not ready, recreating chart...');
        createSalesChart();
        return;
    }
    
    try {
        if (salesData && salesData.length > 0) {
            console.log('Updating chart with', salesData.length, 'data points');
            
            const labels = salesData.map(item => {
                const date = new Date(item.date);
                return date.toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric' 
                });
            });
            const data = salesData.map(item => parseFloat(item.sales) || 0);
            
            console.log('Chart labels:', labels);
            console.log('Chart data:', data);
            
            window.salesChart.data.labels = labels;
            window.salesChart.data.datasets[0].data = data;
        } else {
            console.log('No sales data available, showing empty chart with placeholder');
            // Show chart with some baseline data so the line is visible
            const today = new Date();
            const placeholderData = [];
            for (let i = 6; i >= 0; i--) {
                const date = new Date(today);
                date.setDate(date.getDate() - i);
                placeholderData.push(date.toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric' 
                }));
            }
            
            window.salesChart.data.labels = placeholderData;
            window.salesChart.data.datasets[0].data = [0, 0, 0, 0, 0, 0, 0];
        }
        
        window.salesChart.update('active');
        console.log('Chart updated successfully');
        
        // Update chart statistics using the API summary if available
        if (salesData && salesData.length > 0) {
            updateChartStats(salesData);
        } else {
            // Remove stats container if no data
            const chartContainer = $('#salesChart').closest('.modern-card');
            chartContainer.find('.chart-stats, .chart-summary').remove();
        }
    } catch (error) {
        console.error('Error updating chart:', error);
        // Try to recreate the chart
        setTimeout(() => {
            console.log('Attempting to recreate chart after error...');
            createSalesChart();
        }, 1000);
    }
}

function updateChartStats(salesData) {
    if (!salesData || salesData.length === 0) {
        // Remove stats if no data
        const chartContainer = $('#salesChart').closest('.modern-card');
        chartContainer.find('.chart-stats, .chart-summary').remove();
        return;
    }
    
    const totalSales = salesData.reduce((sum, item) => sum + parseFloat(item.sales || 0), 0);
    const avgSales = totalSales / salesData.length;
    const maxSales = Math.max(...salesData.map(item => parseFloat(item.sales || 0)));
    const totalTransactions = salesData.reduce((sum, item) => sum + parseInt(item.transactions || 0), 0);
    
    // Find chart container and update stats
    const chartContainer = $('#salesChart').closest('.modern-card');
    
    // Remove any existing stats containers to avoid duplicates
    chartContainer.find('.chart-stats, .chart-summary').remove();
    
    // Create comprehensive stats container
    const statsHtml = `
        <div class="chart-stats mt-3 p-3 bg-light rounded">
            <div class="row text-center">
                <div class="col-3">
                    <div class="stat-item">
                        <h6 class="stat-value text-primary mb-1">Tsh ${Math.round(totalSales).toLocaleString()}</h6>
                        <small class="text-muted">Total Sales</small>
                    </div>
                </div>
                <div class="col-3">
                    <div class="stat-item">
                        <h6 class="stat-value text-success mb-1">Tsh ${Math.round(avgSales).toLocaleString()}</h6>
                        <small class="text-muted">Daily Average</small>
                    </div>
                </div>
                <div class="col-3">
                    <div class="stat-item">
                        <h6 class="stat-value text-warning mb-1">Tsh ${Math.round(maxSales).toLocaleString()}</h6>
                        <small class="text-muted">Best Day</small>
                    </div>
                </div>
                <div class="col-3">
                    <div class="stat-item">
                        <h6 class="stat-value text-info mb-1">${totalTransactions.toLocaleString()}</h6>
                        <small class="text-muted">Transactions</small>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    chartContainer.find('.modern-card-body').append(statsHtml);
}

function createSampleChartData(days) {
    console.log('Creating sample chart data for', days, 'days');
    const sampleData = [];
    const today = new Date();
    
    for (let i = days - 1; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        
        // Create realistic sample sales data with more variety
        const randomFactor = Math.random();
        let sales = 0;
        let transactions = 0;
        
        // 85% chance of having sales (more realistic business pattern)
        if (randomFactor > 0.15) {
            // Varying sales amounts based on day patterns
            const baseAmount = 30000; // Base amount in Tsh
            const variance = Math.random() * 120000; // Up to 120k variance
            const dayOfWeek = date.getDay();
            
            // Weekend modifier (lower sales on weekends)
            const weekendMultiplier = (dayOfWeek === 0 || dayOfWeek === 6) ? 0.7 : 1.0;
            
            sales = Math.floor((baseAmount + variance) * weekendMultiplier);
            transactions = Math.floor(Math.random() * 15) + 1; // 1 to 15 transactions
        }
        
        sampleData.push({
            date: date.toISOString().split('T')[0],
            sales: sales,
            transactions: transactions
        });
    }
    
    console.log('Sample data created with total sales:', 
        sampleData.reduce((sum, item) => sum + item.sales, 0));
    return sampleData;
}

// ===== Data Tables =====
function initializeDataTables() {
    if ($.fn.DataTable) {
        $('.data-table').DataTable({
            responsive: true,
            pageLength: 25,
            order: [[0, 'desc']],
            language: {
                search: "Search:",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                paginate: {
                    first: "First",
                    last: "Last",
                    next: "Next",
                    previous: "Previous"
                }
            }
        });
    }
}

// ===== Form Validation =====
function initializeFormValidation() {
    // Bootstrap form validation
    $('.needs-validation').on('submit', function(e) {
        if (!this.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();
        }
        $(this).addClass('was-validated');
    });
    
    // Real-time validation
    $('.form-control').on('blur', function() {
        validateField($(this));
    });
    
    // Number input formatting
    $('.currency-input').on('input', function() {
        formatCurrency($(this));
    });
}

function validateField($field) {
    const value = $field.val().trim();
    const fieldType = $field.attr('type') || 'text';
    
    let isValid = true;
    let errorMessage = '';
    
    // Required field validation
    if ($field.prop('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required.';
    }
    
    // Email validation
    if (fieldType === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address.';
        }
    }
    
    // Display validation feedback
    const $feedback = $field.siblings('.invalid-feedback');
    if (!isValid) {
        $field.addClass('is-invalid').removeClass('is-valid');
        if ($feedback.length) {
            $feedback.text(errorMessage);
        }
    } else if (value) {
        $field.addClass('is-valid').removeClass('is-invalid');
    }
}

function formatCurrency($input) {
    let value = $input.val().replace(/[^\d.]/g, '');
    if (value) {
        value = parseFloat(value).toFixed(2);
        $input.val(value);
    }
}

// ===== Product Search =====
function initializeProductSearch() {
    $('#productSearch').on('input', debounce(function() {
        const query = $(this).val();
        if (query.length >= 2) {
            searchProducts(query);
        } else {
            $('#searchResults').empty().hide();
        }
    }, 300));
}

function searchProducts(query) {
    $.ajax({
        url: '/api/products/search/',
        method: 'GET',
        data: { q: query },
        success: function(data) {
            displaySearchResults(data.results);
        },
        error: function(xhr, status, error) {
            console.error('Error searching products:', error);
        }
    });
}

function displaySearchResults(products) {
    const $results = $('#searchResults');
    $results.empty();
    
    if (products.length > 0) {
        products.forEach(function(product) {
            const $item = $(`
                <div class="search-result-item" data-product-id="${product.id}">
                    <div class="product-info">
                        <strong>${product.name}</strong>
                        <span class="text-muted">${product.sku}</span>
                    </div>
                    <div class="product-price">
                        $${product.price}
                        <span class="stock-info">(${product.stock} in stock)</span>
                    </div>
                </div>
            `);
            
            $item.on('click', function() {
                selectProduct(product);
                $results.empty().hide();
            });
            
            $results.append($item);
        });
        
        $results.show();
    } else {
        $results.html('<div class="no-results">No products found</div>').show();
    }
}

// ===== Sales Form =====
function initializeSalesForm() {
    let saleItems = [];
    
    // Add product to sale
    $(document).on('click', '.add-to-sale', function() {
        const productId = $(this).data('product-id');
        const productName = $(this).data('product-name');
        const productPrice = parseFloat($(this).data('product-price'));
        
        addItemToSale({
            id: productId,
            name: productName,
            price: productPrice,
            quantity: 1
        });
    });
    
    // Remove item from sale
    $(document).on('click', '.remove-item', function() {
        const index = $(this).data('index');
        saleItems.splice(index, 1);
        updateSaleDisplay();
    });
    
    // Update quantity
    $(document).on('input', '.item-quantity', function() {
        const index = $(this).data('index');
        const quantity = parseInt($(this).val()) || 1;
        saleItems[index].quantity = quantity;
        updateSaleDisplay();
    });
    
    function addItemToSale(product) {
        const existingIndex = saleItems.findIndex(item => item.id === product.id);
        
        if (existingIndex >= 0) {
            saleItems[existingIndex].quantity += 1;
        } else {
            saleItems.push(product);
        }
        
        updateSaleDisplay();
    }
    
    function updateSaleDisplay() {
        const $saleItems = $('#saleItems');
        $saleItems.empty();
        
        let total = 0;
        
        saleItems.forEach(function(item, index) {
            const subtotal = item.price * item.quantity;
            total += subtotal;
            
            const $item = $(`
                <div class="sale-item">
                    <div class="item-info">
                        <strong>${item.name}</strong>
                    </div>
                    <div class="item-controls">
                        <input type="number" class="form-control item-quantity" 
                               value="${item.quantity}" min="1" data-index="${index}">
                        <span class="item-price">$${item.price.toFixed(2)}</span>
                        <span class="item-subtotal">$${subtotal.toFixed(2)}</span>
                        <button type="button" class="btn btn-sm btn-danger remove-item" 
                                data-index="${index}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `);
            
            $saleItems.append($item);
        });
        
        $('#saleTotal').text(`$${total.toFixed(2)}`);
        $('#totalAmount').val(total.toFixed(2));
        
        // Update hidden input for form submission
        $('#productsData').val(JSON.stringify(saleItems.map(item => ({
            product_id: item.id,
            quantity: item.quantity,
            unit_price: item.price
        }))));
    }
}

// ===== Notifications =====
function initializeNotifications() {
    // Mark notification as read
    $('.notification-item').on('click', function() {
        const notificationId = $(this).data('notification-id');
        if (notificationId) {
            markNotificationAsRead(notificationId);
        }
    });
    
    // Auto-hide alerts
    $('.alert').each(function() {
        const $alert = $(this);
        setTimeout(function() {
            $alert.fadeOut();
        }, 5000);
    });
}

function markNotificationAsRead(notificationId) {
    $.ajax({
        url: `/notifications/mark-read/${notificationId}/`,
        method: 'POST',
        headers: {
            'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        success: function(data) {
            if (data.success) {
                $(`.notification-item[data-notification-id="${notificationId}"]`).addClass('read');
                updateNotificationBadge();
            }
        },
        error: function(xhr, status, error) {
            console.error('Error marking notification as read:', error);
        }
    });
}

function updateNotificationBadge() {
    const unreadCount = $('.notification-item:not(.read)').length;
    const $badge = $('.notification-badge');
    
    if (unreadCount > 0) {
        $badge.text(unreadCount).show();
    } else {
        $badge.hide();
    }
}

function showNotification(type, message, duration = 5000) {
    const iconMap = {
        success: 'check-circle',
        error: 'exclamation-triangle',
        warning: 'exclamation-circle',
        info: 'info-circle'
    };
    
    const $notification = $(`
        <div class="alert alert-${type} alert-dismissible fade show notification-toast" role="alert">
            <i class="fas fa-${iconMap[type]} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
    
    $('.messages-container').prepend($notification);
    
    // Auto-hide after duration
    setTimeout(function() {
        $notification.fadeOut(function() {
            $(this).remove();
        });
    }, duration);
}

// ===== Vue.js Components =====
if (typeof Vue !== 'undefined') {
    // Dashboard Vue app
    const dashboardApp = new Vue({
        el: '#dashboard-app',
        data: {
            stats: {
                totalProducts: 0,
                totalSales: 0,
                totalRevenue: 0,
                totalExpenses: 0,
                profit: 0
            },
            recentSales: [],
            lowStockProducts: [],
            isLoading: false
        },
        methods: {
            loadData() {
                this.isLoading = true;
                
                fetch('/api/dashboard-data/')
                    .then(response => response.json())
                    .then(data => {
                        this.stats = data.stats || this.stats;
                        this.recentSales = data.recent_sales || [];
                        this.lowStockProducts = data.low_stock_products || [];
                    })
                    .catch(error => {
                        console.error('Error loading dashboard data:', error);
                        this.showNotification('error', 'Failed to load dashboard data');
                    })
                    .finally(() => {
                        this.isLoading = false;
                    });
            },
            formatCurrency(amount) {
                return new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD'
                }).format(amount);
            },
            showNotification(type, message) {
                showNotification(type, message);
            }
        },
        mounted() {
            this.loadData();
            // Refresh data every 5 minutes
            setInterval(this.loadData, 300000);
        }
    });
}

// ===== Utility Functions =====
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

function formatDate(date) {
    return new Date(date).toLocaleDateString();
}

function formatDateTime(date) {
    return new Date(date).toLocaleString();
}

// ===== Global AJAX Setup =====
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", $('[name=csrfmiddlewaretoken]').val());
        }
    }
});

function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

// ===== Print Functions =====
function printPage() {
    window.print();
}

function exportToPDF(elementId, filename = 'document.pdf') {
    // Implementation would depend on a PDF library like jsPDF
    console.log('Export to PDF functionality would be implemented here');
}

// ===== Loading Overlay =====
function showLoading() {
    if (!$('#loadingOverlay').length) {
        $('body').append(`
            <div id="loadingOverlay" class="loading-overlay">
                <div class="spinner"></div>
            </div>
        `);
    }
    $('#loadingOverlay').fadeIn();
}

function hideLoading() {
    $('#loadingOverlay').fadeOut();
}

// ===== Error Handling =====
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    // showNotification('error', 'An unexpected error occurred. Please try again.');
});

// ===== Service Worker Registration (for PWA capabilities) - Temporarily disabled =====
// if ('serviceWorker' in navigator) {
//     window.addEventListener('load', function() {
//         navigator.serviceWorker.register('/static/js/sw.js')
//             .then(function(registration) {
//                 console.log('SW registered: ', registration);
//             })
//             .catch(function(registrationError) {
//                 console.log('SW registration failed: ', registrationError);
//             });
//     });
// }

// ===== Responsive Image Loading =====
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Initialize lazy loading when DOM is ready
$(document).ready(function() {
    lazyLoadImages();
});

// ===== Local Storage Utilities =====
const LocalStorage = {
    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('Error saving to localStorage:', e);
        }
    },
    
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('Error reading from localStorage:', e);
            return defaultValue;
        }
    },
    
    remove(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.error('Error removing from localStorage:', e);
        }
    }
};

// ===== Theme Management =====
const ThemeManager = {
    init() {
        const savedTheme = LocalStorage.get('theme', 'light');
        this.setTheme(savedTheme);
        
        // Add theme toggle listener
        $('#themeToggle').on('click', () => {
            this.toggleTheme();
        });
    },
    
    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        LocalStorage.set('theme', theme);
        
        // Update toggle button
        const $toggle = $('#themeToggle');
        if (theme === 'dark') {
            $toggle.html('<i class="fas fa-sun"></i>');
        } else {
            $toggle.html('<i class="fas fa-moon"></i>');
        }
    },
    
    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    }
};

// Initialize theme management
$(document).ready(function() {
    ThemeManager.init();
});

// ===== Export for use in other files =====
window.BusinessManager = {
    showNotification,
    hideLoading,
    showLoading,
    formatCurrency,
    formatDate,
    formatDateTime,
    LocalStorage,
    ThemeManager
};