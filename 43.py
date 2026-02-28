# alone.py - Fixed Complete Facebook Account Validator
from flask import Flask, render_template_string, request, jsonify, send_file
import os
import sys
import requests
import re
import json
import time
import base64
from datetime import datetime
import io
from werkzeug.utils import secure_filename
import threading
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = 'facebook-checker-secret-key-2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# -------- HTML Template (Fixed JavaScript) --------
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Cookie & Token Checker v3.0</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css">
    <style>
        :root {
            --primary: #1877f2;
            --secondary: #42b72a;
            --success: #198754;
            --danger: #dc3545;
            --warning: #ffc107;
            --info: #0dcaf0;
            --dark: #18191a;
            --darker: #121416;
            --light: #f0f2f5;
            --facebook-blue: #1877f2;
            --facebook-green: #42b72a;
        }
        
        body {
            background: linear-gradient(135deg, var(--darker), #0c0e10);
            color: var(--light);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            background-attachment: fixed;
        }
        
        .logo-header {
            background: linear-gradient(90deg, var(--facebook-blue), var(--facebook-green));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            text-align: center;
            padding: 20px 0;
            margin-bottom: 30px;
            border-bottom: 3px solid rgba(24, 119, 242, 0.3);
        }
        
        .logo-text {
            font-family: 'Arial Black', sans-serif;
            font-size: 2.5rem;
            text-shadow: 0 2px 10px rgba(24, 119, 242, 0.3);
            letter-spacing: 1px;
        }
        
        .version {
            font-size: 1rem;
            opacity: 0.8;
            margin-top: -10px;
        }
        
        .card-premium {
            background: rgba(30, 31, 32, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(24, 119, 242, 0.3);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
            margin-bottom: 25px;
        }
        
        .card-premium:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(24, 119, 242, 0.2);
            border-color: var(--facebook-blue);
        }
        
        .card-header-premium {
            background: linear-gradient(90deg, var(--facebook-blue), var(--facebook-green));
            color: white;
            border-radius: 15px 15px 0 0 !important;
            padding: 15px 25px;
            font-weight: bold;
            border: none;
        }
        
        .btn-facebook {
            background: linear-gradient(90deg, var(--facebook-blue), var(--facebook-green));
            border: none;
            color: white;
            padding: 12px 30px;
            border-radius: 8px;
            font-weight: bold;
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }
        
        .btn-facebook:before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: 0.5s;
        }
        
        .btn-facebook:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(24, 119, 242, 0.4);
        }
        
        .btn-facebook:hover:before {
            left: 100%;
        }
        
        .form-control-premium {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(24, 119, 242, 0.3);
            color: white;
            border-radius: 8px;
            padding: 12px 15px;
            transition: all 0.3s;
        }
        
        .form-control-premium:focus {
            background: rgba(255, 255, 255, 0.12);
            border-color: var(--facebook-blue);
            box-shadow: 0 0 0 0.25rem rgba(24, 119, 242, 0.25);
            color: white;
        }
        
        .profile-pic {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            border: 4px solid var(--facebook-blue);
            object-fit: cover;
            margin: 0 auto 20px;
            display: block;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        
        .info-box {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid var(--facebook-blue);
        }
        
        .info-label {
            color: #aaa;
            font-size: 0.85rem;
            margin-bottom: 5px;
        }
        
        .info-value {
            color: white;
            font-weight: bold;
            font-size: 1rem;
            word-break: break-all;
        }
        
        .status-badge {
            padding: 8px 20px;
            border-radius: 50px;
            font-weight: bold;
            font-size: 1.1rem;
            display: inline-block;
            margin-bottom: 20px;
        }
        
        .status-live {
            background: linear-gradient(90deg, #28a745, #20c997);
            color: white;
        }
        
        .status-death {
            background: linear-gradient(90deg, #dc3545, #fd7e14);
            color: white;
        }
        
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            display: none;
        }
        
        .spinner-facebook {
            width: 70px;
            height: 70px;
            border: 5px solid rgba(24, 119, 242, 0.3);
            border-top: 5px solid var(--facebook-blue);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .result-card {
            background: rgba(40, 40, 40, 0.7);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .live-card {
            border-left: 5px solid #28a745;
        }
        
        .death-card {
            border-left: 5px solid #dc3545;
        }
        
        .summary-box {
            background: linear-gradient(135deg, rgba(24, 119, 242, 0.1), rgba(66, 183, 42, 0.1));
            border-radius: 15px;
            padding: 25px;
            margin-top: 30px;
            border: 1px solid rgba(24, 119, 242, 0.2);
        }
        
        .account-details-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .copy-btn {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.3s;
            margin-left: 10px;
        }
        
        .copy-btn:hover {
            background: var(--facebook-blue);
            border-color: var(--facebook-blue);
        }
        
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 8px;
            color: white;
            z-index: 10000;
            display: none;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .notification-success {
            background: linear-gradient(90deg, #28a745, #20c997);
        }
        
        .notification-error {
            background: linear-gradient(90deg, #dc3545, #fd7e14);
        }
        
        .profile-section {
            text-align: center;
            padding: 20px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .friends-count {
            background: var(--facebook-blue);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            display: inline-block;
            margin-top: 10px;
        }
        
        .account-link {
            color: var(--facebook-blue);
            text-decoration: none;
            word-break: break-all;
        }
        
        .account-link:hover {
            text-decoration: underline;
            color: #42b72a;
        }
        
        .tab-content-area {
            padding: 20px 0;
        }
        
        .mode-section {
            animation: fadeIn 0.5s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <!-- Loading Overlay -->
    <div class="loading-overlay" id="loadingOverlay">
        <div class="text-center">
            <div class="spinner-facebook"></div>
            <h4 class="mt-3" id="loadingText">Checking...</h4>
        </div>
    </div>

    <!-- Notification -->
    <div class="notification" id="notification"></div>

    <!-- Header -->
    <div class="container-fluid px-0">
        <div class="logo-header">
            <div class="container">
                <h1 class="logo-text animate__animated animate__fadeInDown">
                    <i class="fab fa-facebook-square"></i> Facebook Account Validator
                </h1>
                <p class="version animate__animated animate__fadeIn">Professional Cookie & Token Checker v3.0</p>
            </div>
        </div>
    </div>

    <div class="container">
        <!-- Mode Selection -->
        <div class="row justify-content-center mb-5 animate__animated animate__fadeInUp" id="modeSelection">
            <div class="col-lg-10">
                <div class="card card-premium">
                    <div class="card-header card-header-premium text-center">
                        <h3 class="mb-0"><i class="fas fa-cogs"></i> SELECT CHECKING MODE</h3>
                    </div>
                    <div class="card-body">
                        <div class="row text-center">
                            <div class="col-md-6 mb-4">
                                <button class="btn btn-facebook w-100 py-4" onclick="showMode('cookie')">
                                    <i class="fas fa-cookie-bite fa-3x mb-3"></i><br>
                                    <h4>Cookie Checker</h4>
                                    <p class="mb-0">Extract & Validate Facebook Cookies</p>
                                    <small>Get full account details from cookies</small>
                                </button>
                            </div>
                            <div class="col-md-6 mb-4">
                                <button class="btn btn-facebook w-100 py-4" onclick="showMode('token')">
                                    <i class="fas fa-key fa-3x mb-3"></i><br>
                                    <h4>Token Checker</h4>
                                    <p class="mb-0">Validate Facebook Access Tokens</p>
                                    <small>Check token status & account info</small>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Cookie Checker Section -->
        <div id="cookieSection" class="mode-section" style="display: none;">
            <div class="row">
                <div class="col-lg-12">
                    <div class="card card-premium">
                        <div class="card-header card-header-premium">
                            <h3 class="mb-0"><i class="fas fa-cookie-bite"></i> COOKIE CHECKER</h3>
                            <button class="btn btn-sm btn-light float-end" onclick="goBack()">
                                <i class="fas fa-arrow-left"></i> Back
                            </button>
                        </div>
                        <div class="card-body">
                            <div class="tab-content-area">
                                <div class="mb-4">
                                    <label class="form-label mb-3"><i class="fas fa-keyboard"></i> Paste Facebook Cookie:</label>
                                    <textarea class="form-control form-control-premium" id="singleCookie" rows="8" placeholder="c_user=100000000000000; xs=abc123def456ghi789; fr=0abc123def456ghi789..."></textarea>
                                    <div class="mt-3">
                                        <small class="text-muted">
                                            <i class="fas fa-info-circle"></i> Cookie should contain c_user, xs, and fr parameters
                                        </small>
                                    </div>
                                </div>
                                <div class="text-center">
                                    <button class="btn btn-facebook btn-lg px-5" onclick="checkSingleCookie()">
                                        <i class="fas fa-search"></i> CHECK COOKIE & EXTRACT INFO
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Token Checker Section -->
        <div id="tokenSection" class="mode-section" style="display: none;">
            <div class="row">
                <div class="col-lg-12">
                    <div class="card card-premium">
                        <div class="card-header card-header-premium">
                            <h3 class="mb-0"><i class="fas fa-key"></i> TOKEN CHECKER</h3>
                            <button class="btn btn-sm btn-light float-end" onclick="goBack()">
                                <i class="fas fa-arrow-left"></i> Back
                            </button>
                        </div>
                        <div class="card-body">
                            <div class="tab-content-area">
                                <div class="mb-4">
                                    <label class="form-label mb-3"><i class="fas fa-key"></i> Paste Facebook Access Token:</label>
                                    <textarea class="form-control form-control-premium" id="singleToken" rows="8" placeholder="EAAG... (Facebook Access Token)"></textarea>
                                    <div class="mt-3">
                                        <small class="text-warning">
                                            <i class="fas fa-exclamation-triangle"></i> Tokens are sensitive. Ensure secure environment.
                                        </small>
                                    </div>
                                </div>
                                <div class="text-center">
                                    <button class="btn btn-facebook btn-lg px-5" onclick="checkSingleToken()">
                                        <i class="fas fa-search"></i> CHECK TOKEN & ACCOUNT INFO
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Results Section -->
        <div id="resultsSection" style="display: none;">
            <div class="row">
                <div class="col-lg-12">
                    <div class="card card-premium">
                        <div class="card-header card-header-premium">
                            <h3 class="mb-0"><i class="fas fa-chart-line"></i> VALIDATION RESULTS</h3>
                            <button class="btn btn-sm btn-light float-end" onclick="goBack()">
                                <i class="fas fa-arrow-left"></i> Back
                            </button>
                        </div>
                        <div class="card-body">
                            <div id="resultsContainer"></div>
                            <div id="summaryContainer"></div>
                            <div class="text-center mt-4" id="actionButtons"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="mt-5 py-4" style="background: rgba(0,0,0,0.5); border-top: 1px solid rgba(255,255,255,0.1);">
        <div class="container text-center">
            <p class="mb-2"><i class="fas fa-code"></i> Facebook Account Validator v3.0</p>
            <small class="text-muted">
                <i class="fas fa-shield-alt"></i> Secure Processing
            </small>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let currentMode = '';
        let liveContent = '';
        let contentType = '';

        function showNotification(message, type = 'success') {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.className = 'notification notification-' + type;
            notification.style.display = 'block';
            
            setTimeout(() => {
                notification.style.display = 'none';
            }, 3000);
        }

        function showLoading(text) {
            document.getElementById('loadingText').textContent = text;
            document.getElementById('loadingOverlay').style.display = 'flex';
        }

        function hideLoading() {
            document.getElementById('loadingOverlay').style.display = 'none';
        }

        function showMode(mode) {
            // Hide mode selection
            document.getElementById('modeSelection').style.display = 'none';
            
            // Hide all mode sections
            document.getElementById('cookieSection').style.display = 'none';
            document.getElementById('tokenSection').style.display = 'none';
            document.getElementById('resultsSection').style.display = 'none';
            
            // Show selected mode
            if (mode === 'cookie') {
                document.getElementById('cookieSection').style.display = 'block';
                currentMode = 'cookie';
            } else if (mode === 'token') {
                document.getElementById('tokenSection').style.display = 'block';
                currentMode = 'token';
            }
        }

        function goBack() {
            // Show mode selection
            document.getElementById('modeSelection').style.display = 'block';
            
            // Hide all other sections
            document.getElementById('cookieSection').style.display = 'none';
            document.getElementById('tokenSection').style.display = 'none';
            document.getElementById('resultsSection').style.display = 'none';
            
            // Clear inputs
            document.getElementById('singleCookie').value = '';
            document.getElementById('singleToken').value = '';
            
            currentMode = '';
            liveContent = '';
            contentType = '';
        }

        async function checkSingleCookie() {
            const cookie = document.getElementById('singleCookie').value.trim();
            if (!cookie) {
                showNotification('Please enter a cookie to check!', 'error');
                return;
            }

            showLoading('Extracting account information...');
            
            try {
                const response = await fetch('/check_single_cookie', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: 'cookie=' + encodeURIComponent(cookie)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displaySingleResult(data.result, 'cookie');
                    showNotification('Cookie checked successfully!', 'success');
                } else {
                    showNotification('Error: ' + data.error, 'error');
                }
            } catch (error) {
                showNotification('Network error: ' + error.message, 'error');
            } finally {
                hideLoading();
            }
        }

        async function checkSingleToken() {
            const token = document.getElementById('singleToken').value.trim();
            if (!token) {
                showNotification('Please enter a token to check!', 'error');
                return;
            }

            showLoading('Fetching account details...');
            
            try {
                const response = await fetch('/check_single_token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: 'token=' + encodeURIComponent(token)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displaySingleResult(data.result, 'token');
                    showNotification('Token checked successfully!', 'success');
                } else {
                    showNotification('Error: ' + data.error, 'error');
                }
            } catch (error) {
                showNotification('Network error: ' + error.message, 'error');
            } finally {
                hideLoading();
            }
        }

        function displaySingleResult(result, type) {
            // Hide current mode section, show results
            document.getElementById('cookieSection').style.display = 'none';
            document.getElementById('tokenSection').style.display = 'none';
            document.getElementById('resultsSection').style.display = 'block';
            
            const isLive = result.status === 'live';
            const statusClass = isLive ? 'status-live' : 'status-death';
            const statusText = isLive ? '✅ ACCOUNT VALID' : '❌ ACCOUNT INVALID';
            
            // Generate profile picture URL
            let profilePicUrl = 'https://cdn-icons-png.flaticon.com/512/149/149071.png';
            if (isLive && result.user_id) {
                if (result.profile_pic && result.profile_pic !== 'N/A') {
                    profilePicUrl = result.profile_pic;
                } else if (result.token) {
                    profilePicUrl = 'https://graph.facebook.com/' + result.user_id + '/picture?type=large';
                }
            }
            
            let detailsHtml = '';
            if (isLive) {
                detailsHtml = `
                    <div class="profile-section">
                        <img src="${profilePicUrl}" class="profile-pic animate__animated animate__zoomIn" 
                             onerror="this.src='https://cdn-icons-png.flaticon.com/512/149/149071.png'">
                        ${result.friends_count && result.friends_count !== 'N/A' ? 
                            `<div class="friends-count animate__animated animate__fadeIn">
                                <i class="fas fa-users"></i> ${result.friends_count} Friends
                            </div>` : ''}
                    </div>
                    
                    <div class="account-details-grid">
                        <div class="info-box">
                            <div class="info-label"><i class="fas fa-user"></i> Full Name</div>
                            <div class="info-value">${result.name || 'N/A'}</div>
                        </div>
                        
                        <div class="info-box">
                            <div class="info-label"><i class="fas fa-id-card"></i> User ID</div>
                            <div class="info-value">
                                ${result.user_id || 'N/A'}
                                <button class="copy-btn" onclick="copyToClipboard('${result.user_id || ''}')">Copy</button>
                            </div>
                        </div>
                        
                        <div class="info-box">
                            <div class="info-label"><i class="fas fa-at"></i> Username</div>
                            <div class="info-value">
                                ${result.username || 'N/A'}
                                ${result.username && result.username !== 'N/A' ? 
                                    `<button class="copy-btn" onclick="copyToClipboard('${result.username}')">Copy</button>` : ''}
                            </div>
                        </div>
                        
                        <div class="info-box">
                            <div class="info-label"><i class="fas fa-envelope"></i> Email</div>
                            <div class="info-value">
                                ${result.email || 'N/A'}
                                ${result.email && result.email !== 'N/A' ? 
                                    `<button class="copy-btn" onclick="copyToClipboard('${result.email}')">Copy</button>` : ''}
                            </div>
                        </div>
                        
                        <div class="info-box">
                            <div class="info-label"><i class="fas fa-phone"></i> Phone Number</div>
                            <div class="info-value">
                                ${result.phone || 'N/A'}
                                ${result.phone && result.phone !== 'N/A' ? 
                                    `<button class="copy-btn" onclick="copyToClipboard('${result.phone}')">Copy</button>` : ''}
                            </div>
                        </div>
                        
                        <div class="info-box">
                            <div class="info-label"><i class="fas fa-link"></i> Profile Link</div>
                            <div class="info-value">
                                ${result.profile_link && result.profile_link !== 'N/A' ? 
                                    `<a href="${result.profile_link}" target="_blank" class="account-link">
                                        ${result.profile_link}
                                    </a>
                                    <button class="copy-btn" onclick="copyToClipboard('${result.profile_link}')">Copy</button>` : 
                                    'N/A'}
                            </div>
                        </div>
                        
                        <div class="info-box">
                            <div class="info-label"><i class="fas fa-birthday-cake"></i> Birth Date</div>
                            <div class="info-value">${result.birthday || 'N/A'}</div>
                        </div>
                        
                        <div class="info-box">
                            <div class="info-label"><i class="fas fa-venus-mars"></i> Gender</div>
                            <div class="info-value">${result.gender || 'N/A'}</div>
                        </div>
                        
                        <div class="info-box">
                            <div class="info-label"><i class="fas fa-map-marker-alt"></i> Location</div>
                            <div class="info-value">${result.location || 'N/A'}</div>
                        </div>
                    </div>
                `;
            }
            
            document.getElementById('resultsContainer').innerHTML = `
                <div class="text-center mb-4">
                    <div class="status-badge ${statusClass} animate__animated animate__pulse">
                        ${statusText}
                    </div>
                </div>
                
                <div class="result-card ${isLive ? 'live-card' : 'death-card'}">
                    <h5 class="mb-3"><i class="fas fa-info-circle"></i> ${type.toUpperCase()} VALIDATION RESULT</h5>
                    <p><strong>Status:</strong> ${result.status || 'Unknown'}</p>
                    <p><strong>Message:</strong> ${result.message || 'No message'}</p>
                    ${!isLive ? `<p class="text-danger"><i class="fas fa-exclamation-triangle"></i> ${result.message || 'Invalid or expired'}</p>` : ''}
                </div>
                
                ${detailsHtml}
            `;
            
            const total = 1;
            const live = isLive ? 1 : 0;
            const death = total - live;
            
            document.getElementById('summaryContainer').innerHTML = `
                <div class="summary-box">
                    <h4 class="mb-4"><i class="fas fa-chart-pie"></i> SUMMARY</h4>
                    <div class="row text-center">
                        <div class="col-md-3 mb-3">
                            <h2 class="display-6">${total}</h2>
                            <p class="text-muted">Total Checked</p>
                        </div>
                        <div class="col-md-3 mb-3">
                            <h2 class="display-6 text-success">${live}</h2>
                            <p class="text-muted">✅ Valid</p>
                        </div>
                        <div class="col-md-3 mb-3">
                            <h2 class="display-6 text-danger">${death}</h2>
                            <p class="text-muted">❌ Invalid</p>
                        </div>
                        <div class="col-md-3 mb-3">
                            <h2 class="display-6 ${isLive ? 'text-success' : 'text-danger'}">${isLive ? '100%' : '0%'}</h2>
                            <p class="text-muted">Success Rate</p>
                        </div>
                    </div>
                </div>
            `;
            
            document.getElementById('actionButtons').innerHTML = isLive ? `
                <button class="btn btn-facebook me-3" onclick="exportResults()">
                    <i class="fas fa-download"></i> EXPORT RESULTS
                </button>
                <button class="btn btn-success" onclick="checkAnother()">
                    <i class="fas fa-redo"></i> CHECK ANOTHER
                </button>
            ` : `
                <button class="btn btn-facebook" onclick="checkAnother()">
                    <i class="fas fa-redo"></i> TRY AGAIN
                </button>
            `;
        }

        function checkAnother() {
            goBack();
            if (currentMode === 'cookie') {
                showMode('cookie');
            } else if (currentMode === 'token') {
                showMode('token');
            }
        }

        function exportResults() {
            showNotification('Export feature coming soon!', 'info');
        }

        function copyToClipboard(text) {
            if (!text || text === 'N/A') return;
            
            navigator.clipboard.writeText(text).then(() => {
                showNotification('Copied to clipboard!', 'success');
            }).catch(() => {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                showNotification('Copied to clipboard!', 'success');
            });
        }
    </script>
</body>
</html>
'''

# -------- Profile Name Cache --------
cookie_name_cache = {}

def parse_cookie_string(cookie_str):
    cookies = {}
    for part in cookie_str.split(";"):
        if "=" in part:
            k, v = part.strip().split("=", 1)
            cookies[k] = v
    return cookies

def GetNew(ua=None):
    if ua is None:
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    return {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': ua
    }

def extract_name(cookie_string, ua=None):
    try:
        cookies = parse_cookie_string(cookie_string)
        user_id = cookies.get("c_user")
        if not user_id:
            return "❌ No c_user", None

        url = f"https://www.facebook.com/profile.php?id={user_id}"
        resp = requests.get(url, cookies=cookies, headers=GetNew(ua), timeout=15)
        html = resp.text

        # Try to extract more detailed account info
        profile_match = re.search(r'"CurrentUserInitialData",\[\],\{(.*?)\},', html)
        
        if profile_match:
            try:
                account_json = json.loads("{" + profile_match.group(1) + "}")
                name = account_json.get("NAME", "Unknown")
                return name, user_id
            except:
                pass

        # Alternative extraction methods
        name_match = re.search(r'<title>([^<]+)</title>', html)
        if name_match:
            name = name_match.group(1).replace(' | Facebook', '').strip()
            if name and name != 'Facebook':
                return name, user_id
        
        # Try to extract from JSON-LD
        json_ld_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
        if json_ld_match:
            try:
                data = json.loads(json_ld_match.group(1))
                name = data.get('name', 'Unknown')
                if name and name != 'Facebook':
                    return name, user_id
            except:
                pass
        
        return "❌ Expired", None
    except Exception as e:
        return f"⚠️ Error: {str(e)}", None

def extract_token_from_cookie(cookie_string):
    try:
        response = requests.get(
            'https://business.facebook.com/business_locations',
            headers={
                'Cookie': cookie_string,
                'User-Agent': 'Mozilla/5.0 (Linux; Android 11; RMX2144 Build/RKQ1.201217.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/103.0.5060.71 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/375.1.0.28.111;]',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            },
            timeout=15
        )
        
        token_match = re.search(r'(EAAG\w+|EAA\w+)', response.text)
        if token_match:
            return token_match.group(1)
        return None
    except:
        return None

def get_facebook_account_details(access_token, user_id=None):
    """Get detailed Facebook account information using Graph API"""
    try:
        base_url = "https://graph.facebook.com/v18.0/"
        
        # Get basic info
        if not user_id:
            me_url = f"{base_url}me?access_token={access_token}&fields=id,name,email,birthday,gender,location,locale,link,first_name,last_name,middle_name"
            response = requests.get(me_url, timeout=10)
            
            if response.status_code == 200:
                user_info = response.json()
                user_id = user_info.get('id')
            else:
                return None
        else:
            user_url = f"{base_url}{user_id}?access_token={access_token}&fields=id,name,email,birthday,gender,location,locale,link,first_name,last_name,middle_name"
            response = requests.get(user_url, timeout=10)
            user_info = response.json() if response.status_code == 200 else {}
        
        # Get friends count
        friends_count = "N/A"
        try:
            friends_url = f"{base_url}{user_id}/friends?access_token={access_token}&limit=1&summary=total_count"
            friends_response = requests.get(friends_url, timeout=10)
            
            if friends_response.status_code == 200:
                friends_data = friends_response.json()
                summary = friends_data.get('summary', {})
                friends_count = summary.get('total_count', 'N/A')
        except:
            pass
        
        # Get profile picture
        profile_pic = None
        try:
            picture_url = f"{base_url}{user_id}/picture?access_token={access_token}&type=large&redirect=false"
            picture_response = requests.get(picture_url, timeout=10)
            
            if picture_response.status_code == 200:
                picture_data = picture_response.json()
                if picture_data.get('data', {}).get('url'):
                    profile_pic = picture_data['data']['url']
        except:
            pass
        
        # Get username from profile link
        username = "N/A"
        profile_link = user_info.get('link', '')
        if profile_link:
            parsed = urlparse(profile_link)
            if parsed.path and parsed.path != '/':
                username = parsed.path.strip('/')
        
        # Compile all account details
        account_details = {
            'user_id': user_id,
            'name': user_info.get('name', 'N/A'),
            'email': user_info.get('email', 'N/A'),
            'phone': user_info.get('phone', 'N/A'),
            'birthday': user_info.get('birthday', 'N/A'),
            'gender': user_info.get('gender', 'N/A'),
            'location': user_info.get('location', {}).get('name', 'N/A') if isinstance(user_info.get('location'), dict) else user_info.get('location', 'N/A'),
            'locale': user_info.get('locale', 'N/A'),
            'profile_link': profile_link,
            'username': username,
            'profile_pic': profile_pic,
            'friends_count': friends_count,
            'first_name': user_info.get('first_name', 'N/A'),
            'last_name': user_info.get('last_name', 'N/A'),
            'middle_name': user_info.get('middle_name', 'N/A')
        }
        
        return account_details
        
    except Exception as e:
        print(f"Error getting account details: {e}")
        return None

def check_cookie(cookie_string):
    try:
        cookies = parse_cookie_string(cookie_string)
        user_id = cookies.get("c_user")
        
        if not user_id:
            return {
                "status": "death",
                "user_id": None,
                "name": None,
                "token": None,
                "message": "Invalid cookie format - No c_user found"
            }

        token = extract_token_from_cookie(cookie_string)
        
        if token:
            account_details = get_facebook_account_details(token, user_id)
            
            if account_details:
                name = account_details.get('name')
                if not name or name == 'N/A':
                    # Fallback to profile extraction
                    extracted_name, extracted_uid = extract_name(cookie_string)
                    if extracted_name not in ["❌ Expired", "⚠️ Error", "⚠️ ParseError", "❌ No c_user", "Unknown"]:
                        name = extracted_name
                        if extracted_uid:
                            user_id = extracted_uid
                
                result = {
                    "status": "live",
                    "user_id": user_id,
                    "name": name or account_details.get('name', 'Unknown'),
                    "token": token,
                    "message": "Cookie is valid and account details extracted",
                }
                
                # Add account details
                result.update(account_details)
                
                # Try to extract additional info from HTML
                try:
                    url = f"https://www.facebook.com/profile.php?id={user_id}"
                    resp = requests.get(url, cookies=cookies, headers=GetNew(), timeout=10)
                    html = resp.text
                    
                    # Try to extract email from page
                    email_match = re.search(r'["\']email["\']\s*:\s*["\']([^"\']+)["\']', html)
                    if email_match and (not result.get('email') or result.get('email') == 'N/A'):
                        result['email'] = email_match.group(1)
                    
                    # Try to extract phone
                    phone_match = re.search(r'["\']phone["\']\s*:\s*["\']([^"\']+)["\']', html)
                    if phone_match and (not result.get('phone') or result.get('phone') == 'N/A'):
                        result['phone'] = phone_match.group(1)
                        
                except:
                    pass
                
                return result
            else:
                # Graph API failed, try HTML extraction
                extracted_name, extracted_uid = extract_name(cookie_string)
                if extracted_name not in ["❌ Expired", "⚠️ Error", "⚠️ ParseError", "❌ No c_user", "Unknown"]:
                    return {
                        "status": "live",
                        "user_id": extracted_uid or user_id,
                        "name": extracted_name,
                        "token": token,
                        "message": "Cookie is valid but limited info available",
                        "email": "N/A",
                        "phone": "N/A",
                        "birthday": "N/A",
                        "gender": "N/A",
                        "location": "N/A",
                        "profile_link": f"https://facebook.com/profile.php?id={extracted_uid or user_id}",
                        "username": "N/A",
                        "friends_count": "N/A"
                    }
                else:
                    return {
                        "status": "death",
                        "user_id": None,
                        "name": None,
                        "token": None,
                        "message": "Cookie appears expired"
                    }
        else:
            # Token extraction failed - cookie is DEATH
            return {
                "status": "death",
                "user_id": None,
                "name": None,
                "token": None,
                "message": "Cookie expired or invalid"
            }
            
    except Exception as e:
        return {
            "status": "death",
            "user_id": None,
            "name": None,
            "token": None,
            "message": f"Error: {str(e)}"
        }

def validate_token(access_token):
    try:
        # First check if token is valid
        url = f"https://graph.facebook.com/me?access_token={access_token}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            user_info = response.json()
            user_id = user_info.get('id')
            name = user_info.get('name', 'Unknown')
            
            # Get detailed account info
            account_details = get_facebook_account_details(access_token, user_id)
            
            result = {
                "status": "live",
                "name": name,
                "user_id": user_id,
                "token": access_token,
                "message": "Token is valid and account details extracted"
            }
            
            if account_details:
                result.update(account_details)
            else:
                # Add default values if account details failed
                result.update({
                    "email": "N/A",
                    "phone": "N/A",
                    "birthday": "N/A",
                    "gender": "N/A",
                    "location": "N/A",
                    "profile_link": f"https://facebook.com/{user_id}",
                    "username": "N/A",
                    "friends_count": "N/A"
                })
            
            return result
        else:
            return {
                "status": "death",
                "name": None,
                "user_id": None,
                "token": None,
                "message": "Token expired or invalid"
            }
    except requests.exceptions.RequestException:
        return {
            "status": "death",
            "name": None,
            "user_id": None,
            "token": None,
            "message": "Network error"
        }

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/check_single_cookie', methods=['POST'])
def check_single_cookie_route():
    try:
        cookie = request.form.get('cookie', '').strip()
        if not cookie:
            return jsonify({'error': 'No cookie provided'}), 400
        
        result = check_cookie(cookie)
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/check_single_token', methods=['POST'])
def check_single_token_route():
    try:
        token = request.form.get('token', '').strip()
        if not token:
            return jsonify({'error': 'No token provided'}), 400
        
        result = validate_token(token)
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Facebook Account Validator v3.0...")
    print("🌐 Server running at: http://localhost:5000")
    print("📱 Access from any device on your network")
    print("⚡ Features: Cookie Checker | Token Checker | Full Account Details")
    print("🔒 Secure & Professional | All data processed locally")
    print("\n✅ HOW TO USE:")
    print("1. Open browser: http://localhost:5000")
    print("2. Select 'Cookie Checker' or 'Token Checker'")
    print("3. Paste your cookie or token")
    print("4. Click 'Check' button")
    print("5. View full account details including profile picture!")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
