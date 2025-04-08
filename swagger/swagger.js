const express = require('express');
const swaggerUi = require('swagger-ui-express');
const fs = require('fs');
const path = require('path');

const app = express();

// Serve Swagger documentation for all services
const swaggerDocsPath = path.join(__dirname, 'swaggerDocs');
const swaggerFiles = fs.readdirSync(swaggerDocsPath);

swaggerFiles.forEach((file) => {
  if (file.endsWith('.json')) {
    const serviceName = file.replace('.json', '');
    const swaggerJson = require(path.join(swaggerDocsPath, file));
    
    // Create a route for each service's Swagger documentation
    app.use(`/api-docs/${serviceName}`, swaggerUi.serve, swaggerUi.setup(swaggerJson));
    console.log(`Swagger docs for ${serviceName} are available at /api-docs/${serviceName}`);
  }
});

// Example of health check route
app.get('/health', (req, res) => {
  res.send('Service is healthy');
});

const port = process.env.PORT || 6008;
app.listen(port, () => {
  console.log(`Swagger docs server is running on port ${port}`);
});
