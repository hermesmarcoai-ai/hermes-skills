module.exports = {
  apps: [
    {
      name: 'hermes-discord',
      script: '/root/.hermes/discord-gateway.sh',
      exec_interpreter: 'bash',
      exec_mode: 'fork',
      instances: 1,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
      kill_timeout: 5000,
      env: {
        PATH: '/root/.hermes/node/bin:/root/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
        HERMES_HOME: '/root/.hermes',
        HERMES_GATEWAY_PLATFORMS: 'discord'
      },
      log_file: '/root/.hermes/logs/discord-combined.log',
      time: true
    },
    {
      name: 'hermes-telegram',
      script: '/root/.hermes/telegram-gateway.sh',
      exec_interpreter: 'bash',
      exec_mode: 'fork',
      instances: 1,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
      kill_timeout: 5000,
      env: {
        PATH: '/root/.hermes/node/bin:/root/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
        HERMES_HOME: '/root/.hermes',
        HERMES_GATEWAY_PLATFORMS: 'telegram'
      },
      log_file: '/root/.hermes/logs/telegram-combined.log',
      time: true
    }
  ]
};
