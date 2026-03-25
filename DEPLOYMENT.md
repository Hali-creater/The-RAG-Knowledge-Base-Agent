# Deployment Guide: Back4app Containers

This guide provides instructions for deploying the RAG Intelligence Agent to [Back4app Containers](https://www.back4app.com/docs-containers).

## Deployment Steps

1.  **Prepare your repository:** Ensure your repository is on GitHub, as Back4app Containers uses GitHub integration.
2.  **Create a New App on Back4app:**
    *   Log in to [Back4app](https://www.back4app.com/).
    *   Click on **Create New App** and select **Containers**.
    *   Connect your GitHub account and select this repository.
3.  **Configure Deployment Settings:**
    *   **App Name:** Provide a descriptive name (e.g., `rag-intelligence-agent`).
    *   **Branch:** Select the branch you want to deploy (typically `main`).
    *   **Root Directory:** Leave as `/` (default).
4.  **Set Environment Variables:**
    *   Click on the **Environment Variables** tab.
    *   Add `GROQ_API_KEY`: Your Groq API key (optional if you want to provide it through the UI).
    *   Add `APP_TYPE`: Set to `fastapi` to run the FastAPI web interface, or `streamlit` to run the Streamlit interface. If not set, it defaults to `fastapi`.
    *   Add `PORT`: Set to `8080` (Back4app will usually provide this automatically, but the `start.sh` script defaults to 8080).
5.  **Configure Persistent Storage:**
    *   Since the app stores documents and the vector database in the `data/` directory, you should configure persistent storage if you want your data to persist between deployments.
    *   Back4app Containers might not support persistent volumes in the same way as Kubernetes by default in all tiers. If you need persistence, consider using an external database or storage provider.
    *   For the simple usage, the `data/` and `uploads/` directories are initialized on startup.
6.  **Deploy:**
    *   Click **Create** to start the build and deployment process.
    *   You can monitor the deployment logs in the Back4app dashboard.
7.  **Access your App:**
    *   Once the deployment is complete, Back4app will provide a unique URL (e.g., `https://yourappname.back4app.app`).

## Troubleshooting

*   **Port Issues:** The app is configured to listen on the port specified by the `PORT` environment variable (defaulting to 8080). Ensure this matches your Back4app configuration.
*   **API Keys:** If the Groq API key is not provided as an environment variable, you will need to enter it in the web interface's sidebar or settings.
*   **Startup Errors:** Check the deployment logs in the Back4app dashboard for any error messages related to dependency installation or script execution.
