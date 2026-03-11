module.exports = {
  apps: [
    {
      name: "python-backend",
      script: "main.py",

      interpreter: "/var/www/project/.venv/bin/python",

      cwd: "/var/www/project",

      env: {
        ENV_FILE: "/etc/python-env/data-parsing/.env"
      },

      interpreter_args: "-u",

      exec_mode: "fork",
      autorestart: true,
      watch: false,
      max_memory_restart: "1G",

      env_production: {
        APP_ENV: "production"
      }
    }
  ]
};