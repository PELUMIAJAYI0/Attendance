// Firebase configuration and initialization
const firebaseConfig = {
  apiKey: "AIzaSyCNsx1D1j0QHddkQMcznLfj3z_tuht7dxo",
  authDomain: "smart-attendance-a2034.firebaseapp.com",
  projectId: "smart-attendance-a2034",
  storageBucket: "smart-attendance-a2034.firebasestorage.app",
  messagingSenderId: "176563659722",
  appId: "1:176563659722:web:158dd339631ed11e766533"
};

// Initialize Firebase using the compat version (since we're using compat SDKs)
firebase.initializeApp(firebaseConfig);

// Export for use in other files if needed
window.firebaseApp = firebase.app();