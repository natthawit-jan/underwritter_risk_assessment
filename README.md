# 🛡️ Underwriter AI Risk Analyzer

**AI-Powered Property Risk Assessment Tool**  
This project provides an AI-assisted property risk analysis platform aimed at helping insurance underwriters and risk analysts evaluate properties more efficiently.

- Users input a property address.
- The system:
  - Geolocates the property (latitude/longitude).
  - Checks historical FEMA disaster events (e.g., floods, wildfires, hurricanes) within a 50-mile radius.
  - Performs live web searches for recent disasters affecting the area.
  - Uses a local LLaMA 3.1 AI model to summarize risks, rate property exposure (Low, Medium, High), and provide underwriting recommendations.
- The result is a fast, data-driven risk report that automates what would otherwise be hours of manual research.

---

# 📌 Special Notes

- **Local AI Model**: The application relies on a locally hosted Ollama server running the **LLaMA 3.1 (8B)** model for generating risk assessments. No external API calls to cloud LLMs are required.
  
- **FEMA Data Limits**: Disaster information is fetched from FEMA’s public API with a limit of the latest **5000 records**. Deeper historical queries are not currently paginated.

- **Web Search Dependency**: Disaster-related search results are retrieved via **DuckDuckGo**, meaning risk identification partly depends on search engine indexing and result freshness.

- **Security Considerations**: The backend API is **public and unsecured** — there is no authentication, no authorization, and no rate limiting implemented. It is recommended to add security measures before production use.

- **Error Handling**: Basic validation exists (e.g., missing address input), but robust handling for API outages, service errors, or AI failures is limited.

- **Frontend CORS**: The backend is **CORS-enabled**, allowing the frontend (React app) or other external clients to interact without cross-origin issues.

- **Unused Imports**: Although the `folium` library is imported for potential map visualization, it is **not used** in the current backend implementation.

- **Project Cleanup**: The project ZIP includes unnecessary MacOS system files (e.g., `.DS_Store`, `__MACOSX/`) which are harmless but should ideally be cleaned for production deployments.
