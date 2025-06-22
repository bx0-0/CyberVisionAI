const searchInput = document.getElementById("search-input");
const searchContainer = document.getElementById("search-container");
const searchBtn = document.getElementById("search-btn");
const loading = document.getElementById("loading");
const results = document.getElementById("results");
const resultList = document.getElementById("result-list");
const agent1Answer = document.getElementById("agent1")
// Center search bar initially
searchContainer.classList.add("absolute", "top-1/2", "left-1/2", "transform", "-translate-x-1/2", "-translate-y-1/2");

["click", "keypress"].forEach((eventType) => {
  const handler = (event) => {
    if (eventType === "click" || (eventType === "keypress" && event.key === "Enter")) {
      performSearch();
    }
  };
  eventType === "click" ? searchBtn.addEventListener(eventType, handler) : searchInput.addEventListener(eventType, handler);
});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

async function sendQueryToBackend(query) {
  const csrfToken = getCookie('csrftoken'); // Ensure 'csrftoken' matches the CSRF token name used in your backend
  console.log(csrfToken);
  try {
    const response = await fetch('get_query_from_user/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify({ "query": query }),
    });

    if (response.status === 200) {
      console.log('Query saved successfully.');
    } else if (response.status === 401) {
      console.error('User not authenticated.');
    } else if (response.status === 400) {
      console.error('Invalid query.');
    } else if (response.status === 500) {
      console.error('An error occurred while saving the query.');
    } else if (response.status === 404) {
      console.error('Query not found.');
    } else {
      console.error('An unexpected error occurred.');
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

function performSearch() {
  const query = searchInput.value.trim();
  if (query === "") {
    console.error("Query is empty.");
    return;
  }
  console.log("Query:", query);
  // sendQueryToBackend(query);

  const eventSource = new EventSource("search_sync/");
  eventSource.onmessage = function (event) {
    loading.classList.remove("hidden");
    results.classList.add("hidden");  
    try {
      console.log("Received data:", event.data); // Debugging
      const data = JSON.parse(event.data);
      console.log("Parsed data:", data.message);
      if (data.agent === "agent1" && data.message) {
        console.log("in agent 1111111111111111")
        loading.classList.add("hidden");
        results.classList.remove("hidden");  
        agent1Answer.classList.remove("hidden");
        agent1Answer.innerHTML = `<p class="font-bold text-gray-800 dark:text-gray-100 whitespace-pre-wrap">${(agent1Answer.textContent + " " + data.message).replace(/\s+/g, ' ').trim()}</p>`; 
        
      
      }
      
    } catch (parseError) {
      console.error("Error parsing SSE data:", parseError);
    }
  };

  eventSource.onerror = function (event) {
    console.error("Error occurred with SSE connection:", event);
    eventSource.close(); // Close the connection on error
  };

}
function toggleDetails(button) {
  const details = button.parentElement.nextElementSibling;
  details.classList.toggle("hidden");
  button.innerHTML = details.classList.contains("hidden") ? "▼" : "▲";
}
