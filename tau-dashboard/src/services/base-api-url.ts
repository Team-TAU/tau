export default process.env.NODE_ENV === 'development'
  ? `http://localhost:${process.env.VUE_APP_API_PORT}`
  : window.location.origin;
