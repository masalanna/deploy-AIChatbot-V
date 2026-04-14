// ✅ Utility to get current time
function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// ✅ Typing indicator functions
function showTypingIndicator() {
    const chatDisplay = document.getElementById("chat-display");

    const typingIndicator = document.createElement("div");
    typingIndicator.classList.add("bot-message");
    typingIndicator.id = "typing-indicator";
    typingIndicator.innerHTML = `
        <div class="typing-indicator">
            <span></span><span></span><span></span>
        </div>
    `;

    chatDisplay.appendChild(typingIndicator);
    chatDisplay.scrollTop = chatDisplay.scrollHeight;
}

function removeTypingIndicator() {
    const chatDisplay = document.getElementById("chat-display");
    const typingIndicator = document.getElementById("typing-indicator");
    if (typingIndicator) {
        chatDisplay.removeChild(typingIndicator);
    }
}

// ✅ Function to create bot message
function createBotMessage(message) {
    const currentTime = getCurrentTime();
    return `
        <div>
            <div class="bot-message mb-0" style="display: flex; align-items: flex-start; gap: 10px;">
                <div>
                    <img src="/static/images/SVA.jfif" alt="Chatbot Icon" class="chatbot-icon-in-ai-res">
                </div>
                <div class="ai-response-container mb-0" style="text-align: left;">
                    ${message}
                </div>
            </div>
            <div class="time-stamp-css w-85">${currentTime}</div>
        </div>
    `;
}

// ✅ Function to create option buttons
function createOptions(options) {
    let buttonsHTML = `<div class="options-container">`;
    options.forEach(opt => {
        buttonsHTML += `<button class="option-btn" onclick="handleOptionClick(this, '${opt}')">${opt}</button>`;
    });
    buttonsHTML += `</div>`;
    return buttonsHTML;
}

// ✅ Initial welcome message (merged from initializeChat)
window.onload = function () {
    const chatDisplay = document.getElementById("chat-display");

    showTypingIndicator();

    setTimeout(() => {
        removeTypingIndicator();

        const welcomeMessage = `
            <div class="bot-message welcome-message">
                <img src="/static/images/SVA.jfif" alt="Chatbot Icon" class="chatbot-icon">
                Welcome to Softdel, this is SVA, your virtual assistant!<br>
                How can I assist you today?
            </div>
            <div class="bot-message">
                Don't know what to ask? Here are some suggestions:
            </div>
        `;

        chatDisplay.innerHTML += welcomeMessage;

        // Show clickable options automatically
        chatDisplay.innerHTML += createOptions([
            "Products",
            "Services",
            "About Company",
            "Contact Us"
        ]);

        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    }, 1200);
};

// ✅ Handle option clicks
function handleOptionClick(button, message) {
    const chatDisplay = document.getElementById("chat-display");

    // Show user message
    const userMessage = `
        <div class="user-message">
            ${message}
        </div>
    `;
    chatDisplay.innerHTML += userMessage;

    // Show typing animation
    showTypingIndicator();

    // Simulate bot delay
    setTimeout(() => {
        removeTypingIndicator();

        let botResponse = "";
        let options = [];

        if (message === "Products") {
            botResponse = createBotMessage("Here are some of our Products:");
            options = ["Product Engineering", "Communication protocol stacks", "IoT Gateway & Platform"];
        } else if (message === "Services") {
            botResponse = createBotMessage("Here are some of our Services:");
            options = ["Consulting", "Support", "Custom Development"];
        } else if (message === "About Company") {
            botResponse = createBotMessage("Softdel is a global technology company specializing in engineering and IoT solutions.");
        } else if (message === "Contact Us") {
            botResponse = createBotMessage("You can reach us at: contact@softdel.com 📧");
        } else if (message === "Product Engineering") {
            botResponse = createBotMessage("Here are some quality options for Product Engineering:");
            options = ["Design Services", "Development", "Testing"];
        } else if (message === "Communication protocol stacks") {
            botResponse = createBotMessage("Here are some quality options for Communication protocol stacks:");
            options = ["BACnet", "Modbus", "KNX"];
        } else if (message === "IoT Gateway & Platform") {
            botResponse = createBotMessage("Here are some quality options for IoT Gateway & Platform:");
            options = ["Edge Gateway", "Cloud Integration", "Analytics"];
        } else {
            botResponse = createBotMessage(`Here is the response for "${message}".`);
        }

        chatDisplay.innerHTML += botResponse;

        // Show sub-options if available
        if (options.length > 0) {
            chatDisplay.innerHTML += createOptions(options);
        }

        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    }, 1200);
}
