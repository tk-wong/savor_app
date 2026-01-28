
module.exports = {
  preset: 'jest-expo',
  transform: {
    '^.+\\.tsx?$': ['ts-jest',{
        tsconfig: 'tsconfig.json',  // Points to your tsconfig for consistent types
        babelConfig: true,  // Enables Babel for TS files (for Flow stripping and JSX)
    },],  // Handles .ts and .tsx with ts-jest
  },
  transformIgnorePatterns: [
    'node_modules/(?!((jest-)?react-native|@react-native(-community)?)|expo(nent)?|@expo(nent)?/.*|@expo-google-fonts/.*|react-navigation|@react-navigation/.*|@unimodules/.*|unimodules|sentry-expo|native-base|react-native-svg)'
  ],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  setupFilesAfterEnv: ['@testing-library/jest-native/extend-expect'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',  // Mirrors your tsconfig paths alias
  },
};