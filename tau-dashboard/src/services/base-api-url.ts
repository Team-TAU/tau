export default import.meta.env.NODE_ENV === "development"
  ? `http://localhost:${import.meta.env.VUE_APP_API_PORT}`
  : window.location.origin;
