// Importing necessary modules
import { readFileSync, writeFileSync } from 'fs';
import * as path from 'path';

// Define types for OpenAPI schema and properties
interface OpenAPISchema {
  type?: string;
  properties?: Record<string, OpenAPIProperty>;
}

interface OpenAPIProperty {
  type?: string;
  format?: string;
}

// Path to the OpenAPI JSON file
const openApiFilePath = path.join(__dirname, 'openapi.json');
const outputFilePath = path.join(__dirname, 'zodSchemas.ts');

// Read and parse the OpenAPI JSON file
const openApiData = JSON.parse(readFileSync(openApiFilePath, 'utf-8'));

// Check if the OpenAPI file has schema definitions
if (!openApiData.components?.schemas) {
  throw new Error('No schemas found in OpenAPI JSON.');
}

// Function to convert OpenAPI types to Zod types
const mapOpenApiToZod = (type: string, format?: string): string => {
  if (type === 'string') {
    if (format === 'uuid') return 'z.string().uuid()';
    if (format === 'email') return 'z.string().email()';
    return 'z.string()';
  }
  if (type === 'integer' || type === 'number') return 'z.number()';
  if (type === 'boolean') return 'z.boolean()';
  if (type === 'array') return 'z.array(z.any())'; // This should be handled better
  return 'z.any()'; // Fallback for unknown types
};

// Generate Zod schema definitions
let zodSchemaFileContent = `import { z } from 'zod';\n\n`;

for (const [schemaName, schemaDef] of Object.entries(openApiData.components.schemas)) {
  const typedSchemaDef = schemaDef as OpenAPISchema;
  if (typedSchemaDef.type !== 'object' || !typedSchemaDef.properties) continue;

  let zodProperties: string[] = [];

  for (const [propName, propDef] of Object.entries(typedSchemaDef.properties)) {
    const typedPropDef = propDef as OpenAPIProperty;
    const zodType = mapOpenApiToZod(typedPropDef.type, typedPropDef.format);
    zodProperties.push(`  ${propName}: ${zodType},`);
  }

  zodSchemaFileContent += `export const ${schemaName}Schema = z.object({\n${zodProperties.join('\n')}\n});\n\n`;
}

// Write the generated Zod schemas to a file
writeFileSync(outputFilePath, zodSchemaFileContent);

console.log(`✅ Zod schemas generated and saved to ${outputFilePath}`);
