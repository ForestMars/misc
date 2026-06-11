// oas-to-zod.ts
// Parses a OAS file in JSON format and converts it to a Zod schema.
// This is a work in progress and only supports a subset of the OAS spec.
// It is designed to be used as a library in a larger project.
//
// Usage:
// npx ts-node oas-to-zod.ts
//
// This will read the openapi.json file in the current directory and convert it to a Zod schema.
// The resulting schema will be printed to the console.

import { readFileSync } from 'fs';  // Correct usage for reading files in Node.js
import path from 'path';
import { z } from 'zod';

// Path to the OpenAPI JSON file
const openApiFilePath = path.join(__dirname, 'openapi.json');

// Read the OpenAPI JSON file synchronously
const openApiData = JSON.parse(readFileSync(openApiFilePath, 'utf-8'));

// Extract the "User" schema from the OpenAPI components
const userSchema = openApiData.components.schemas.User;

// Create a Zod schema based on the OpenAPI schema
const userZodSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  email: z.string().email(),
});

// Now, let's see what our Zod schema looks like
console.log(userZodSchema.parse({
  id: "123e4567-e89b-12d3-a456-426614174000", 
  name: "John Doe", 
  email: "johndoe@example.com"
}));
