#!/usr/bin/env node

const fs = require('fs').promises;
const path = require('path');
const { marked } = require('marked');

const checklistsDir = path.join(__dirname, '../markdown');
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
        // Clean up the text, removing any nested list markers if they exist
        const cleanedText = item.text.replace(/^\s*[-*+]\s+/, '');
        items.push({
          section: currentSection,
          item: cleanedText,
          // We can add more structured data here later if needed
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


const main = async () => {
  try {
    console.log('Starting API data generation...');
    await fs.mkdir(outputDir, { recursive: true });

    const allChecklists = [];
    const archetypesPath = path.join(__dirname, '..', 'markdown', 'archetypes');
    const variantsPath = path.join(__dirname, '..', 'markdown', 'variants');

    const processDir = async (dir, type) => {
      const files = await fs.readdir(dir);
      for (const file of files) {
        if (path.extname(file) === '.md') {
          const checklistId = path.basename(file, '.md');
          const filePath = path.join(dir, file);
          const content = await fs.readFile(filePath, 'utf-8');
          const jsonData = parseMarkdown(content, checklistId);
          const checklistInfo = { ...jsonData, type };

          // Write individual checklist file
          const individualOutputPath = path.join(outputDir, `${checklistId}.json`);
          await fs.writeFile(individualOutputPath, JSON.stringify(jsonData, null, 2));
          console.log(`  ✓ Generated ${path.relative(path.join(__dirname, '..'), individualOutputPath)}`);

          // Add to the main list (without the detailed items for a smaller index)
          allChecklists.push({
            id: checklistInfo.id,
            title: checklistInfo.title,
            type: checklistInfo.type,
            url: `api/${checklistId}.json`
          });
        }
      }
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
