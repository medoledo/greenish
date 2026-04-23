
        const SESSION_CODE = '{{ session.code }}';
        const TOTAL_SLIDES = {{ total_slides }};
        const CURRENT_INDEX = {{ current_index }};
        const CSRF_TOKEN = '{{ csrf_token }}';
        const IS_ACTIVITY_ACTIVE = {{ session.activity_active|lower }};
        const CURRENT_SLIDE_DATA = {% if current_slide %}{
            id: {{ current_slide.id }},
            title: '{{ current_slide.title|escapejs }}',
            content: '{{ current_slide.content|escapejs }}',
            slide_type: '{{ current_slide.slide_type }}',
            activity_type: '{{ current_slide.activity_type|default_if_none:"" }}',
            activity_config: {% if current_slide.activity_config %}{{ current_slide.activity_config|safe }}{% else %}null{% endif %},
            shocking_fact: {{ current_slide.shocking_fact|lower }},
            image_url: {% if current_slide.image %}'{{ current_slide.image.url }}'{% else %}null{% endif %},
        }{% else %}null{% endif %};

        let eventSource = null;
        let leaderboardVisible = false;
        let activityActive = IS_ACTIVITY_ACTIVE;
        let currentSlideIndex = CURRENT_INDEX;
        let currentSlideData = CURRENT_SLIDE_DATA;
        let isLoading = false;

        // Activity templates
        const ACTIVITIES = {
            sprint: {
                title: '♻️ Sort the Waste!',
                items: [
                    { name: 'Orange Peel', bin: 'compose', emoji: '🍊' },
                    { name: 'Plastic Bag', bin: 'landfill', emoji: '🛍️' },
                    { name: 'Glass Bottle', bin: 'recycle', emoji: '🍶' },
                    { name: 'Newspaper', bin: 'recycle', emoji: '📰' },
                    { name: 'Banana Peel', bin: 'compose', emoji: '🍌' },
                    { name: 'Aluminum Can', bin: 'recycle', emoji: '🥫' },
                ],
                bins: [
                    { id: 'recycle', name: '♻️ Recycle', color: '#52B788' },
                    { id: 'compose', name: '🌱 Compost', color: '#95D5B2' },
                    { id: 'landfill', name: '🗑️ Landfill', color: '#E76F51' },
                ]
            },
            decompose: {
                title: '⏳ How Long Does It Take?',
                items: [
                    { name: 'Banana Peel', time: '2-5 weeks', slot: 0, emoji: '🍌' },
                    { name: 'Newspaper', time: '6 weeks', slot: 1, emoji: '📰' },
                    { name: 'Cigarette Butt', time: '10 years', slot: 2, emoji: '🚬' },
                    { name: 'Plastic Bag', time: '500 years', slot: 3, emoji: '🛍️' },
                    { name: 'Glass Bottle', time: '1M+ years', slot: 4, emoji: '🍶' },
                ],
                timeline: ['~1 Month', '~2 Months', '~10 Years', '~500 Years', '~1M Years']
            },
            quiz: {
                title: '🌍 Plastic vs Planet',
                questions: [
                    { q: 'How many plastic bags are used worldwide every minute?', options: ['10,000', '100,000', '1 million', '10 million'], correct: 2 },
                    { q: 'What percentage of plastic is actually recycled globally?', options: ['9%', '25%', '50%', '75%'], correct: 0 },
                    { q: 'How long does a plastic bottle take to decompose?', options: ['10 years', '75 years', '450 years', '1,000 years'], correct: 2 },
                    { q: 'Egypt generates approximately how many tons of waste per year?', options: ['5 million', '26 million', '50 million', '100 million'], correct: 1 },
                    { q: 'What percentage of Egypt\'s waste is food/organic waste?', options: ['10%', '25%', '50%', '75%'], correct: 2 },
                    { q: 'Which ocean has the largest garbage patch?', options: ['Atlantic', 'Indian', 'Pacific', 'Arctic'], correct: 2 },
                    { q: 'How many marine animals are killed by plastic each year?', options: ['100K', '1 million', '10 million', '100 million'], correct: 1 },
                    { q: 'A single plastic bag is used for an average of...', options: ['5 minutes', '30 minutes', '12 hours', '1 day'], correct: 2 },
                    { q: 'What is the most common item found in beach cleanups?', options: ['Straws', 'Bottles', 'Cigarette butts', 'Bags'], correct: 2 },
                    { q: 'Recycling 1 aluminum can saves enough energy to...', options: ['Run a TV for 1 hour', 'Power a light bulb for 20 hours', 'Run a computer for 3 hours', 'Charge a phone twice'], correct: 1 },
                ]
            },
            commitment: {
                title: '💚 Make Your Green Commitment!',
                prompt: 'I will...',
                placeholder: 'Share your environmental commitment...'
            },
            sort_stats: {
                title: '📊 True or False?',
                statements: [
                    { text: 'Egypt generates about 26 million tons of waste per year', answer: true },
                    { text: '50% of waste in Egypt is food/organic waste', answer: true },
                    { text: 'Plastic makes up 80% of Egypt\'s waste by volume', answer: false, fact: 'Plastic is about 12-15% by volume' },
                    { text: 'Recycling rate in Egypt is about 12%', answer: true },
                    { text: 'A plastic bag takes 500 years to decompose', answer: true },
                    { text: 'Egypt has one of the highest waste generation rates in Africa', answer: false, fact: 'Egypt\'s rate is moderate for the region' },
                    { text: 'Only 9% of all plastic ever made has been recycled', answer: true },
                    { text: 'Burning waste in open air is common in Egypt', answer: true },
                ]
            }
        };

        // Floating particles
        (function(){
            const c = document.getElementById('facilitator-particles');
            if (!c) return;
            const emojis = ['🌿','','🌱','','💚','','🌸','','🌍',''];
            for (let i = 0; i < 20; i++) {
                const s = document.createElement('span');
                s.textContent = emojis[Math.floor(Math.random() * emojis.length)];
                s.style.left = Math.random() * 100 + '%';
                s.style.top = Math.random() * 100 + '%';
                s.style.animationDelay = (Math.random() * 12) + 's';
                s.style.animationDuration = (10 + Math.random() * 8) + 's';
                s.style.fontSize = (24 + Math.random() * 16) + 'px';
                c.appendChild(s);
            }
        })();

        // SSE — named events
        function connectSSE() {
            eventSource = new EventSource('/session/' + SESSION_CODE + '/stream/');
            eventSource.addEventListener('slide_change', function(event) {
                const data = JSON.parse(event.data);
                currentSlideIndex = data.slide_index;
                currentSlideData = data.slide;
                updateSlideDisplay(data.slide_index, data.total_slides, data.slide);
            });
            eventSource.addEventListener('activity_toggle', function(event) {
                const data = JSON.parse(event.data);
                activityActive = data.activity_active;
                updateActivityBadge();
                if (activityActive && currentSlideData && currentSlideData.slide_type === 'activity') {
                    renderFacilitatorActivity(currentSlideData.activity_type, currentSlideData.activity_config);
                } else {
                    hideFacilitatorActivity();
                }
            });
            eventSource.addEventListener('session_status', function(event) {
                const data = JSON.parse(event.data);
                if (data.status === 'ended') {
                    window.location.href = '/session/';
                }
            });
            eventSource.addEventListener('activity_result', function(event) {
                if (activityActive && currentSlideData && currentSlideData.slide_type === 'activity') {
                    refreshLiveStats();
                }
            });
            eventSource.onerror = function() {
                setTimeout(connectSSE, 3000);
            };
        }

        function updateSlideDisplay(index, total, slide) {
            // Update counter
            document.getElementById('current-index').textContent = index + 1;
            document.getElementById('total-slides').textContent = total;

            // Update progress dots
            document.querySelectorAll('#progress-dots .dot').forEach((dot, i) => {
                dot.classList.remove('active');
                if (i === index) dot.classList.add('active');
            });

            // Update slide content
            const display = document.getElementById('slide-display');
            if (!slide) {
                display.innerHTML = '<div class="slide-empty"><div class="empty-icon">🌿</div><h2>Session Ready</h2><p>Use the controls below to start presenting</p></div>';
                return;
            }

            let imgHTML = slide.image_url ? '<img src="' + slide.image_url + '" alt="" class="slide-image">' : '';
            let titleHTML = slide.title ? '<h2 class="slide-title' + (slide.shocking_fact ? ' shocking-text' : '') + '">' + slide.title + '</h2>' : '';
            let bodyHTML = '<div class="slide-body" id="slide-body">' + slide.content.replace(/\n/g, '<br>') + '</div>';

            let activityBadgeHTML = '';
            let activityPanelHTML = '';
            if (slide.slide_type === 'activity' && slide.activity_type) {
                const icons = {sprint:'♻️',decompose:'⏳',quiz:'🌍',commitment:'💚',sort_stats:'📊',poll:'📊',sort:'♻️',guess:'⏳',discuss:'💬',commit:'💪',match:'🧩',problem:'🔍',case_study:'📋'};
                const icon = icons[slide.activity_type] || '🎯';
                activityBadgeHTML = '<div class="activity-badge" id="activity-badge" style="' + (activityActive ? '' : 'display:none;') + '"><span class="activity-icon" id="activity-icon">' + icon + '</span>Activity: ' + slide.activity_type + '</div>';
                activityPanelHTML = '<div class="fac-activity-panel" id="fac-activity-panel" style="' + (activityActive ? '' : 'display:none;') + '"><h3 class="activity-title" id="fac-activity-title"></h3><div id="fac-activity-content"></div><div class="fac-live-stats" id="fac-live-stats"></div><div class="fac-live-feed" id="fac-live-feed"></div></div>';
            }

            const shockingClass = slide.shocking_fact ? ' shocking' : '';
            display.innerHTML = '<div class="slide-content dark-glass' + shockingClass + '" id="current-slide" data-slide-id="' + slide.id + '">' +
                imgHTML + titleHTML + bodyHTML + activityBadgeHTML + activityPanelHTML + '</div>';

            // Re-trigger animation
            const content = document.querySelector('.slide-content');
            if (content) {
                content.style.animation = 'none';
                content.offsetHeight;
                content.style.animation = '';
            }

            // Render activity if active
            if (activityActive && slide.slide_type === 'activity' && slide.activity_type) {
                renderFacilitatorActivity(slide.activity_type, slide.activity_config);
            }
        }

        function renderFacilitatorActivity(type, config) {
            const template = (config && config.template) ? config.template : type;
            const titleEl = document.getElementById('fac-activity-title');
            const contentEl = document.getElementById('fac-activity-content');
            if (!titleEl || !contentEl) return;

            switch(template) {
                case 'sprint': renderFacSprint(titleEl, contentEl); break;
                case 'decompose': renderFacDecompose(titleEl, contentEl); break;
                case 'quiz': renderFacQuiz(titleEl, contentEl, config); break;
                case 'commitment': renderFacCommitment(titleEl, contentEl); break;
                case 'sort_stats': renderFacSortStats(titleEl, contentEl, config); break;
                default: titleEl.textContent = type.charAt(0).toUpperCase() + type.slice(1); contentEl.innerHTML = '<p style="color:rgba(255,255,255,0.5)">Activity active</p>'; break;
            }
            refreshLiveStats();
        }

        function hideFacilitatorActivity() {
            const panel = document.getElementById('fac-activity-panel');
            if (panel) panel.style.display = 'none';
        }

        function renderFacSprint(titleEl, contentEl) {
            const data = ACTIVITIES.sprint;
            titleEl.textContent = data.title;
            let binsHTML = '<div class="sort-game-bins">';
            data.bins.forEach(b => {
                binsHTML += '<div class="sort-game-bin" style="border-color:' + b.color + '33"><h4 style="color:' + b.color + '">' + b.name + '</h4><div class="bin-dropzone"></div></div>';
            });
            binsHTML += '</div>';
            let itemsHTML = '<div class="sort-game-items">';
            data.items.forEach(item => {
                itemsHTML += '<div class="sort-game-item">' + item.emoji + ' ' + item.name + '</div>';
            });
            itemsHTML += '</div>';
            contentEl.innerHTML = itemsHTML + binsHTML;
        }

        function renderFacDecompose(titleEl, contentEl) {
            const data = ACTIVITIES.decompose;
            titleEl.textContent = data.title;
            let itemsHTML = '<div class="decompose-items">';
            data.items.forEach(item => {
                itemsHTML += '<div class="decompose-item">' + item.emoji + ' ' + item.name + '</div>';
            });
            itemsHTML += '</div>';
            let timelineHTML = '<div class="decompose-timeline">';
            data.timeline.forEach(t => {
                timelineHTML += '<div class="decompose-slot"><h5>' + t + '</h5><div class="slot-item"></div></div>';
            });
            timelineHTML += '</div>';
            contentEl.innerHTML = itemsHTML + timelineHTML;
        }

        function renderFacQuiz(titleEl, contentEl, config) {
            const data = ACTIVITIES.quiz;
            const questions = (config && config.questions) ? config.questions : data.questions;
            titleEl.textContent = data.title;
            let qHTML = '<div class="quiz-counter">Question 1 of ' + questions.length + '</div>';
            qHTML += '<div class="activity-title" style="font-size:16px;margin-bottom:12px;">' + questions[0].q + '</div>';
            const letters = ['A', 'B', 'C', 'D'];
            qHTML += '<div class="quiz-options">';
            questions[0].options.forEach((opt, i) => {
                qHTML += '<button class="quiz-option" style="pointer-events:none;opacity:0.7"><span class="quiz-letter">' + letters[i] + '</span> ' + opt + '</button>';
            });
            qHTML += '</div>';
            contentEl.innerHTML = qHTML;
        }

        function renderFacCommitment(titleEl, contentEl) {
            const data = ACTIVITIES.commitment;
            titleEl.textContent = data.title;
            contentEl.innerHTML = '<p style="color:rgba(255,255,255,0.6);font-style:italic;">"' + data.prompt + '"</p>';
        }

        function renderFacSortStats(titleEl, contentEl, config) {
            const data = ACTIVITIES.sort_stats;
            const statements = (config && config.statements) ? config.statements : data.statements;
            titleEl.textContent = data.title;
            let qHTML = '<div class="quiz-counter">Statement 1 of ' + statements.length + '</div>';
            qHTML += '<div class="tf-statement">' + statements[0].text + '</div>';
            qHTML += '<div class="tf-buttons"><button class="tf-btn tf-btn-true" style="pointer-events:none;opacity:0.7">✅ True</button><button class="tf-btn tf-btn-false" style="pointer-events:none;opacity:0.7">❌ False</button></div>';
            contentEl.innerHTML = qHTML;
        }

        function refreshLiveStats() {
            const statsEl = document.getElementById('fac-live-stats');
            const feedEl = document.getElementById('fac-live-feed');
            if (!statsEl || !feedEl) return;

            fetch('/session/' + SESSION_CODE + '/activity-stats/')
            .then(r => r.json())
            .then(data => {
                if (data.total > 0) {
                    statsEl.innerHTML = '<div class="fac-stat"><strong>' + data.submitted + '</strong>/' + data.total + ' submitted</div>' +
                        (data.correct !== null ? '<div class="fac-stat"><strong>' + data.correct + '</strong> correct</div>' : '') +
                        '<div class="fac-stat"><strong>' + data.avg_points + '</strong> avg pts</div>';
                } else {
                    statsEl.innerHTML = '<div class="fac-stat">Waiting for submissions...</div>';
                }

                if (data.posts && data.posts.length > 0) {
                    feedEl.innerHTML = data.posts.map(p =>
                        '<div class="fac-feed-item"><span class="fac-feed-avatar">' + p.avatar + '</span><div><span class="fac-feed-name">' + p.name + '</span><div class="fac-feed-content">' + p.content + '</div></div></div>'
                    ).join('');
                } else {
                    feedEl.innerHTML = '';
                }
            });
        }

        function navigateSlide(direction) {
            if (isLoading) return;
            isLoading = true;
            const btnId = direction === 'next' ? 'btn-next' : 'btn-prev';
            const btn = document.getElementById(btnId);
            if (btn) { btn.classList.add('btn-loading'); btn.disabled = true; }

            fetch('/session/' + SESSION_CODE + '/action/' + direction + '/', {
                method: 'POST',
                headers: {'X-CSRFToken': CSRF_TOKEN, 'Content-Type': 'application/x-www-form-urlencoded'},
            }).then(r => r.json()).finally(() => {
                isLoading = false;
                if (btn) { btn.classList.remove('btn-loading'); btn.disabled = false; }
            });
        }

        function gotoSlide(index) {
            if (isLoading) return;
            fetch('/session/' + SESSION_CODE + '/action/goto/', {
                method: 'POST',
                headers: {'X-CSRFToken': CSRF_TOKEN, 'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'index=' + index,
            }).then(r => r.json());
        }

        function sessionAction(action) {
            const btnId = action === 'start_session' ? 'btn-start' : action === 'end_session' ? 'btn-end' : null;
            const doFetch = () => fetch('/session/' + SESSION_CODE + '/action/' + action + '/', {
                method: 'POST',
                headers: {'X-CSRFToken': CSRF_TOKEN, 'Content-Type': 'application/x-www-form-urlencoded'},
            }).then(r => r.json()).then(data => {
                if (data.success) {
                    updateSessionButtons(data.status);
                    const statusEl = document.getElementById('session-status');
                    if (statusEl) {
                        statusEl.textContent = data.status;
                        statusEl.className = 'session-status status-' + data.status;
                    }
                }
            });

            if (btnId) {
                const btn = document.getElementById(btnId);
                if (btn) { btn.classList.add('btn-loading'); btn.disabled = true; }
                doFetch().finally(() => {
                    if (btn) { btn.classList.remove('btn-loading'); btn.disabled = false; }
                });
            } else {
                doFetch();
            }
        }

        function updateSessionButtons(status) {
            const startBtn = document.getElementById('btn-start');
            const endBtn = document.getElementById('btn-end');
            if (status === 'active') {
                if (startBtn) startBtn.remove();
                if (!endBtn) {
                    const actionsDiv = document.querySelector('.action-buttons');
                    const toggleBtn = document.getElementById('btn-activity');
                    const newEndBtn = document.createElement('button');
                    newEndBtn.className = 'btn btn-danger btn-full';
                    newEndBtn.id = 'btn-end';
                    newEndBtn.textContent = '\u23F9 End Session';
                    newEndBtn.onclick = function() { sessionAction('end_session'); };
                    actionsDiv.insertBefore(newEndBtn, toggleBtn);
                }
            } else if (status === 'waiting') {
                if (endBtn) endBtn.remove();
                if (!startBtn) {
                    const actionsDiv = document.querySelector('.action-buttons');
                    const toggleBtn = document.getElementById('btn-activity');
                    const newStartBtn = document.createElement('button');
                    newStartBtn.className = 'btn btn-primary btn-full';
                    newStartBtn.id = 'btn-start';
                    newStartBtn.textContent = '\u25B6 Start Session';
                    newStartBtn.onclick = function() { sessionAction('start_session'); };
                    actionsDiv.insertBefore(newStartBtn, toggleBtn);
                }
            }
        }

        function toggleActivity() {
            if (isLoading) return;
            const action = activityActive ? 'stop_activity' : 'start_activity';
            const btn = document.getElementById('btn-activity');
            if (btn) { btn.classList.add('btn-loading'); btn.disabled = true; }

            fetch('/session/' + SESSION_CODE + '/action/' + action + '/', {
                method: 'POST',
                headers: {'X-CSRFToken': CSRF_TOKEN, 'Content-Type': 'application/x-www-form-urlencoded'},
            }).then(r => r.json()).then(data => {
                if (data.success) {
                    activityActive = data.activity_active;
                    updateActivityBadge();
                    if (activityActive && currentSlideData && currentSlideData.slide_type === 'activity') {
                        renderFacilitatorActivity(currentSlideData.activity_type, currentSlideData.activity_config);
                    } else {
                        hideFacilitatorActivity();
                    }
                }
            }).finally(() => {
                if (btn) { btn.classList.remove('btn-loading'); btn.disabled = false; }
            });
        }

        function updateActivityBadge() {
            const badge = document.getElementById('activity-badge');
            if (badge) badge.style.display = activityActive ? 'inline-flex' : 'none';
            const btn = document.getElementById('btn-activity');
            if (btn) btn.innerHTML = activityActive ? '⏹ Stop Activity' : '🏁 Start Activity';
        }

        function toggleLeaderboard() {
            const section = document.getElementById('leaderboard-section');
            leaderboardVisible = !leaderboardVisible;
            section.style.display = leaderboardVisible ? 'block' : 'none';
            if (leaderboardVisible) loadLeaderboard();
        }

        function loadLeaderboard() {
            fetch('/session/' + SESSION_CODE + '/leaderboard/')
            .then(r => r.json())
            .then(data => {
                const list = document.getElementById('leaderboard-list');
                list.innerHTML = data.leaderboard.map((p, i) =>
                    '<div class="leaderboard-item ' + (i < 3 ? 'top-' + (i+1) : '') + '">' +
                    '<span class="lb-rank">' + (i < 3 ? ['🥇','🥈','🥉'][i] : i+1) + '</span>' +
                    '<span class="lb-avatar">' + p.avatar + '</span>' +
                    '<span class="lb-name">' + p.name + '</span>' +
                    '<span class="lb-points">' + p.points + 'pts</span>' +
                    (p.streak >= 3 ? '<span class="lb-streak">🔥' + p.streak + '</span>' : '') +
                    '<span class="lb-badges">' + p.badges.join(' ') + '</span></div>'
                ).join('');
            });
        }

        function refreshPlayersList() {
            fetch('/session/' + SESSION_CODE + '/state/')
            .then(r => r.json())
            .then(data => {
                document.getElementById('participant-count').textContent = data.participant_count + ' participants';
                const playersSection = document.querySelector('.players-section h3');
                if (playersSection) playersSection.textContent = '👥 Joined Players (' + data.participant_count + ')';
            });
            fetch('/session/' + SESSION_CODE + '/leaderboard/')
            .then(r => r.json())
            .then(data => {
                const list = document.getElementById('players-list');
                if (list) {
                    list.innerHTML = data.leaderboard.map(p =>
                        '<div class="player-item">' +
                        '<span class="player-avatar">' + p.avatar + '</span>' +
                        '<span class="player-name">' + p.name + '</span>' +
                        '<span class="player-points">' + p.points + 'pts</span>' +
                        (p.streak >= 2 ? '<span class="player-streak">🔥' + p.streak + '</span>' : '') +
                        '</div>'
                    ).join('');
                }
            });
        }

        document.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowRight' || e.key === ' ') {
                e.preventDefault();
                navigateSlide('next');
            } else if (e.key === 'ArrowLeft') {
                e.preventDefault();
                navigateSlide('prev');
            }
        });

        setInterval(function() {
            loadLeaderboard();
            refreshPlayersList();
            if (activityActive && currentSlideData && currentSlideData.slide_type === 'activity') {
                refreshLiveStats();
            }
        }, 5000);

        // Initial render
        if (activityActive && currentSlideData && currentSlideData.slide_type === 'activity') {
            renderFacilitatorActivity(currentSlideData.activity_type, currentSlideData.activity_config);
        }

        connectSSE();
    