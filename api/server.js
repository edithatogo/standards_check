const express = require('express');
const fs = require('fs').promises;
const path = require('path');
const { marked } = require('marked');
const cors = require('cors');

const app = express();
const port = 3000;

const checklistsDir = path.join(__dirname, '../markdown');

app.use(cors());
app.use(express.json());

// Helper function to parse markdown content into a structured JSON object.
const parseMarkdown = (content, checklistId) => {
  const tokens = marked.lexer(content);
  const items = [];
  let currentSection = '';

  for (const token of tokens) {
    if (token.type === 'heading') {
      currentSection = token.text;
    } else if (token.type === 'list') {
      for (const item of token.items) {
        items.push({
          section: currentSection,
          item: item.text,
        });
      }
    }
  }

  const title = tokens.find(token => token.type === 'heading' && token.depth === 1)?.text || 'Untitled Checklist';

  return {
    id: checklistId,
    title: title,
    items: items,
  };
};

// Endpoint to get all checklists
app.get('/api/checklists', async (req, res) => {
  try {
    const checklistData = [];
    const archetypesPath = path.join(checklistsDir, 'archetypes');
    const variantsPath = path.join(checklistsDir, 'variants');

    const readChecklistsFromDir = async (dir, type) => {
      const files = await fs.readdir(dir);
      for (const file of files) {
        if (path.extname(file) === '.md') {
          const filePath = path.join(dir, file);
          const content = await fs.readFile(filePath, 'utf-8');
          const checklistId = path.basename(file, '.md');
          const jsonData = parseMarkdown(content, checklistId);
          checklistData.push({ ...jsonData, type });
        }
      }
    };

    await readChecklistsFromDir(archetypesPath, 'archetype');
    await readChecklistsFromDir(variantsPath, 'variant');

    res.json(checklistData);
  } catch (error) {
    console.error('Error fetching checklists:', error);
    res.status(500).json({ error: 'Failed to fetch checklists' });
  }
});

// Endpoint to get a single checklist by ID
app.get('/api/checklists/:id', async (req, res) => {
    try {
        const checklistId = req.params.id;
        const findChecklist = async (dir) => {
            const files = await fs.readdir(dir);
            const foundFile = files.find(file => path.basename(file, '.md') === checklistId);
            if (foundFile) {
                return path.join(dir, foundFile);
            }
            return null;
        };

        const archetypesPath = path.join(checklistsDir, 'archetypes');
        const variantsPath = path.join(checklistsDir, 'variants');

        const filePath = await findChecklist(archetypesPath) || await findChecklist(variantsPath);

        if (filePath) {
            const content = await fs.readFile(filePath, 'utf-8');
            const jsonData = parseMarkdown(content, checklistId);
            res.json(jsonData);
        } else {
            res.status(404).json({ error: 'Checklist not found' });
        }
    } catch (error) {
        console.error(`Error fetching checklist ${req.params.id}:`, error);
        res.status(500).json({ error: 'Failed to fetch checklist' });
    }
});


app.listen(port, () => {
  console.log(`Checklist API server running at http://localhost:${port}`);
});
