module.exports = {
  extends: ['react-app', 'react-app/jest'],

  // Add or customize ESLint rules here
  rules: {
    // Example: Enabling warnings for unused variables
    'no-unused-vars': 'warn',

    // Example: Disabling a specific CRA rule (use with caution)
    'react/jsx-no-comment-textnodes': 'off', // Consider alternative commenting strategies

    // Example: Customizing a CRA rule (adjust severity as needed)
    'react/jsx-uses-vars': 'error', // Enforce stricter variable usage in JSX

    // Add your own custom rules here (refer to ESLint documentation)
    'no-console': ['warn', { allow: ['warn', 'error'] }], // Allow console.warn and console.error
  },
};