const DEFAULT_ORIGIN = 'http://localhost:3000';

function createCorsOptions(value) {
  const origins = (value || '').split(',').map(origin => origin.trim()).filter(Boolean);
  if (origins.includes('*') && origins.length !== 1) {
    throw new Error('CORS_ORIGIN=* must be used by itself');
  }

  return {
    origin: origins.length === 0 ? [DEFAULT_ORIGIN] : origins[0] === '*' ? '*' : origins,
    optionsSuccessStatus: 200,
  };
}

module.exports = { createCorsOptions };
