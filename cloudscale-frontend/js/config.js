/**
 * CloudScale Frontend - Centralized API Configuration
 *
 * In local development (localhost, 127.0.0.1, file://), the API base defaults to:
 *   http://127.0.0.1:8000
 *
 * In production (e.g. deployed to Vercel), the API base defaults to:
 *   https://cloudscale-backend.vercel.app
 *
 * You can also override the API URL at runtime by setting window.CLOUDSCALE_API_URL
 * or by saving 'cloudscale_api_url' in localStorage.
 */
(function () {
  const isLocal =
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1" ||
    window.location.protocol === "file:";

  // Production backend Vercel URL placeholder
  const DEFAULT_PROD_URL = "https://cloudscale-backend.vercel.app";
  const DEFAULT_LOCAL_URL = "http://127.0.0.1:8000";

  let savedOverride = null;
  try {
    savedOverride = localStorage.getItem("cloudscale_api_url");
  } catch (e) {}

  const rawUrl =
    window.CLOUDSCALE_API_URL ||
    savedOverride ||
    (isLocal ? DEFAULT_LOCAL_URL : DEFAULT_PROD_URL);

  // Normalize: remove any trailing slash
  const cleanUrl = rawUrl.replace(/\/+$/, "");

  window.CLOUDSCALE_CONFIG = {
    API_URL: cleanUrl,
    isLocal: isLocal,
    getEndpoint: function (path) {
      const cleanPath = path.startsWith("/") ? path : "/" + path;
      return cleanUrl + cleanPath;
    }
  };
})();
