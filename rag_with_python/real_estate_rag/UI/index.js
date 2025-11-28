const form = document.querySelector("form");
const input = document.querySelector("input");
const chatContainer = document.getElementById("chatContainer");
const agentTypeSelect = document.getElementById("agentType");

// Session memory to store conversation history
let conversationHistory = [];
let currentAgentType = "rag";

// Clear history when agent type changes
agentTypeSelect.addEventListener("change", function() {
  if (agentTypeSelect.value !== currentAgentType) {
    conversationHistory = [];
    currentAgentType = agentTypeSelect.value;
    addSystemMessage(`Switched to ${agentTypeSelect.options[agentTypeSelect.selectedIndex].text}. Previous conversation cleared.`);
  }
});

form.addEventListener("submit", function (e) {
  e.preventDefault();
  const question = input.value.trim();
  if (question) {
    addMessage(question, "user");
    const agentType = agentTypeSelect.value;
    
    // Add user message to history
    conversationHistory.push({
      role: "user",
      content: question
    });
    
    main(question, agentType);
    input.value = "";
  }
});

function addMessage(text, type) {
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${type}-message`;
  
  if (type === "bot") {
    messageDiv.innerHTML = formatResponse(text);
  } else {
    messageDiv.textContent = text;
  }
  
  chatContainer.appendChild(messageDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

function addSystemMessage(text) {
  const messageDiv = document.createElement("div");
  messageDiv.className = "message system-message";
  messageDiv.textContent = text;
  chatContainer.appendChild(messageDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

function formatResponse(text) {
  // Convert markdown-style formatting to HTML
  let formatted = text
    // Headers
    .replace(/### ([^\n]+)/g, '<h3>$1</h3>')
    .replace(/## ([^\n]+)/g, '<h2>$1</h2>')
    // Bold
    .replace(/\*\*([^\*]+)\*\*/g, '<strong>$1</strong>')
    // Bullet points
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    // Links
    .replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
    // Line breaks
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>');
  
  // Wrap consecutive <li> in <ul>
  formatted = formatted.replace(/(<li>.*<\/li>)/s, function(match) {
    return '<ul>' + match + '</ul>';
  });
  
  // Wrap in paragraphs
  if (!formatted.startsWith('<h') && !formatted.startsWith('<ul>')) {
    formatted = '<p>' + formatted + '</p>';
  }
  
  return formatted;
}

async function main(question, agentType) {
  try {
    console.log("Question received:", question, "Agent type:", agentType);
    console.log("Conversation history:", conversationHistory);
    
    // Add thinking indicator
    const thinkingDiv = document.createElement("div");
    thinkingDiv.className = "message bot-message thinking";
    thinkingDiv.innerHTML = '<span class="typing-indicator"><span></span><span></span><span></span></span>';
    chatContainer.appendChild(thinkingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    let endpoint, requestBody;
    
    // Determine endpoint and request body based on agent type
    if (agentType === "rag") {
      endpoint = "http://localhost:8000/query/rag";
      requestBody = { 
        query: question,
        conversation_history: conversationHistory.slice(-10), // Last 10 messages
        max_history: 10
      };
    } else if (agentType === "auto") {
      endpoint = "http://localhost:8000/query/auto";
      requestBody = { 
        query: question,
        conversation_history: conversationHistory.slice(-10),
        max_history: 10
      };
    } else {
      // buy, rent, or details agent
      endpoint = "http://localhost:8000/query/agent";
      requestBody = {
        agent_type: agentType,
        message: question,
        conversation_history: conversationHistory.slice(-10),
        context: {}
      };
    }

    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("Final response:", data);
    
    // Remove thinking indicator
    chatContainer.removeChild(thinkingDiv);
    
    // Extract answer based on response type
    let answer;
    if (agentType === "rag") {
      answer = data.answer;
    } else if (agentType === "auto") {
      answer = data.response || data.answer || JSON.stringify(data);
    } else {
      // Agent response
      answer = data.response || data.message || JSON.stringify(data);
    }
    
    // Add assistant response to history
    conversationHistory.push({
      role: "assistant",
      content: answer
    });
    
    // Add bot response
    addMessage(answer, "bot");
  } catch (error) {
    console.error("Error in main function.", error.message);
    
    // Remove thinking indicator if exists
    const thinkingDiv = chatContainer.querySelector(".thinking");
    if (thinkingDiv) {
      chatContainer.removeChild(thinkingDiv);
    }
    
    addMessage("Sorry, something went wrong. Please try again. Error: " + error.message, "bot");
  }
}

// Generate or retrieve session ID
function getSessionId() {
  let sessionId = sessionStorage.getItem('chatSessionId');
  if (!sessionId) {
    sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    sessionStorage.setItem('chatSessionId', sessionId);
  }
  return sessionId;
}