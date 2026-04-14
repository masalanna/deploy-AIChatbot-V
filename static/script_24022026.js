document.addEventListener("DOMContentLoaded", initializeChat);// Wait for the documents to be fully loaded before initializing the chat

document.getElementById("send-button").addEventListener("click", sendMessage);// Attach event listener to the send button
// document.getElementById("chatbot-reset").addEventListener("click", clearChat);
// document.getElementById('minimize-button').addEventListener("click", minimize);
document.getElementById("user-input").addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        event.preventDefault(); // Prevent default form submission
        sendMessage(); // Call sendMessage function
    }
});

let isMinimized = false; // Flag to track the state of the chatbot

function initializeChat() {
    const chatDisplay = document.getElementById("chat-display");
    //<img src="/static/images/SVA.jfif" alt="Chatbot Icon" class="chatbot-icon">
    const welcomeMessage = `
        <div class="bot-message welcome-message">
            <h3>Welcome to Softdel</h3>
            <p>This is SVA, your virtual assistant!<br> How can I assist you?</p>
            <p>Not sure what to ask? Here are a few suggestions to help you get started.</p>
        </div>
        
        <div class="options">
            <button class="option-button" onclick="handleOptionClick(this, 'products')"><img src="/static/images/product-icon.png" alt="Product Icon" class="tabs-icon"> <span>Products</span></button>
            <button class="option-button" onclick="handleOptionClick(this, 'services')"><img src="/static/images/services-icon.png" alt="Product Icon" class="tabs-icon"> <span>Services</span></button>
            <button class="option-button" onclick="handleOptionClick(this, 'about company')"><img src="/static/images/about-icon.png" alt="Product Icon" class="tabs-icon"> <span>About Company</span></button>
            <button class="option-button" onclick="handleOptionClick(this, 'contact us')"><img src="/static/images/contact-icon.png" alt="Product Icon" class="tabs-icon"> <span>Contact Us</span></button>
            <button class="option-button" onclick="handleOptionClick(this, 'schedule call')"><img src="/static/images/schedule-call-icon.png" alt="Product Icon" class="tabs-icon"> <span>Schedule Call</span></button>
        </div>
    `;
    chatDisplay.innerHTML = welcomeMessage; // Set the initial welcome message
}

function handleOptionClick(button, message) {
    const optionButtons = document.querySelectorAll(".option-button");

    // Disable all main option buttons
    optionButtons.forEach((btn) => {
        btn.disabled = true;
        btn.classList.remove("active-option");
    });

    // Highlight the clicked button
    button.classList.add("active-option");

    const chatDisplay = document.getElementById("chat-display");
    const currentTime = getCurrentTime();

    // Add chatbot message introducing suboptions
    if (message === "products") {
        const botResponse = createBotMessage("Here are some of our Products:");
        chatDisplay.innerHTML += botResponse;

    } else if (message === "schedule call") {
        showScheduleForm();
        chatDisplay.appendChild(formContainer);
    //chatDisplay.scrollTop = chatDisplay.scrollHeight;
    }else if (message === "services") {
        const botResponse = createBotMessage("Our services are designed to cater to your needs. Here are the details:");
        chatDisplay.innerHTML += botResponse;

    } else if (message === "about company") {
        const botResponse = createBotMessage("Let me share some information about our company. Softdel is a leading technology company specializing in IoT, smart building solutions, and protocol engineering:");
        chatDisplay.innerHTML += botResponse;

    } else if (message === "contact us") {
         const contactMsg = `<strong>You can reach us at:</strong><br><br>
                        <strong>Email:</strong> info@softdel.com<br>
                        <strong>Phone:</strong> +91-20 6701 0001<br>
                        <strong>Address:</strong> www.softdel.com
Softdel Systems Private Limited
3rd Floor, Pentagon P4 Magarpatta City, Hadapsar, Pune, Maharashtra 411028, India.`;
            chatDisplay.innerHTML += `
            <div>
                <div class="user-message mb-0" style="display: flex; align-items: flex-start; gap: 10px;">
                    <div class="ai-response-container mb-0" style="text-align: left;">
                        ${message}
                    </div>
                    <div>
                        <img src="/static/images/UserBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res">
                    </div>
                </div>
                <div class="time-stamp-css w-100 userTime">${currentTime}</div>
            </div>`;
            chatDisplay.innerHTML += createBotMessage(contactMsg, new Date().toLocaleTimeString());
    }

    // Display suboptions
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

    // Scroll to the bottom of the chat
      chatDisplay.scrollTop = chatDisplay.scrollHeight;
}
function handleSubOptionClickWithDisable(button, message) {
    alert('Function working correct');
    // Disable all buttons inside the same parent container
    const siblingButtons1 = button.parentElement.querySelectorAll("button");
    siblingButtons1.forEach(btn => btn.disabled = true);

    // Call your original function
    handleSubOptionClick(messagex);
}
function sendMessage() {
    const userInput = document.getElementById("user-input").value.trim();
    if (userInput === "") return; // Do nothing for empty input

    const chatDisplay = document.getElementById("chat-display");
    const currentTime = getCurrentTime();

    // Display user message
    chatDisplay.innerHTML += `
    <div>
        <div class="user-message mb-0" style="display: flex; align-items: flex-start; gap: 10px;">
            <div class="ai-response-container mb-0" style="text-align: left;">
                ${userInput}
            </div>
            <div>
                <img src="/static/images/UserBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res">
            </div>
        </div>
        <div class="time-stamp-css w-100 userTime">${currentTime}</div>
    </div>
    `;
    // 🔹 Check for schedule keywords BEFORE clearing input
    const lowerInput = userInput.toLowerCase();
    if (scheduleKeywords.some(keyword => lowerInput.includes(keyword))) {
         showScheduleForm(); // Show schedule form
         document.getElementById("user-input").value = ""; // Clear input
         return; // Prevent sending message to AI backend
}


//    // 🔹 Check for schedule keywords BEFORE clearing input
//    const lowerInput = userInput.toLowerCase();
//    if (scheduleKeywords.some(keyword => lowerInput.includes(keyword))) {
//        showScheduleForm(); // Show schedule form
//    }

    // Show typing indicator
    const typingIndicator = document.createElement("div");
    typingIndicator.classList.add("bot-message");
    typingIndicator.id = "typing-indicator";
    typingIndicator.innerHTML = '<div id="typingIndicator" class="typing"><div class="dot"></div> <div class="dot"></div><div class="dot"></div></div>';
    chatDisplay.appendChild(typingIndicator);
    chatDisplay.scrollTop = chatDisplay.scrollHeight;

    // Send the message to the server
    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_input: userInput }),
    })
    .then((response) => response.json())
    .then((data) => {
    setTimeout(() => {
        // Remove typing indicator
        const typingIndicator = document.getElementById("typing-indicator");
        if (typingIndicator) chatDisplay.removeChild(typingIndicator);

        let responseText = data.response;

        // Handle markdown-style link: [text](url)
        responseText = responseText.replace(
            /\[([^\]]+)\]\(\s*(https?:\/\/[^\s)]+)\s*\)/g,
            '<a href="$2" target="_blank" style="text-decoration:underline;">$1</a>'
        );

        // Detect “You might also be interested in” section dynamically
        const interestMatch = responseText.match(/You might also be interested in:(.*)/s);
        if (interestMatch) {
            const topicsText = interestMatch[1].trim();

            // Extract bullet points (• or - or newline separated)
            const topics = topicsText
                .split(/\n|•|-/)
                .map(t => t.trim())
                .filter(t => t.length > 0);

            // Convert each topic into a clickable button
            const clickableTopics = topics
                .map(topic => `<button class="clickable-topic" data-topic="${topic}"
                    style="background-color:transparent;
                    border:none;
                    color:#0900FF;
                    text-decoration:underline;
                    cursor:pointer; ">
                    ${topic}
                </button>`)
                .join(" ");

            // Replace the section with clickable buttons
            responseText = responseText.replace(
                /You might also be interested in:(.*)/s,
                `<div style="margin-top:8px;">You might also be interested in:</div><div style="margin-top:6px;">${clickableTopics}</div>`
            );
        }

        const formattedResponse = responseText;
        const currentTime = getCurrentTime();

        // Display bot message
        chatDisplay.innerHTML += `
        <div>
            <div class="bot-message mb-0" style="display: flex; align-items: flex-start; gap: 10px;">
                <div>
                    <img src="/static/images/BotBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res">
                </div>
                <div class="ai-response-container mb-0" style="text-align: left;">
                    ${formattedResponse}
                </div>
            </div>
            <div class="time-stamp-css w-85 botTime">${currentTime}</div>
        </div>`;

        // Scroll to bottom
        chatDisplay.scrollTop = chatDisplay.scrollHeight;

        // Attach click event to dynamic topic buttons
        const topicElements = chatDisplay.querySelectorAll(".clickable-topic");
        topicElements.forEach(el => {
            el.addEventListener("click", () => {
                const selectedTopic = el.dataset.topic;
                document.getElementById("user-input").value = selectedTopic;
                sendMessage(); // Simulate user sending the message
            });
        });

    }, 1000);
})



    .catch((error) => {
        console.error("Error:", error);
        chatDisplay.innerHTML += `
        <div>
            <div class="bot-message mb-0" style="display: flex; align-items: flex-start; gap: 10px;">
                <div>
                    <img src="/static/images/BotBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res">
                </div>
                <div class="ai-response-container mb-0" style="text-align: left;">
                    Sorry, an error occurred. Please try again later.
                </div>
            </div>
            <div class="time-stamp-css w-85 botTime">${currentTime}</div>
        </div>`;
    });

    // Clear input field
    document.getElementById("user-input").value = "";
}

function getCurrentTime() {
    const now = new Date();
    let hours = now.getHours();
    const minutes = now.getMinutes();
    const ampm = hours >= 12 ? "PM" : "AM";
    hours = hours % 12 || 12;
    const formattedMinutes = minutes < 10 ? `0${minutes}` : minutes;
    return `${hours}:${formattedMinutes} ${ampm}`;
}

function clearChat() {
    const chatDisplay = document.getElementById("chat-display");
    chatDisplay.innerHTML = ""; // Clear chat messages
    initializeChat(); // Reload the initial welcome message
}
function minimize() {
    if (!isMinimized) {
        const chatContainer = document.getElementById("chat-container");
        chatContainer.style.position = "fixed";
        chatContainer.style.bottom = "10px"; // Positioning at the bottom
        chatContainer.style.right = "10px"; // Positioning at the right
        chatContainer.style.width = "50px"; // Adjust width for icon
        chatContainer.style.height = "50px"; // Adjust height for icon
        chatContainer.innerHTML = `<img src="/static/images/SVA.jfif" alt="Chatbot Icon" style="width: 50px; height: 50px;">`; // Update with your chatbot icon

        isMinimized = true; // Update state
    }
}


// 🔹 New helper function that disables all sibling buttons once one is clicked
function handleSubSubOptionClickWithDisable(button, message) {
    // Disable all buttons inside the same parent container
    const siblingButtons = button.parentElement.querySelectorAll("button");
    siblingButtons.forEach(btn => btn.disabled = true);

    // Call your original function
    handleSubSubOptionClick(message);
}

function handleSubSubOptionClick(option) {
    const chatDisplay = document.getElementById("chat-display");
    const currentTime = getCurrentTime();

    // Display the selected sub-suboption with detailed information
    let info = "";
    if (option === "BACnet Stack – softBAC") {
        info = "<strong>BACnet Stack – softBAC:</strong><br/> A robust and reliable protocol stack for BACnet communication, designed for seamless integration and high performance in building automation systems.<br/> <br/> If you require more information, please type your question, and I’ll be happy to help.";
    } else if (option === "Modbus Stack – SoftMOD") {
        info = "<strong>Modbus Stack – SoftMOD:</strong><br/>A flexible and efficient Modbus protocol stack, supporting both RTU and TCP/IP for industrial automation applications.<br/> <br/> If you require more information, please type your question, and I’ll be happy to help.";
    } else if (option === "HART Stack – softHARTKNX Protocol") {
        info = "<strong>HART Stack – softHARTKNX Protocol:</strong><br/> A versatile communication stack enabling two-way digital communication over 4-20mA signals, ideal for smart field instruments in industrial automation.<br/> <br/> If you require more information, please type your question, and I’ll be happy to help.";
    } else if (option === "DMX Stack – SoftDMX") {
        info = "<strong>DMX Stack – SoftDMX:</strong><br/> A high-performance protocol stack for DMX communication, tailored for lighting and entertainment control systems.<br/> <br/> If you require more information, please type your question, and I’ll be happy to help.";
    } else if (option === "EdificeEdge – IoT Gateway") {
        info = "<strong>EdificeEdge – IoT Gateway:</strong><br/> A powerful gateway solution that bridges devices and enterprise systems, enabling seamless IoT connectivity and data integration.<br/> <br/> If you require more information, please type your question, and I’ll be happy to help.";
    } else if (option === "EdificePlus - Enterprise Platform") {
        info = "<strong>EdificePlus - Enterprise Platform:</strong><br/> A scalable platform offering advanced analytics and device management for enterprise IoT ecosystems.<br/> <br/> If you require more information, please type your question, and I’ll be happy to help.";
    } else if (option === "BOSS – BACnet Over IP Simulation System") {
        info = "<strong>BOSS – BACnet Over IP Simulation System:</strong><br/>A comprehensive simulation tool for BACnet over IP, allowing testing and validation of BACnet devices and systems.<br/> <br/> If you require more information, please type your question, and I’ll be happy to help.";
    } else if (option === "Device Engineering") {
        info = "<strong>Device Engineering:</strong><br/>Softdel specializes in product design and engineering, helping clients reduce time-to-market and costs. Their expertise spans hardware design, embedded software, testing, and deployment, enabling manufacturers and OEMs to create smart, connected, and IoT-ready products. Services include SoC multilayer boards and SOM-based carrier boards for application processors and microcontrollers.<br/> <br/> If you require more information, please type your question, and I’ll be happy to help.";
    } else if (option === "IoT Solutions and Services") {
        info = "<strong>IoT Solutions and Services:</strong><br/>Softdel provides IoT design, consulting, development, and integration services, enabling global product companies and OEMs to innovate faster. Their future-ready solutions focus on advanced controls, connectivity, and digital transformation, helping clients create cutting-edge, smart, and connected products.<br/> <br/> If you require more information, please type your question, and I’ll be happy to help.";
    } else if (option === "Platform Engineering") {
        info = "<strong>Platform Engineering:</strong><br/>Softdel’s platform engineering services help organizations deliver scalable, cloud-native platforms. By addressing IoT lifecycle challenges, they connect devices and enterprises to create customer-focused solutions. <br/> <br/> If you require more information, please type your question, and I’ll be happy to help.";
    } else if (option === "Managed Services") {
        info = "<strong>Managed Services:</strong><br/> Softdel's managed services ensure scalable, adaptable IT infrastructure tailored to business needs. They handle daily operations with expertise in areas like cloud management, SaaS, hardware, data analytics, DevOps, network security, and technical support, ensuring professional excellence.<br/> <br/> If you require more information, please type your question, and I’ll be happy to help.";
    } else if (option === "Industry 4.0") {
        info = "<strong>Industry 4.0:</strong><br/> Softdel’s expertise with technologies driving Industry 4.0, including AI and machine learning, digital twin technology, cloud computing, IoT, edge computing, and more, help accelerate speed to insights across the industrial lifecycle — from conceptual and engineering design to performance optimisation.<br/> <br/> If you require more information, please type your question, and I’ll be happy to help.";
    } else if (option === "Custom Application Development") {
        info = "<strong>Custom Application Development:</strong><br/>Our Offerings with Softdel’s custom application development services, you receive a powerful solution tailored precisely to your needs, crafted to support your business’s vision and growth trajectory. Leveraging deep technical expertise and a customer-focused approach, we deliver end-to-end solutions that integrate seamlessly into your existing infrastructure.<br/> <br/> If you require more information, please type your question, and I’ll be happy to help.";
    } else if (option === "Testing Services") {
        info = "<strong>Testing Services:</strong><br/> Softdel offers specialised holistic testing services from the edge to the cloud, providing faultless and secure solutions. we employ modern methodologies like agile or traditional software development life cycle (SDLC) to perform quality assurance (QA) for test planning, trace ability, evidence recording, and defect reporting.<br/> <br/> If you require more information, please type your question, and I’ll be happy to help.";
    } else if (option === "IoT Labs") {
        info = "<strong>IoT Labs:</strong><br/> Softdel’s expertise with technologies driving Industry 4.0, including AI and machine learning, digital twin technology, cloud computing, IoT, edge computing, and more, help accelerate speed to insights across the industrial lifecycle — from conceptual and engineering design to performance optimisation.<br/> <br/> If you require more information, please type your question, and I’ll be happy to help.";
    } else if (option === "Functional Safety & Compliance") {
        info = "<strong>Functional Safety & Compliance:</strong><br/>Softdel provides end-to-end testing and certification services, including pre-assessment, gap analysis, and complete compliance testing. We guide you through technical challenges, ensuring your products meet industry-standard compliance requirements and gain access to global markets. We assist customers across diverse product categories throughout the entire certification process. <br/> <br/> If you require more information, please type your question, and I’ll be happy to help." ;
    } else if (option === "Data Analytics & AI") {
        info = "<strong>Data Analytics & AI:</strong><br/> Softdel offers comprehensive data lifecycle services, including acquisition, aggregation, governance, analytics, and visualization. Leveraging AI and domain expertise, they build intelligent systems to extract value from data, prioritize use cases, and connect the unconnected.<br/> <br/> If you require more information, please type your question, and I’ll be happy to help.";
    } else if (option === "Cloud") {
        info = "<strong>Cloud:</strong><br/>Softdel provides advanced cloud services to help businesses integrate their IT and OT business models to enable them to make better business decisions.<br/> <br/> If you require more information, please type your question, and I’ll be happy to help.";
    } else if (option === "Mobile") {
        info = "<strong>Mobile:</strong><br/> Softdel develops tailored mobile applications by combining different data exchange and data processing mediums backed by our in-depth understanding of business requirements. we provide a wide range of mobile app development services, including multi-platform operations, easy device interfacing, data analysis, and reporting.<br/> <br/> If you require more information, please type your question, and I’ll be happy to help.";
    } else if (option === "UI/UX") {
        info = "<strong>UI/UX:</strong><br/> Our UI/UX services are tailored to deliver functional and aesthetically pleasing designs that put the user at the center of the development process. We employ a mix of research, creativity, and the latest design practices to craft experiences that resonate with your audience. <br/> <br/> If you require more information, please type your question, and I’ll be happy to help.";
    } else if (option === "BACnet") {
        info = "BACnet:With our extensive BACnet expertise and experience of 15+ years, we provide holistic services for BACnet enabled solutions, ensuring BACnet compliance and interoperability between devices and systems. We guide OEMs and enterprises through their Buildings-IoT journey, supporting high growth business models and market needs, and enabling a seamless transition to BACnet-enabled solutions.<br/> <br/> If you require more information, please type your question, and I’ll be happy to help.";
    } else {
        info = `Sorry, no additional information is available for "${option}". <br/> <br/> If you require more information, please type your question, and I’ll be happy to help.`;
    }

    // Add the information to the chat display
    chatDisplay.innerHTML += `
    <div>
        <div class="user-message mb-0" style="display: flex; align-items: flex-start; gap: 10px;">
            <div class="ai-response-container mb-0" style="text-align: left;">
                ${option}
            </div>
            <div>
                <img src="/static/images/UserBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res">
            </div>
        </div>
        <div class="time-stamp-css w-100 userTime">${currentTime}</div>
    </div>`;
    chatDisplay.innerHTML += `
    <div>
        <div class="bot-message mb-0" style="display: flex; align-items: flex-start; gap: 10px;">
            <div>
                <img src="/static/images/BotBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res">
            </div>
            <div class="ai-response-container mb-0" style="text-align: left;">
                ${info}
            </div>
        </div>
        <div class="time-stamp-css w-85 botTime">${currentTime}</div>
    </div>`;

    // Scroll to the bottom of the chat
    chatDisplay.scrollTop = chatDisplay.scrollHeight;
}
function handleSubOptionClickWithDisable(button, message) {
    // Disable all buttons inside the same parent container
    const siblingButtons1 = button.parentElement.querySelectorAll("button");
    siblingButtons1.forEach(btn => btn.disabled = true);

    // Call your original function
    handleSubOptionClick(message);
}
function createBotMessage(message) {
    const currentTime = getCurrentTime();
    return `
        <div>
            <div class="bot-message mb-0" style="display: flex; align-items: flex-start; gap: 10px;">
                <div>
                    <img src="/static/images/BotBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res">
                </div>
                <div class="ai-response-container mb-0" style="text-align: left;">
                    ${message}
                </div>
            </div>
            <div class="time-stamp-css w-85 botTime">${currentTime}</div>
        </div>
    `;
}

function handleSubOptionClick(message) {
    const chatDisplay = document.getElementById("chat-display");
    const currentTime = getCurrentTime();

    // Add the user's selected suboption
    chatDisplay.innerHTML += `
    <div>
        <div class="user-message mb-0" style="display: flex; align-items: flex-start; gap: 10px;">
            <div class="ai-response-container mb-0" style="text-align: left;">
                ${message}
            </div>
            <div>
                <img src="/static/images/UserBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res">
            </div>
        </div>
        <div class="time-stamp-css w-100 userTime">${currentTime}</div>
    </div>

    `;

    let optionsHTML = "";

    if (message === "Communication protocol stacks") {
        optionsHTML = `
        <div>
        <div class="bot-message mb-0" style="display: flex; align-items: flex-start; gap: 10px;">
            <div>
               <img src="/static/images/BotBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res">
            </div>
            <div class="ai-response-container mb-0" style="text-align: left;">
                Here are some quality options for Communication protocol stacks:
            </div>
        </div>
        <div class="time-stamp-css w-85 botTime">
         ${currentTime}
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
        <div class="bot-message mb-0" style="display: flex; align-items: flex-start; gap: 10px;">
            <div>
               <img src="/static/images/BotBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res">
            </div>
            <div class="ai-response-container mb-0" style="text-align: left;">
                Here are some quality options for IoT Gateway & Platform:
            </div>
        </div>
        <div class="time-stamp-css w-85 botTime">
         ${currentTime}
        </div>


        <div class="options">
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'EdificeEdge – IoT Gateway')">EdificeEdge – IoT Gateway</button>
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'EdificePlus - Enterprise Platform')">EdificePlus - Enterprise Platform</button>
        </div>`;
    } else if (message === "BACnet Simulator") {
        optionsHTML = `
        <div>
        <div class="bot-message mb-0"  style="display: flex; align-items: flex-start; gap: 10px;">
            <div>
                <img src="/static/images/BotBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res">
            </div>
            <div class="ai-response-container text-align-right mb-0" style ={{textAlign: left}}>
                Here are some quality options for BACnet Simulator:
            </div>
        </div>
        <div class='time-stamp-css w-85 botTime' >
        ${currentTime}
        </div>
        </div>

        <div class="options">
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'BOSS – BACnet Over IP Simulation System')">BOSS – BACnet Over IP Simulation System</button>
        </div>`;
    } else if (message === "Product Engineering") {
        optionsHTML = `

        <div>
        <div class="bot-message mb-0"  style="display: flex; align-items: flex-start; gap: 10px;">
            <div>
                <img src="/static/images/BotBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res">
            </div>
            <div class="ai-response-container mb-0" style={{ textAlign: "left" }}>
               Here are some quality options for Product Engineering:
            </div>

        </div>
        <div class='time-stamp-css w-85 botTime' >
        ${currentTime}
        </div>
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
        <div class="bot-message mb-0"  style="display: flex; align-items: flex-start; gap: 10px;">
            <div>
                <img src="/static/images/BotBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res">
            </div>
            <div class="ai-response-container mb-0" style={{ textAlign: "left" }}>
                Discover Softdel’s world-class quality services crafted to deliver excellence, innovation, and measurable impact.
            </div>

        </div>
        <div class='time-stamp-css w-85 botTime' >
        ${currentTime}
        </div>
        </div>
        <div class="options">
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'Testing Services')">Testing Services</button>
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'IoT Labs')">IoT Labs</button>
            <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'Functional Safety & Compliance')">Functional Safety & Compliance</button>
        </div>`;
    } else if (message === "Centers of Excellence") {
        optionsHTML = `
        <div>
            <div class="bot-message mb-0" style="display: flex; align-items: flex-start; gap: 10px;">
                <div>
                    <img src="/static/images/BotBadge.png" alt="Chatbot Icon" class="chatbot-icon-in-ai-res">
                </div>
                <div class="ai-response-container mb-0" style="text-align: left;">
                    Here are some quality options for Centers of Excellence:
                </div>
            </div>
            <div class="time-stamp-css w-85 botTime">${currentTime}</div>
        </div>
            <div class="options">
                <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'Data Analytics & AI')">Data Analytics & AI</button>
                <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'Cloud')">Cloud</button>
                <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'Mobile')">Mobile</button>
                <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'UI/UX')">UI/UX</button>
                <button class="option-button" onclick="handleSubSubOptionClickWithDisable(this,'BACnet')">BACnet</button>
            </div>
        `;
    } else {
        optionsHTML = `
        <div class="bot-message">
            <div>
                <img src="/static/images/SVA.jfif" alt="Chatbot Icon" class="chatbot-icon-in-ai-res">
            </div>
             Sorry, no further options available for "${message}".
        </div>`;
    }

    chatDisplay.innerHTML += optionsHTML;

    // Scroll to the bottom of the chat
    chatDisplay.scrollTop = chatDisplay.scrollHeight;
}

//Minimize
const minimizeBtn = document.getElementById("chatbot-minimize");
// const avatar = document.getElementById("chatbot-avatar");
const chatContainer = document.getElementById("chat-container"); // ✅ use this

// When avatar is clicked → show chat & hide avatar
// avatar.addEventListener("click", () => {
//     chatContainer.style.display = "flex";  
//     avatar.style.display = "none";         
// });

// When minimize button is clicked → hide chat & show avatar
// minimizeBtn.addEventListener("click", () => {
//     chatContainer.style.display = "none"; 
//     avatar.style.display = "flex"; 
// });
// ======== Schedule Call Form Logic ========

// Keywords that trigger showing the schedule form

// Keywords that trigger the schedule form
const scheduleKeywords = [
    "schedule call",
    "book a meeting",
    "connect with executive",
    "schedule a meeting",
    "talk to representative",
    "call with customer"
];

//// Listen for send button
//document.getElementById("send-button").addEventListener("click", () => {
//    const userInput = document.getElementById("user-input").value.toLowerCase();
//    if (scheduleKeywords.some(keyword => userInput.includes(keyword))) {
//        showScheduleForm();
//    }
//});
//
//// Listen for Enter key
//document.getElementById("user-input").addEventListener("keypress", (event) => {
//    if (event.key === "Enter") {
//        const userInput = document.getElementById("user-input").value.toLowerCase();
//        if (scheduleKeywords.some(keyword => userInput.includes(keyword))) {
//            showScheduleForm();
//        }
//    }
//});

// Show schedule form
//function showScheduleForm() {
//    const chatDisplay = document.getElementById("chat-display");
//
//    // Remove existing form if any
//    const existingForm = document.getElementById("schedule-form");
//    if (existingForm) existingForm.remove();
//
//    // Create form container
//    const formContainer = document.createElement("div");
//    formContainer.id = "schedule-form";
//    formContainer.className = "schedule-form";
//    formContainer.innerHTML = `
//        <h3>📞 Schedule a Call</h3>
//
//<form id="meetingForm">
//    <label for="name">Name:</label>
//    <input type="text" id="name" required />
//
//    <label for="mobile">Mobile:</label>
//    <input type="tel" id="mobile" required pattern="[0-9]{10}" placeholder="10 digit mobile number" />
//
//    <label for="email">Email:</label>
//    <input type="email" id="email" required />
//
//    <label for="date">Date:</label>
//    <input type="date" id="date" required />
//
//    <label for="time">Time:</label>
//    <input type="time" id="time" required />
//
//    <label for="duration">Duration (in minutes):</label>
//    <input type="number" id="duration" min="1" required />
//
//    <button type="submit" id='submit'>Submit data</button>
//</form>
//<script>
//    const form = document.getElementById('meetingForm');
//
//    form.addEventListener('submit', function(e) {
//        e.preventDefault(); // Prevent page reload
//
//        const name = document.getElementById('name').value.trim();
//
//        const mobile = document.getElementById('mobile').value.trim();
//        const email = document.getElementById('email').value.trim();
//        const date = document.getElementById('date').value;
//        const time = document.getElementById('time').value;
//        const duration = document.getElementById('duration').value;
//
//
//        if (!name || !mobile || !email || !date || !time || !duration) {
//            alert('Please fill all fields.');
//            return;
//        }
//
//        fetch('/submit', {
//            method: 'POST',
//            headers: {
//                'Content-Type': 'application/json'
//            },
//            body: JSON.stringify({ name, mobile, email, date, time, duration })
//        })
//        .then(response => response.json())
//        .then(data => {
//            alert(data.message);
//            form.reset();
//        })
//        .catch(error => {
//            console.error('Error:', error);
//            alert("❌ Error submitting form.");
//        });
//    });
//</script>
//    `;
//    chatDisplay.appendChild(formContainer);
//    chatDisplay.scrollTop = chatDisplay.scrollHeight;
//
//    // Attach handlers
//
//}

//function getUserDetails (){
//// Get form values
//        const name = document.getElementById('name').value.trim();
//        const mobile = document.getElementById('mobile').value.trim();
//        const email = document.getElementById('email').value.trim();
//        const date = document.getElementById('date').value;
//        const time = document.getElementById('time').value;
//        const duration = document.getElementById('duration').value;
//
//        // Debug in console
//        console.log("Captured data:", { name, mobile, email, date, time, duration });
//
//        // Validate
//        if (!name || !mobile || !email || !date || !time || !duration) {
//            alert('Please fill all fields.');
//            return;
//        }
//
//        try {
//            const response =  fetch('/submit_schedule', {
//                method: 'POST',
//                headers: { 'Content-Type': 'application/json' },
//                body: JSON.stringify({ name, mobile, email, date, time, duration })
//            });
//
//            const data =  response.json();
//            console.log("Response from backend:", data);
//            alert(data.message);
//            form.reset();
//        } catch (error) {
//            console.error('❌ Error:', error);
//            alert("❌ Error submitting form.");
//        }
//}

function showScheduleForm(event) {
     const chatDisplay = document.getElementById("chat-display");

  // ✅ Remove any existing form first
  const existingForm = document.getElementById("schedule-form");
  if (existingForm) {
    existingForm.remove();
  }

  // ✅ Create a new container div
  const formContainer = document.createElement("div");
  formContainer.id = "schedule-form";
  formContainer.className = "schedule-form";
    formContainer.innerHTML =  `

    <h3 class="mb-0">Please fill the form</h3>
  <form id="callForm">
    <div class="from-group">
        <div>
            <label for="name">Name:</label>
            <input type="text" id="name"  />
            <div class="error-message" id="error-name"></div>
        </div>
        <div>
            <label for="mobile">Mobile:</label>
            <input type="tel" id="mobile"  pattern="[0-9]{10}" placeholder="10 digit mobile number" />
            <div class="error-message" id="error-mobile"></div>
        </div>
    </div>
    <div class="from-group">
    <div>
        <label for="email">Email:</label>
        <input type="email" id="email"  />
        <div class="error-message" id="error-email"></div>
        </div>
        <div>
        <label for="date">Date:</label>
        <input class="input-for-time" type="date" id="date"  />
        <div style="margin-top: 3px;" class="error-message" id="error-date"></div>
      </div>
    </div>
    <div class="from-group" id="schedule-call-time">
      
      <div>
        <label for="time">Time:</label>
        <input class="input-for-time" type="time" id="time"  />
        <div style="margin-top: 3px;" class="error-message" id="error-time"></div>
      </div>
      <div id="duration-div">
        <label for="duration">Duration (in minutes):</label>
        <input class="input-for-time" type="number" id="duration" min="1" />
        <div style="margin-top: 3px;" class="error-message" id="error-duration"></div>
      </div>
    </div>
    <div class="submitBtnContainer">
    <button type="submit" id="submit">Schedule</button>
    </div>
  </form>
`;
    chatDisplay.appendChild(formContainer);
    chatDisplay.scrollTop = chatDisplay.scrollHeight;
    const meetingForm = document.getElementById('callForm');
//    if (!meetingForm) return;
    if (meetingForm) {
    meetingForm.addEventListener("submit", async function (event) {
    event.preventDefault();

        const name = document.getElementById('name').value.trim();
        const mobile = document.getElementById('mobile').value.trim();
        const email = document.getElementById('email').value.trim();
        const date = document.getElementById('date').value;
        const time = document.getElementById('time').value;
        const duration = document.getElementById('duration').value;

        // Debug in console
        console.log("Captured data:", { name, mobile, email, date, time, duration });

        // Validation Start
       // Clear old error messages
document.querySelectorAll('.error-message').forEach(e => e.textContent = '');

// Validation
let hasError = false;

if (!name || !mobile || !email || !date || !time || !duration) {
  if (!name) document.getElementById("error-name").textContent = "Please enter your name.";
  if (!mobile) document.getElementById("error-mobile").textContent = "Please enter your mobile number.";
  if (!email) document.getElementById("error-email").textContent = "Please enter your email.";
  if (!date) document.getElementById("error-date").textContent = "Please select a date.";
  if (!time) document.getElementById("error-time").textContent = "Please select a time.";
  if (!duration) document.getElementById("error-duration").textContent = "Please enter duration.";
  hasError = true;
}

if (name && !/^[a-zA-Z\s]+$/.test(name)) {
  document.getElementById("error-name").textContent = "Name should contain only letters.";
  hasError = true;
}

if (mobile && !/^\d{10}$/.test(mobile)) {
  document.getElementById("error-mobile").textContent = "Enter a valid 10-digit mobile number.";
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

if (duration && (isNaN(duration) || duration <= 0)) {
  document.getElementById("error-duration").textContent = "Duration must be a positive number.";
  hasError = true;
}

// Stop if any errors
if (hasError) return;
        // Validation End

        try {
            const response =  await fetch('/submit_schedule', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, mobile, email, date, time, duration })
            });

            const data = await response.json();
            console.log("Response from backend:", data);
            //alert(data.message);
            if(data.message.includes("scheduled successfully!")){
            meetingForm.style.display = "none";
            // Show success message
        const successMessage = document.createElement('div');
        successMessage.innerHTML = `
            <div class="successMsgStyle">
                Thank you for scheduling a meeting with our executive! <br/>
                We’ll get in touch with you shortly to confirm your appointment.
            </div>
        `;
        meetingForm.parentElement.appendChild(successMessage);
            //clearChat();
            //chatContainer.style.display = "none";
            //avatar.style.display = "flex";
            //meetingForm.reset();
             // Wait 5 seconds, then close chatbox
            setTimeout(() => {
                clearChat();
                chatContainer.style.display = "none";
                avatar.style.display = "flex";
                meetingForm.reset();
                successMessage.remove(); // optional: remove the message after closing
            }, 5000);
            
            }
//               meetingForm.reset();
        } catch (error) {
            console.error('❌ Error:', error);
            alert("❌ Error submitting form.");
        }

     chatDisplay.scrollTop = chatDisplay.scrollHeight;
});
}
else{
 console.log("form:", false);
}
}

// Hide schedule form
function hideScheduleForm() {
    const form = document.getElementById("schedule-form");
    if (form) form.remove();
}

// Submit form handler
