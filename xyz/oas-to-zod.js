"use strict";
var _a;
Object.defineProperty(exports, "__esModule", { value: true });
// Importing necessary modules
var fs_1 = require("fs");
var path = require("path");
// Path to the OpenAPI JSON file
var openApiFilePath = path.join(__dirname, 'openapi.json');
var outputFilePath = path.join(__dirname, 'zodSchemas.ts');
// Read and parse the OpenAPI JSON file
var openApiData = JSON.parse((0, fs_1.readFileSync)(openApiFilePath, 'utf-8'));
// Check if the OpenAPI file has schema definitions
if (!((_a = openApiData.components) === null || _a === void 0 ? void 0 : _a.schemas)) {
    throw new Error('No schemas found in OpenAPI JSON.');
}
// Function to convert OpenAPI types to Zod types
var mapOpenApiToZod = function (type, format) {
    if (type === 'string') {
        if (format === 'uuid')
            return 'z.string().uuid()';
        if (format === 'email')
            return 'z.string().email()';
        return 'z.string()';
    }
    if (type === 'integer' || type === 'number')
        return 'z.number()';
    if (type === 'boolean')
        return 'z.boolean()';
    if (type === 'array')
        return 'z.array(z.any())'; // This should be handled better
    return 'z.any()'; // Fallback for unknown types
};
// Generate Zod schema definitions
var zodSchemaFileContent = "import { z } from 'zod';\n\n";
for (var _i = 0, _b = Object.entries(openApiData.components.schemas); _i < _b.length; _i++) {
    var _c = _b[_i], schemaName = _c[0], schemaDef = _c[1];
    var typedSchemaDef = schemaDef;
    if (typedSchemaDef.type !== 'object' || !typedSchemaDef.properties)
        continue;
    var zodProperties = [];
    for (var _d = 0, _e = Object.entries(typedSchemaDef.properties); _d < _e.length; _d++) {
        var _f = _e[_d], propName = _f[0], propDef = _f[1];
        var typedPropDef = propDef;
        var zodType = mapOpenApiToZod(typedPropDef.type, typedPropDef.format);
        zodProperties.push("  ".concat(propName, ": ").concat(zodType, ","));
    }
    zodSchemaFileContent += "export const ".concat(schemaName, "Schema = z.object({\n").concat(zodProperties.join('\n'), "\n});\n\n");
}
// Write the generated Zod schemas to a file
(0, fs_1.writeFileSync)(outputFilePath, zodSchemaFileContent);
console.log("\u2705 Zod schemas generated and saved to ".concat(outputFilePath));
