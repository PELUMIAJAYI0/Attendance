// static/js/firebase-config.js (FINAL CORRECTED CODE)

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCNsx1D1j0QHddkQMcznLfj3z_tuht7dxo",
  authDomain: "smart-attendance-a2034.firebaseapp.com",
  projectId: "smart-attendance-a2034",
  storageBucket: "smart-attendance-a2034.appspot.com",
  messagingSenderId: "176563659722",
  appId: "1:176563659722:web:158dd339631ed11e766533"
};

// Initialize Firebase using the global `firebase` object.
// This will now run successfully because there are no more 'import' errors.
firebase.initializeApp(firebaseConfig);