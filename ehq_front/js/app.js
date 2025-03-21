// English High Q 前端应用脚本

// API基础URL
const API_BASE_URL = 'http://localhost:8000/api';

// 页面元素
const pages = document.querySelectorAll('.page');
const navLinks = document.querySelectorAll('[data-page]');
const guestNav = document.getElementById('guest-nav');
const userNav = document.getElementById('user-nav');
const userBalanceElements = document.querySelectorAll('#user-balance');

// 表单元素
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const rechargeForm = document.getElementById('recharge-form');
const questionForm = document.getElementById('question-form');

// 错误提示元素
const loginError = document.getElementById('login-error');
const registerError = document.getElementById('register-error');
const rechargeError = document.getElementById('recharge-error');
const rechargeSuccess = document.getElementById('recharge-success');
const questionError = document.getElementById('question-error');

// 个人信息元素
const profileUsername = document.getElementById('profile-username');
const profileEmail = document.getElementById('profile-email');
const profileBalance = document.getElementById('profile-balance');

// 答案卡片元素
const answerCard = document.getElementById('answer-card');
const answerQuestion = document.getElementById('answer-question');
const answerContent = document.getElementById('answer-content');
const answerCost = document.getElementById('answer-cost');

// 历史记录元素
const historyList = document.getElementById('history-list');
const historyEmpty = document.getElementById('history-empty');

// 初始化应用
function initApp() {
    // 检查用户是否已登录
    checkAuthStatus();
    
    // 设置页面导航事件
    setupNavigation();
    
    // 设置表单提交事件
    setupForms();
    
    // 设置退出登录事件
    document.getElementById('logout-btn').addEventListener('click', logout);
}

// 检查用户认证状态
async function checkAuthStatus() {
    const token = localStorage.getItem('token');
    
    if (!token) {
        showGuestNav();
        navigateTo('home');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/users/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const userData = await response.json();
            showUserNav(userData);
            updateUserInfo(userData);
        } else {
            // Token无效或过期
            localStorage.removeItem('token');
            showGuestNav();
            navigateTo('home');
        }
    } catch (error) {
        console.error('认证检查失败:', error);
        showGuestNav();
    }
}

// 设置页面导航
function setupNavigation() {
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetPage = link.getAttribute('data-page');
            
            // 检查是否需要登录才能访问
            const requiresAuth = ['profile', 'question', 'history'].includes(targetPage);
            
            if (requiresAuth && !isLoggedIn()) {
                showError(loginError, '请先登录后再访问此页面');
                navigateTo('login');
                return;
            }
            
            navigateTo(targetPage);
            
            // 如果是历史记录页面，加载历史数据
            if (targetPage === 'history' && isLoggedIn()) {
                loadQuestionHistory();
            }
        });
    });
}

// 导航到指定页面
function navigateTo(pageId) {
    pages.forEach(page => {
        page.classList.add('d-none');
    });
    
    const targetPage = document.getElementById(`${pageId}-page`);
    if (targetPage) {
        targetPage.classList.remove('d-none');
    }
}

// 设置表单提交事件
function setupForms() {
    // 登录表单
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await login();
        });
    }
    
    // 注册表单
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await register();
        });
    }
    
    // 充值表单
    if (rechargeForm) {
        rechargeForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await recharge();
        });
    }
    
    // 提问表单
    if (questionForm) {
        questionForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await askQuestion();
        });
    }
}

// 用户登录
async function login() {
    hideError(loginError);
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/users/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                'username': username,
                'password': password
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            
            // 获取用户信息
            await getUserInfo();
            
            // 导航到首页
            navigateTo('home');
        } else {
            const errorData = await response.json();
            showError(loginError, errorData.detail || '登录失败，请检查用户名和密码');
        }
    } catch (error) {
        console.error('登录失败:', error);
        showError(loginError, '登录请求失败，请稍后再试');
    }
}

// 用户注册
async function register() {
    hideError(registerError);
    
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;
    
    // 验证密码一致性
    if (password !== confirmPassword) {
        showError(registerError, '两次输入的密码不一致');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/users/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username,
                email,
                password
            })
        });
        
        if (response.ok) {
            // 注册成功，自动登录
            const loginResponse = await fetch(`${API_BASE_URL}/users/token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams({
                    'username': username,
                    'password': password
                })
            });
            
            if (loginResponse.ok) {
                const data = await loginResponse.json();
                localStorage.setItem('token', data.access_token);
                
                // 获取用户信息
                await getUserInfo();
                
                // 导航到首页
                navigateTo('home');
            } else {
                // 注册成功但登录失败，导航到登录页
                navigateTo('login');
                showError(loginError, '注册成功，请登录');
            }
        } else {
            const errorData = await response.json();
            showError(registerError, errorData.detail || '注册失败');
        }
    } catch (error) {
        console.error('注册失败:', error);
        showError(registerError, '注册请求失败，请稍后再试');
    }
}

// 获取用户信息
async function getUserInfo() {
    const token = localStorage.getItem('token');
    
    if (!token) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/users/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const userData = await response.json();
            showUserNav(userData);
            updateUserInfo(userData);
        } else {
            // Token无效或过期
            localStorage.removeItem('token');
            showGuestNav();
        }
    } catch (error) {
        console.error('获取用户信息失败:', error);
    }
}

// 用户充值
async function recharge() {
    hideError(rechargeError);
    hideSuccess(rechargeSuccess);
    
    const amount = parseFloat(document.getElementById('recharge-amount').value);
    const description = document.getElementById('recharge-description').value;
    
    if (amount < 1) {
        showError(rechargeError, '充值金额不能小于1元');
        return;
    }
    
    const token = localStorage.getItem('token');
    
    if (!token) {
        showError(rechargeError, '请先登录');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/users/recharge`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                amount,
                description: description || undefined
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            showSuccess(rechargeSuccess, `充值成功！当前余额: ${data.balance.toFixed(2)} 元`);
            
            // 更新用户余额显示
            updateBalance(data.balance);
            
            // 清空表单
            document.getElementById('recharge-amount').value = '';
            document.getElementById('recharge-description').value = '';
        } else {
            const errorData = await response.json();
            showError(rechargeError, errorData.detail || '充值失败');
        }
    } catch (error) {
        console.error('充值失败:', error);
        showError(rechargeError, '充值请求失败，请稍后再试');
    }
}

// 提交英语题目
async function askQuestion() {
    hideError(questionError);
    
    // 隐藏之前的答案卡片
    answerCard.classList.add('d-none');
    
    const question = document.getElementById('question-content').value.trim();
    
    if (!question) {
        showError(questionError, '请输入英语题目');
        return;
    }
    
    const token = localStorage.getItem('token');
    
    if (!token) {
        showError(questionError, '请先登录');
        return;
    }
    
    // 显示加载状态
    const submitBtn = questionForm.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 处理中...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/questions/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                question
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // 显示答案
            answerQuestion.textContent = data.question;
            answerContent.textContent = data.answer;
            answerCost.textContent = `消费: ${data.cost.toFixed(2)} 元`;
            answerCard.classList.remove('d-none');
            
            // 更新用户余额
            await getUserInfo();
            
            // 清空输入框
            document.getElementById('question-content').value = '';
        } else {
            const errorData = await response.json();
            showError(questionError, errorData.detail || '提交题目失败');
        }
    } catch (error) {
        console.error('提交题目失败:', error);
        showError(questionError, '提交请求失败，请稍后再试');
    } finally {
        // 恢复按钮状态
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
    }
}

// 加载问题历史记录
async function loadQuestionHistory() {
    const token = localStorage.getItem('token');
    
    if (!token) {
        return;
    }
    
    // 清空历史记录列表
    historyList.innerHTML = '';
    
    // 显示加载状态
    const loadingSpinner = document.createElement('div');
    loadingSpinner.className = 'spinner-container';
    loadingSpinner.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">加载中...</span></div>';
    historyList.appendChild(loadingSpinner);
    
    try {
        const response = await fetch(`${API_BASE_URL}/questions/history`, {