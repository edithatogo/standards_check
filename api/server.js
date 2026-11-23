const express = require('express');
const fs = require('fs').promises;
const path = require('path');
const { marked } = require('marked');
const cors = require('cors');
const { rateLimit } = require('express-rate-limit');
const { createCorsOptions } = require('./cors-options');

const app = express();
const port = 3000;

const checklistsDir = path.join(__dirname, '../markdown/en');

app.use(cors({
  ...createCorsOptions(process.env.CORS_ORIGIN),
  exposedHeaders: ['RateLimit', 'RateLimit-Policy', 'Retry-After'],
}));
// ponytail: per-process counter; use a shared store before adding workers.
app.use('/api/checklists', rateLimit({
  windowMs: 60_000,
  limit: 100,
  standardHeaders: 'draft-8',
  legacyHeaders: false,
  ipv6Subnet: 56,
  message: { error: 'Too many checklist requests; retry after the indicated delay' },
}));
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
      const files = await fs.readdir(dir, { withFileTypes: true });
      const checklists = await Promise.all(
        files.map(async (file) => {
          if (!file.isFile() || path.extname(file.name) !== '.md') return null;
          const filePath = path.join(dir, file.name);
          const content = await fs.readFile(filePath, 'utf-8');
          const checklistId = path.basename(file.name, '.md');
          const jsonData = parseMarkdown(content, checklistId);
          return { ...jsonData, type };
        })
      );
      checklistData.push(...checklists.filter(Boolean));
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
        if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(checklistId)) {
            return res.status(400).json({ error: 'Invalid checklist ID' });
        }
        const findChecklist = async (dir) => {
            // Select a regular corpus entry; request text never becomes a read path.
            const files = await fs.readdir(dir, { withFileTypes: true });
            const file = files.find(entry => entry.isFile() && entry.name === `${checklistId}.md`);
            return file ? path.join(dir, file.name) : null;
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
        console.error('Error fetching checklist %s:', req.params.id, error);
        res.status(500).json({ error: 'Failed to fetch checklist' });
    }
});


if (require.main === module) {
  app.listen(port, () => {
    console.log(`Checklist API server running at http://localhost:${port}`);
  });
}

module.exports = app;
