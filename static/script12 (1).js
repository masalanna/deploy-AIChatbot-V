document.addEventListener("DOMContentLoaded", initializeChat);
document.getElementById("send-button").addEventListener("click", sendMessage);
document.getElementById("user-input").addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
});

let isMinimized = false;

// scheduleKeywords array removed — detection is now inline regex
// in sendMessage() using a two-tier intent-aware approach.
// See the scheduling detection block inside sendMessage() below.

// ── DOM refs used in multiple places ─────────────────────────
const chatContainer = document.getElementById("chat-container");

// ============================================================
// initializeChat
// ============================================================
function initializeChat() {
    const chatDisplay = document.getElementById("chat-display");
    const welcomeMessage = `
        <div class="bot-message welcome-message">
            <h3>Welcome to Softdel</h3>
            <p>This is SVA, your virtual assistant!<br> How can I assist you?</p>
            <p>Not sure what to ask? Here are a few suggestions to help you get started.</p>
        </div>
        <div class="options">
            <button class="option-button" onclick="handleOptionClick(this, 'products')">
                <img src="/static/images/product-icon.png" alt="Product Icon" class="tabs-icon">
                <span>Products</span>
            </button>
            <button class="option-button" onclick="handleOptionClick(this, 'services')">
                <img src="/static/images/services-icon.png" alt="Product Icon" class="tabs-icon">
                <span>Services</span>
            </button>
            <button class="option-button" onclick="handleOptionClick(this, 'about company')">
                <img src="/static/images/about-icon.png" alt="Product Icon" class="tabs-icon">
                <span>About Company</span>
            </button>
            <button class="option-button" onclick="handleOptionClick(this, 'contact us')">
                <img src="/static/images/contact-icon.png" alt="Product Icon" class="tabs-icon">
                <span>Contact Us</span>
            </button>
            <button class="option-button" onclick="handleOptionClick(this, 'schedule call')">
                <img src="/static/images/schedule-call-icon.png" alt="Product Icon" class="tabs-icon">
                <span>Schedule Call</span>
            </button>
        </div>
    `;
    chatDisplay.innerHTML = welcomeMessage;
}

// ============================================================
// handleOptionClick  (top-level tabs)
// ============================================================
function handleOptionClick(button, message) {
    const optionButtons = document.querySelectorAll(".option-button");
    optionButtons.forEach(btn => btn.classList.remove("active-option"));
    button.classList.add("active-option");

    const chatDisplay = document.getElementById("chat-display");
    const currentTime = getCurrentTime();

    if (message === "schedule call") {
        // FIX: call showScheduleForm() only — it appends the form itself
        showScheduleForm();
        return;
    }

    if (message === "products") {
        chatDisplay.innerHTML += _userBubble("products", currentTime);
        chatDisplay.innerHTML += createBotMessage("Here are some of our Products:");
    } else if (message === "services") {
        chatDisplay.innerHTML += _userBubble("services", currentTime);
        chatDisplay.innerHTML += createBotMessage("Our services are designed to cater to your needs. Here are the details:");
    } else if (message === "about company") {
        chatDisplay.innerHTML += _userBubble("about company", currentTime);
        chatDisplay.innerHTML += createBotMessage(
            "Let me share some information about our company. Softdel is a leading technology company specializing in IoT, smart building solutions, and protocol engineering."
        );
    } else if (message === "contact us") {
        const contactMsg = `<strong>You can reach us at:</strong><br><br>
            <strong>Email:</strong> info@softdel.com<br>
            <strong>Phone:</strong> +91-20 6701 0001<br>
            <strong>Address:</strong> Softdel Systems Private Limited,
            3rd Floor, Pentagon P4 Magarpatta City, Hadapsar, Pune, Maharashtra 411028, India.<br>
            <strong>Web:</strong> <a href="https://www.softdel.com" target="_blank">www.softdel.com</a>`;
        chatDisplay.innerHTML += _userBubble("contact us", currentTime);
        chatDisplay.innerHTML += createBotMessage(contactMsg);
    }

    // Sub-option buttons for products / services
    let subOptionsHTML = "";
    if (message === "products") {
        subOptionsHTML = `
            <div class="options">
                <button class="option-button" onclick="handleSubOptionClickWithDisable(this,'Communication protocol stacks')">Communication protocol stacks</button>
                <button class="option-button" onclick="handleSubOptionClickWithDisable(this,'IoT Gateway & Platform')">IoT Gateway & Platform</button>
                <button class="option-button" onclick="handleSubOptionClickWithDisable(this,'BACnet Simulator')">BACnet Simulator</button>
            </div>`;
    } else if (message === "services") {
        subOptionsHTML = `
            <div class="options">
                <button class="option-button" onclick="handleSubOptionClickWithDisable(this,'Product Engineering')">Product Engineering</button>
                <button class="option-button" onclick="handleSubOptionClickWithDisable(this,'Quality Engineering')">Quality Engineering</button>
                <button class="option-button" onclick="handleSubOptionClickWithDisable(this,'Centers of Excellence')">Center of Excellence</button>
            </div>`;
    }

    chatDisplay.innerHTML += subOptionsHTML;
    chatDisplay.scrollTop = chatDisplay.scrollHeight;
}

// ============================================================
// handleSubOptionClickWithDisable  (single definition — fixed)
// ============================================================
function handleSubOptionClickWithDisable(button, message) {
    // FIX: removed duplicate definition, removed debug alert, fixed messagex → message
    const siblingButtons = button.parentElement.querySelectorAll("button");
    siblingButtons.forEach(btn => btn.classList.add("active-option"));
    handleSubOptionClick(message);  // FIX: was handleSubOptionClick(messagex)
}

// ============================================================
// handleSubSubOptionClickWithDisable
// ============================================================
function handleSubSubOptionClickWithDisable(button, message) {
    const siblingButtons = button.parentElement.querySelectorAll("button");
    siblingButtons.forEach(btn => btn.classList.add("active-option"));
    handleSubSubOptionClick(message);
}

// ============================================================
// sendMessage
// ============================================================
function sendMessage() {
    const userInput = document.getElementById("user-input").value.trim();
    if (userInput === "") return;

    const chatDisplay = document.getElementById("chat-display");
    const currentTime = getCurrentTime();

    // Display user bubble
    chatDisplay.innerHTML += _userBubble(userInput, currentTime);

    // Scheduling intent detection — mirrors intent_router.py two-tier logic.
    // Tier 1: Strong signals fire alone (schedule / book / arrange / appointment).
    // Tier 2: Weak signals (call / meeting / talk / demo / speak / connect)
    //         only fire when paired with a request phrase like "i want to",
    //         "can you", "please", "let's" — preventing false triggers on
    //         knowledge queries like "tell me about call center solutions".
    const lowerInput = userInput.toLowerCase().trim();
    const strongSchedule = /\b(schedule|book|arrange|appointment)\b/.test(lowerInput);
    const weakSchedule   = /\b(meeting|call|connect|talk|speak|demo)\b/.test(lowerInput);
    const requestPhrase  = /\b(i want to|i.d like to|i would like to|can i|can you|could you|please|help me|set up|let.s|want to|need to)\b/.test(lowerInput);
    if (strongSchedule || (weakSchedule && requestPhrase)) {
        showScheduleForm();
        document.getElementById("user-input").value = "";
        return;
    }

    // Typing indicator
    const typingIndicator = document.createElement("div");
    typingIndicator.classList.add("bot-message");
    typingIndicator.id = "typing-indicator";
    typingIndicator.innerHTML = '<div id="typingIndicator" class="typing"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>';
    chatDisplay.appendChild(typingIndicator);
    chatDisplay.scrollTop = chatDisplay.scrollHeight;

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_input: userInput }),
    })
    .then(response => response.json())
    .then(data => {
        setTimeout(() => {
            const indicator = document.getElementById("typing-indicator");
            if (indicator) chatDisplay.removeChild(indicator);

            // show_form from backend: only show form if one isn't already open.
            // Prevents double-render on the rare edge case where JS and backend
            // both flag the same input (should not happen after tightened detection,
            // but kept as a safety net).
            if (data.show_form) {
                if (!document.getElementById("schedule-form")) {
                    showScheduleForm();
                }
                return;
            }

            let responseText = data.response || "Sorry, I couldn't get a response.";

            // Render markdown links: [text](url)
            responseText = responseText.replace(
                /\[([^\]]+)\]\(\s*(https?:\/\/[^\s)]+)\s*\)/g,
                '<a href="$2" target="_blank" style="text-decoration:underline;">$1</a>'
            );

            // Render "You might also be interested in:" as clickable topic buttons
            const interestMatch = responseText.match(/You might also be interested in:(.*)/s);
            if (interestMatch) {
                const topicsText = interestMatch[1].trim();
                const topics = topicsText
                    .split(/\n|•|-/)
                    .map(t => t.replace(/^[\s🌐🏭⚡✨🔗]+/, "").trim())
                    .filter(t => t.length > 0);

                const clickableTopics = topics
                    .map(topic => `<button class="clickable-topic" data-topic="${topic}"
                        style="background-color:transparent; border:none; color:#0900FF;
                               text-decoration:underline; cursor:pointer; margin:2px;">
                        ${topic}
                    </button>`)
                    .join(" ");

                responseText = responseText.replace(
                    /You might also be interested in:(.*)/s,
                    `<div style="margin-top:8px;">You might also be interested in:</div>
                     <div style="margin-top:6px;">${clickableTopics}</div>`
                );
            }

            // Display bot bubble
            chatDisplay.innerHTML += `
            <div>
                <div class="bot-message mb-0" style="display: flex; align-items: flex-start; gap: 10px;">
                    <div>
                        <img src="/static/images/BotBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res">
                    </div>
                    <div class="ai-response-container mb-0" style="text-align: left;">
                        ${responseText}
                    </div>
                </div>
                <div class="time-stamp-css w-85 botTime">${getCurrentTime()}</div>
            </div>`;

            chatDisplay.scrollTop = chatDisplay.scrollHeight;

            // Attach click events to topic buttons
            chatDisplay.querySelectorAll(".clickable-topic").forEach(el => {
                el.addEventListener("click", () => {
                    document.getElementById("user-input").value = el.dataset.topic;
                    sendMessage();
                });
            });

        }, 1000);
    })
    .catch(error => {
        console.error("Fetch error:", error);
        const indicator = document.getElementById("typing-indicator");
        if (indicator) chatDisplay.removeChild(indicator);
        chatDisplay.innerHTML += createBotMessage("Sorry, an error occurred. Please try again later.");
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    });

    document.getElementById("user-input").value = "";
}

// ============================================================
// showScheduleForm
// ============================================================
function showScheduleForm() {
    const chatDisplay = document.getElementById("chat-display");

    // Remove any existing form first
    const existingForm = document.getElementById("schedule-form");
    if (existingForm) existingForm.remove();

    // Create form container
    const formContainer = document.createElement("div");
    formContainer.id = "schedule-form";
    formContainer.className = "schedule-form";
    formContainer.innerHTML = `
        <h3 class="mb-0">Please fill the form</h3>
        <form id="callForm">
            <div class="from-group">
                <div>
                    <label for="name">Name:</label>
                    <input type="text" id="name" />
                    <div class="error-message" id="error-name"></div>
                </div>
                <div>
                    <label for="mobile">Mobile:</label>
                    <input type="tel" id="mobile" placeholder="+44 7123 456789" />
                    <div class="error-message" id="error-mobile"></div>
                </div>
            </div>
            <div class="from-group">
                <div>
                    <label for="email">Email:</label>
                    <input type="email" id="email" />
                    <div class="error-message" id="error-email"></div>
                </div>
                <div>
                    <label for="date">Date:</label>
                    <input class="input-for-time" type="date" id="date" />
                    <div style="margin-top:3px;" class="error-message" id="error-date"></div>
                </div>
            </div>
            <div class="from-group" id="schedule-call-time">
                <div>
                    <label for="time">Time:</label>
                    <input class="input-for-time" type="time" id="time" />
                    <div style="margin-top:3px;" class="error-message" id="error-time"></div>
                </div>
                <div id="duration-div">
                    <label for="duration">Duration (in minutes):</label>
                    <input class="input-for-time" type="number" id="duration" min="30" step="30" placeholder="Minimum 30 minutes" />
                    <div style="margin-top:3px;" class="error-message" id="error-duration"></div>
                </div>
            </div>
            <div class="submitBtnContainer">
                <button type="submit" id="submit">Schedule</button>
            </div>
        </form>
    `;

    // FIX: append via formContainer variable (in scope here)
    chatDisplay.appendChild(formContainer);
    chatDisplay.scrollTop = chatDisplay.scrollHeight;

    const meetingForm = document.getElementById("callForm");
    if (!meetingForm) return;

    meetingForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const name     = document.getElementById("name").value.trim();
        const mobile   = document.getElementById("mobile").value.trim();
        const email    = document.getElementById("email").value.trim();
        const date     = document.getElementById("date").value;
        const time     = document.getElementById("time").value;
        const duration = document.getElementById("duration").value;

        // Clear previous errors
        document.querySelectorAll(".error-message").forEach(e => e.textContent = "");

        // Validation
        let hasError = false;

        if (!name)     { document.getElementById("error-name").textContent     = "Please enter your name.";           hasError = true; }
        if (!mobile)   { document.getElementById("error-mobile").textContent   = "Please enter your mobile number.";  hasError = true; }
        if (!email)    { document.getElementById("error-email").textContent    = "Please enter your email.";           hasError = true; }
        if (!date)     { document.getElementById("error-date").textContent     = "Please select a date.";              hasError = true; }
        if (!time)     { document.getElementById("error-time").textContent     = "Please select a time.";              hasError = true; }
        if (!duration) { document.getElementById("error-duration").textContent = "Please enter duration.";             hasError = true; }

        if (name && !/^[a-zA-Z\s]+$/.test(name)) {
            document.getElementById("error-name").textContent = "Name should contain only letters.";
            hasError = true;
        }
        if (mobile && !/^\+?[0-9\s\-]{7,15}$/.test(mobile)) {
            document.getElementById("error-mobile").textContent = "Enter a valid international phone number (7–15 digits, optional +).";
            hasError = true;
        }
        if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            document.getElementById("error-email").textContent = "Enter a valid email address.";
            hasError = true;
        }
        const today = new Date().toISOString().split("T")[0];
        if (date && date < today) {
            document.getElementById("error-date").textContent = "Date cannot be in the past.";
            hasError = true;
        }
        if (duration && (isNaN(duration) || duration < 30 || duration % 30 !== 0)) {
            document.getElementById("error-duration").textContent = "Duration must be minimum 30 minutes and in 30-minute increments.";
            hasError = true;
        }

        if (hasError) return;

        try {
            const response = await fetch("/submit_schedule", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, mobile, email, date, time, duration }),
            });

            const data = await response.json();
            console.log("Schedule response:", data);

            if (data.success) {
                meetingForm.style.display = "none";

                const successMessage = document.createElement("div");
                successMessage.innerHTML = `
                    <div class="successMsgStyle">
                        Thank you for scheduling a meeting with our executive! <br/>
                        We'll get in touch with you shortly to confirm your appointment.
                    </div>
                `;
                meetingForm.parentElement.appendChild(successMessage);

                // Success UX: keep chat fully visible and accessible.
                // The form fades out, success message stays for 6s, then
                // the schedule-form wrapper removes itself so the user can
                // continue chatting naturally — no abrupt reset or hide.
                setTimeout(() => {
                    const scheduleWrapper = document.getElementById("schedule-form");
                    if (scheduleWrapper) scheduleWrapper.remove();
                    meetingForm.reset();
                }, 6000);

            } else {
                // Show backend error message inline
                const errDiv = document.createElement("div");
                errDiv.style.cssText = "color:red; margin-top:8px; font-size:0.9em;";
                errDiv.textContent = data.message || "Scheduling failed. Please try again.";
                meetingForm.appendChild(errDiv);
                setTimeout(() => errDiv.remove(), 4000);
            }

        } catch (error) {
            console.error("Schedule fetch error:", error);
            alert("❌ Error submitting form. Please try again.");
        }

        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    });
}

// ============================================================
// hideScheduleForm
// ============================================================
function hideScheduleForm() {
    const form = document.getElementById("schedule-form");
    if (form) form.remove();
}

// ============================================================
// handleSubOptionClick  (second-level: product/service categories)
// ============================================================
function handleSubOptionClick(message) {
    const chatDisplay = document.getElementById("chat-display");
    const currentTime = getCurrentTime();
    let optionsHTML = "";

    if (message === "Communication protocol stacks") {
        optionsHTML = `
        <div>
            <div class="bot-message mb-0" style="display:flex; align-items:flex-start; gap:10px;">
                <div><img src="/static/images/BotBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res"></div>
                <div class="ai-response-container mb-0" style="text-align:left;">Here are the Communication Protocol Stacks:</div>
            </div>
            <div class="time-stamp-css w-85 botTime">${currentTime}</div>
        </div>
        <div class="options">
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'BACnet Stack – softBAC')">BACnet Stack – softBAC</button>
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'Modbus Stack – SoftMOD')">Modbus Stack – SoftMOD</button>
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'HART Stack – softHARTKNX Protocol')">HART Stack – softHARTKNX Protocol</button>
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'DMX Stack – SoftDMX')">DMX Stack – SoftDMX</button>
        </div>`;
    } else if (message === "IoT Gateway & Platform") {
        optionsHTML = `
        <div>
            <div class="bot-message mb-0" style="display:flex; align-items:flex-start; gap:10px;">
                <div><img src="/static/images/BotBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res"></div>
                <div class="ai-response-container mb-0" style="text-align:left;">Here are some options for IoT Gateway & Platform:</div>
            </div>
            <div class="time-stamp-css w-85 botTime">${currentTime}</div>
        </div>
        <div class="options">
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'EdificeEdge – IoT Gateway')">EdificeEdge – IoT Gateway</button>
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'EdificePlus - Enterprise Platform')">EdificePlus - Enterprise Platform</button>
        </div>`;
    } else if (message === "BACnet Simulator") {
        optionsHTML = `
        <div>
            <div class="bot-message mb-0" style="display:flex; align-items:flex-start; gap:10px;">
                <div><img src="/static/images/BotBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res"></div>
                <div class="ai-response-container mb-0" style="text-align:left;">Here are options for BACnet Simulator:</div>
            </div>
            <div class="time-stamp-css w-85 botTime">${currentTime}</div>
        </div>
        <div class="options">
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'BOSS – BACnet Over IP Simulation System')">BOSS – BACnet Over IP Simulation System</button>
        </div>`;
    } else if (message === "Product Engineering") {
        optionsHTML = `
        <div>
            <div class="bot-message mb-0" style="display:flex; align-items:flex-start; gap:10px;">
                <div><img src="/static/images/BotBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res"></div>
                <div class="ai-response-container mb-0" style="text-align:left;">Here are options for Product Engineering:</div>
            </div>
            <div class="time-stamp-css w-85 botTime">${currentTime}</div>
        </div>
        <div class="options">
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'Device Engineering')">Device Engineering</button>
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'IoT Solutions and Services')">IoT Solutions and Services</button>
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'Platform Engineering')">Platform Engineering</button>
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'Managed Services')">Managed Services</button>
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'Industry 4.0')">Industry 4.0</button>
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'Custom Application Development')">Custom Application Development</button>
        </div>`;
    } else if (message === "Quality Engineering") {
        optionsHTML = `
        <div>
            <div class="bot-message mb-0" style="display:flex; align-items:flex-start; gap:10px;">
                <div><img src="/static/images/BotBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res"></div>
                <div class="ai-response-container mb-0" style="text-align:left;">Discover Softdel's world-class quality services:</div>
            </div>
            <div class="time-stamp-css w-85 botTime">${currentTime}</div>
        </div>
        <div class="options">
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'Testing Services')">Testing Services</button>
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'IoT Labs')">IoT Labs</button>
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'Functional Safety & Compliance')">Functional Safety & Compliance</button>
        </div>`;
    } else if (message === "Centers of Excellence") {
        optionsHTML = `
        <div>
            <div class="bot-message mb-0" style="display:flex; align-items:flex-start; gap:10px;">
                <div><img src="/static/images/BotBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res"></div>
                <div class="ai-response-container mb-0" style="text-align:left;">Here are options for Centers of Excellence:</div>
            </div>
            <div class="time-stamp-css w-85 botTime">${currentTime}</div>
        </div>
        <div class="options">
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'Data Analytics & AI')">Data Analytics & AI</button>
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'Cloud')">Cloud</button>
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'Mobile')">Mobile</button>
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'UI/UX')">UI/UX</button>
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'BACnet')">BACnet</button>
        </div>`;
    } else {
        optionsHTML = `<div class="bot-message">Sorry, no further options available for "${message}".</div>`;
    }

    chatDisplay.innerHTML += optionsHTML;
    chatDisplay.scrollTop = chatDisplay.scrollHeight;
}

// ============================================================
// handleSubSubOptionClick  (leaf level — shows product/service info)
// ============================================================
function handleSubSubOptionClick(option) {
    const chatDisplay = document.getElementById("chat-display");
    const currentTime = getCurrentTime();

    const infoMap = {
        "BACnet Stack – softBAC":               "<strong>BACnet Stack – softBAC:</strong><br/> A robust and reliable protocol stack for BACnet communication, designed for seamless integration and high performance in building automation systems.<br/><br/> If you require more information, please type your question and I'll be happy to help.",
        "Modbus Stack – SoftMOD":               "<strong>Modbus Stack – SoftMOD:</strong><br/> A flexible and efficient Modbus protocol stack, supporting both RTU and TCP/IP for industrial automation applications.<br/><br/> If you require more information, please type your question and I'll be happy to help.",
        "HART Stack – softHARTKNX Protocol":    "<strong>HART Stack – softHARTKNX Protocol:</strong><br/> A versatile communication stack enabling two-way digital communication over 4-20mA signals, ideal for smart field instruments in industrial automation.<br/><br/> If you require more information, please type your question and I'll be happy to help.",
        "DMX Stack – SoftDMX":                  "<strong>DMX Stack – SoftDMX:</strong><br/> A high-performance protocol stack for DMX communication, tailored for lighting and entertainment control systems.<br/><br/> If you require more information, please type your question and I'll be happy to help.",
        "EdificeEdge – IoT Gateway":            "<strong>EdificeEdge – IoT Gateway:</strong><br/> A powerful gateway solution that bridges devices and enterprise systems, enabling seamless IoT connectivity and data integration.<br/><br/> If you require more information, please type your question and I'll be happy to help.",
        "EdificePlus - Enterprise Platform":    "<strong>EdificePlus - Enterprise Platform:</strong><br/> A scalable platform offering advanced analytics and device management for enterprise IoT ecosystems.<br/><br/> If you require more information, please type your question and I'll be happy to help.",
        "BOSS – BACnet Over IP Simulation System": "<strong>BOSS – BACnet Over IP Simulation System:</strong><br/> A comprehensive simulation tool for BACnet over IP, allowing testing and validation of BACnet devices and systems.<br/><br/> If you require more information, please type your question and I'll be happy to help.",
        "Device Engineering":                   "<strong>Device Engineering:</strong><br/> Softdel specializes in product design and engineering, helping clients reduce time-to-market and costs. Expertise spans hardware design, embedded software, testing, and deployment for smart, connected IoT-ready products.<br/><br/> If you require more information, please type your question and I'll be happy to help.",
        "IoT Solutions and Services":           "<strong>IoT Solutions and Services:</strong><br/> Softdel provides IoT design, consulting, development, and integration services, enabling global product companies and OEMs to innovate faster with future-ready connected solutions.<br/><br/> If you require more information, please type your question and I'll be happy to help.",
        "Platform Engineering":                 "<strong>Platform Engineering:</strong><br/> Softdel's platform engineering services help organizations deliver scalable, cloud-native platforms, connecting devices and enterprises to create customer-focused solutions.<br/><br/> If you require more information, please type your question and I'll be happy to help.",
        "Managed Services":                     "<strong>Managed Services:</strong><br/> Softdel's managed services ensure scalable, adaptable IT infrastructure covering cloud management, SaaS, data analytics, DevOps, network security, and technical support.<br/><br/> If you require more information, please type your question and I'll be happy to help.",
        "Industry 4.0":                         "<strong>Industry 4.0:</strong><br/> Softdel's expertise with AI, machine learning, digital twin, cloud, IoT, and edge computing accelerates speed-to-insights across the industrial lifecycle.<br/><br/> If you require more information, please type your question and I'll be happy to help.",
        "Custom Application Development":       "<strong>Custom Application Development:</strong><br/> Softdel delivers end-to-end custom solutions tailored to your business vision, integrating seamlessly into your existing infrastructure with deep technical expertise.<br/><br/> If you require more information, please type your question and I'll be happy to help.",
        "Testing Services":                     "<strong>Testing Services:</strong><br/> Softdel offers holistic testing from edge to cloud using agile and SDLC methodologies for QA, test planning, traceability, evidence recording, and defect reporting.<br/><br/> If you require more information, please type your question and I'll be happy to help.",
        "IoT Labs":                             "<strong>IoT Labs:</strong><br/> Softdel's IoT Labs leverage AI, digital twin, cloud, and edge computing to accelerate speed-to-insights across the industrial lifecycle.<br/><br/> If you require more information, please type your question and I'll be happy to help.",
        "Functional Safety & Compliance":       "<strong>Functional Safety & Compliance:</strong><br/> Softdel provides end-to-end testing and certification including pre-assessment, gap analysis, and complete compliance testing to meet industry-standard requirements.<br/><br/> If you require more information, please type your question and I'll be happy to help.",
        "Data Analytics & AI":                  "<strong>Data Analytics & AI:</strong><br/> Softdel offers comprehensive data lifecycle services — acquisition, aggregation, governance, analytics, and visualization — leveraging AI and domain expertise.<br/><br/> If you require more information, please type your question and I'll be happy to help.",
        "Cloud":                                "<strong>Cloud:</strong><br/> Softdel provides advanced cloud services to help businesses integrate IT and OT models for better business decisions.<br/><br/> If you require more information, please type your question and I'll be happy to help.",
        "Mobile":                               "<strong>Mobile:</strong><br/> Softdel develops tailored mobile applications combining data exchange and processing with in-depth business understanding across multi-platform operations.<br/><br/> If you require more information, please type your question and I'll be happy to help.",
        "UI/UX":                                "<strong>UI/UX:</strong><br/> Softdel's UI/UX services deliver functional, aesthetically pleasing designs centered on user research, creativity, and modern design practices.<br/><br/> If you require more information, please type your question and I'll be happy to help.",
        "BACnet":                               "<strong>BACnet:</strong><br/> With 15+ years of BACnet expertise, Softdel provides holistic services for BACnet-enabled solutions ensuring compliance and interoperability between devices and systems.<br/><br/> If you require more information, please type your question and I'll be happy to help.",
    };

    const info = infoMap[option] || `Sorry, no additional information is available for "${option}".<br/><br/> If you require more information, please type your question and I'll be happy to help.`;

    chatDisplay.innerHTML += _userBubble(option, currentTime);
    chatDisplay.innerHTML += `
    <div>
        <div class="bot-message mb-0" style="display:flex; align-items:flex-start; gap:10px;">
            <div><img src="/static/images/BotBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res"></div>
            <div class="ai-response-container mb-0" style="text-align:left;">${info}</div>
        </div>
        <div class="time-stamp-css w-85 botTime">${currentTime}</div>
    </div>`;

    chatDisplay.scrollTop = chatDisplay.scrollHeight;
}

// ============================================================
// Utility helpers
// ============================================================

function createBotMessage(message) {
    const currentTime = getCurrentTime();
    return `
        <div>
            <div class="bot-message mb-0" style="display:flex; align-items:flex-start; gap:10px;">
                <div><img src="/static/images/BotBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res"></div>
                <div class="ai-response-container mb-0" style="text-align:left;">${message}</div>
            </div>
            <div class="time-stamp-css w-85 botTime">${currentTime}</div>
        </div>`;
}

function _userBubble(text, currentTime) {
    return `
    <div>
        <div class="user-message mb-0" style="display:flex; align-items:flex-start; gap:10px;">
            <div class="ai-response-container mb-0" style="text-align:left;">${text}</div>
            <div><img src="/static/images/UserBadge.png" alt="User" class="chatbot-icon-in-ai-res"></div>
        </div>
        <div class="time-stamp-css w-100 userTime">${currentTime}</div>
    </div>`;
}

function getCurrentTime() {
    const now = new Date();
    let hours = now.getHours();
    const minutes = now.getMinutes();
    const ampm = hours >= 12 ? "PM" : "AM";
    hours = hours % 12 || 12;
    return `${hours}:${minutes < 10 ? "0" + minutes : minutes} ${ampm}`;
}

function clearChat() {
    const chatDisplay = document.getElementById("chat-display");
    chatDisplay.innerHTML = "";
    initializeChat();
}

function minimize() {
    if (!isMinimized && chatContainer) {
        chatContainer.style.position = "fixed";
        chatContainer.style.bottom = "10px";
        chatContainer.style.right = "10px";
        chatContainer.style.width = "50px";
        chatContainer.style.height = "50px";
        chatContainer.innerHTML = `<img src="/static/images/SVA.jfif" alt="Chatbot Icon" style="width:50px; height:50px;">`;
        isMinimized = true;
    }
}
