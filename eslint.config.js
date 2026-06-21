export default [
  {
    ignores: [
      "htmlcov/**",
      "coverage/**",
      ".venv/**",
      "venv/**",
      "node_modules/**",
      ".git/**",
      ".mypy_cache/**",
      ".pytest_cache/**",
      ".ruff_cache/**"
    ]
  },
  {
    rules: {
      "no-unused-vars": "error",
      "no-undef": "error"
    }
  }
];
