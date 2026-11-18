const DEFAULT_ORIGIN = 'http://localhost:3000';

function createCorsOptions(value) {
  const origins = (value || '').split(',').map(origin => origin.trim()).filter(Boolean);
  if (origins.includes('*')) {
    throw new Error('CORS_ORIGIN must list explicit origins; wildcards are not supported');
  }

  return {
    origin: origins.length === 0 ? [DEFAULT_ORIGIN] : origins,
    optionsSuccessStatus: 200,
  };
}

module.exports = { createCorsOptions };
