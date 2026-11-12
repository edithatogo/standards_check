#!/usr/bin/env node

const fs = require('fs').promises;
const path = require('path');
const { marked } = require('marked');
const yaml = require('js-yaml');

const checklistsDir = path.join(__dirname, '../markdown/en');
const sourceDir = path.join(__dirname, '../source');
const outputDir = path.join(__dirname, '../docs/api');

// Helper function to parse markdown content into a structured JSON object.
const parseMarkdown = (content, checklistId) => {
  const tokens = marked.lexer(content);
  const items = [];
  let currentSection = '';

  const title = tokens.find(token => token.type === 'heading' && token.depth === 1)?.text || 'Untitled Checklist';

  for (const token of tokens) {
    if (token.type === 'heading' && token.depth > 1) {
      currentSection = token.text;
    } else if (token.type === 'list') {
      for (const item of token.items) {
        const cleanedText = item.text.replace(/^\s*[-*+]\s+/, '');
        items.push({
          section: currentSection,
          item: cleanedText,
        });
      }
    }
  }

  return {
    id: checklistId,
    title: title,
    items: items,
  };
};

// Helper function to find and read the corresponding YAML file.
const readSourceYml = async (checklistId, type) => {
  const ymlPath = path.join(sourceDir, `${type}s`, `${checklistId}.yml`);
  try {
    const fileContent = await fs.readFile(ymlPath, 'utf-8');
    return yaml.load(fileContent);
  } catch (error) {
    // If the file doesn't exist, it's not a critical error, just return null.
    if (error.code === 'ENOENT') {
      return null;
    }
    // For other errors, log them.
    console.warn(`Warning: Could not read or parse YAML for ${checklistId}:`, error);
    return null;
  }
};


const main = async () => {
  try {
    console.log('Starting API data generation...');
    await fs.mkdir(outputDir, { recursive: true });

    const allChecklists = [];
    const archetypesPath = path.join(checklistsDir, 'archetypes');
    const variantsPath = path.join(checklistsDir, 'variants');

    const processDir = async (dir, type) => {
      const files = await fs.readdir(dir);
      const filePromises = files.map(async (file) => {
        if (path.extname(file) === '.md') {
          const checklistId = path.basename(file, '.md');
          const filePath = path.join(dir, file);

          // Read markdown and YAML concurrently
          const [content, sourceData] = await Promise.all([
            fs.readFile(filePath, 'utf-8'),
            readSourceYml(checklistId, type)
          ]);
          
          const jsonData = parseMarkdown(content, checklistId);
          
          const combinedData = { ...jsonData };
          if (sourceData) {
            combinedData.title = sourceData.title || jsonData.title;
            combinedData.history = sourceData.history || [];
            combinedData.source_url = sourceData.source_url || null;
          }

          // Write individual checklist file
          const individualOutputPath = path.join(outputDir, `${checklistId}.json`);
          await fs.writeFile(individualOutputPath, JSON.stringify(combinedData, null, 2));
          console.log(`  ✓ Generated ${path.relative(path.join(__dirname, '..'), individualOutputPath)}`);

          return {
            id: combinedData.id,
            title: combinedData.title,
            type: type,
            history: combinedData.history,
            url: `api/${checklistId}.json`
          };
        }
        return null;
      });

      const results = await Promise.all(filePromises);
      const validResults = results.filter(Boolean);

      // Sort to ensure deterministic output
      validResults.sort((a, b) => a.id.localeCompare(b.id));
      allChecklists.push(...validResults);
    };

    await processDir(archetypesPath, 'archetype');
    await processDir(variantsPath, 'variant');

    // Write the main index file
    const indexOutputPath = path.join(outputDir, 'index.json');
    await fs.writeFile(indexOutputPath, JSON.stringify(allChecklists, null, 2));
    console.log(`  ✓ Generated ${path.relative(path.join(__dirname, '..'), indexOutputPath)}`);

    console.log('\nAPI data generation complete!');
    console.log(`All files are located in: ${path.relative(process.cwd(), outputDir)}`);

  } catch (error) {
    console.error('Error generating API data:', error);
    process.exit(1);
  }
};

main();
