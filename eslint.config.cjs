// Deliberately small maintained-JS safety profile; CodeQL performs deeper analysis.
module.exports = [
  {
    ignores: ["**/node_modules/**", "legacy/**", "archive/**", "html/**", "assets/**"],
  },
  {
    files: ["api/**/*.{js,cjs,mjs}", "scripts/**/*.{js,cjs,mjs}", "tests/**/*.{js,cjs,mjs}"],
    rules: {
      "no-debugger": "error",
      "no-dupe-keys": "error",
      "no-eval": "error",
      "no-implied-eval": "error",
      "no-new-func": "error",
      "no-unreachable": "error",
      "no-unsafe-finally": "error",
      "no-with": "error",
    },
  },
];
