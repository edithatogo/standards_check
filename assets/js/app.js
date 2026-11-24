// Local preview progress is bound to this rendered checklist, never to a newer edition.
const MAX_NOTE_LENGTH = 2000;

// JSON can escape each UTF-16 code unit as six ASCII bytes. Bound a compact
// snapshot by the actual rendered checklist size, including every checkbox.
function maxProgressBytes(identity, itemCount) {
  const envelope = JSON.stringify({schema: 1, source: identity, checkboxes: {}, notes: {}});
  return new TextEncoder().encode(envelope).length + itemCount * (6 * MAX_NOTE_LENGTH + 128);
}

function persistProgress(storage, key, snapshot) {
  try {
    storage.setItem(key, JSON.stringify(snapshot));
    return true;
  } catch {
    return false;
  }
}

function validateProgressSnapshot(value, identity, itemCount) {
  const record = v => v !== null && typeof v === 'object' && !Array.isArray(v);
  const only = (v, allowed) => Object.keys(v).every(k => allowed.includes(k));
  if (!record(value) || !record(value.source) || !record(value.checkboxes) ||
      !record(value.notes) || !only(value, ['schema', 'source', 'checkboxes', 'notes']) ||
      !only(value.source, ['page', 'sha256']) || value.schema !== 1 ||
      value.source.page !== identity.page || value.source.sha256 !== identity.sha256) return null;

  const validId = key => {
    if (!/^item-(0|[1-9]\d*)$/.test(key)) return false;
    return Number(key.slice(5)) < itemCount;
  };
  const checkboxes = {};
  const notes = {};
  for (const [key, checked] of Object.entries(value.checkboxes)) {
    if (!validId(key) || typeof checked !== 'boolean') return null;
    checkboxes[key] = checked;
  }
  for (const [key, note] of Object.entries(value.notes)) {
    if (!validId(key) || typeof note !== 'string' || note.length > MAX_NOTE_LENGTH) return null;
    notes[key] = note;
  }
  return {schema: 1, source: identity, checkboxes, notes};
}

document.addEventListener('DOMContentLoaded', async () => {
  const mainContent = document.querySelector('main');
  if (!mainContent) return;

  // Use a unique key for each checklist based on the page title
  const pageKey = document.title.replace(/\s+/g, '-').toLowerCase();

  // Reuse native task-list checkboxes; never add duplicates or count instructions.
  const checklistItems = [...mainContent.querySelectorAll('ul.task-list li')]
    .filter(item => item.querySelector('input[type="checkbox"]'));
  const progressBar = document.getElementById('progressBar');
  const exportButton = document.getElementById('exportButton');
  const importButton = document.getElementById('importButton');
  const totalItems = checklistItems.length;
  // Web Crypto is native to supported secure HTTPS browsers. The rendered item
  // text, rather than the page title or positional IDs, determines edition identity.
  const itemText = checklistItems.map(item => item.textContent.trim()).join('\n');
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(itemText));
  const sha256 = Array.from(new Uint8Array(digest), n => n.toString(16).padStart(2, '0')).join('');
  const identity = {page: location.pathname, sha256};
  const storageKey = `standardflow-progress:v1:${identity.page}:${sha256}`;
  const maxBytes = maxProgressBytes(identity, totalItems);

  // --- State Management ---
  let state = {schema: 1, source: identity, checkboxes: {}, notes: {}};

  let storageWarningShown = false;
  function saveState(snapshot = state) {
    try {
      if (persistProgress(localStorage, storageKey, snapshot)) {
        storageWarningShown = false;
        return true;
      }
    } catch {
      // Accessing localStorage itself can be denied.
    }
    if (!storageWarningShown) {
      alert('Checklist progress could not be saved locally. Export a backup before leaving this page.');
      storageWarningShown = true;
    }
    return false;
  }

  let saveStateTimeout;
  function debouncedSaveState() {
    if (saveStateTimeout) {
      clearTimeout(saveStateTimeout);
    }
    saveStateTimeout = setTimeout(() => {
      saveState();
      saveStateTimeout = null;
    }, 500);
  }

  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden' && saveStateTimeout) {
      clearTimeout(saveStateTimeout);
      saveState(); // Ensure last state is saved
      saveStateTimeout = null;
    }
  });

  function loadState() {
    try {
      const saved = localStorage.getItem(storageKey);
      if (!saved || new TextEncoder().encode(saved).length > maxBytes) return;
      const validated = validateProgressSnapshot(JSON.parse(saved), identity, totalItems);
      if (validated) state = validated;
    } catch {
      console.warn('Invalid saved checklist progress was ignored');
    }
  }

  function updateProgress() {
    const checkedItems = checklistItems.filter((_, i) => state.checkboxes[`item-${i}`] === true).length;
    const percentage = totalItems > 0 ? Math.round((checkedItems / totalItems) * 100) : 0;
    
    if (progressBar) {
      progressBar.style.width = `${percentage}%`;
      progressBar.setAttribute('aria-valuenow', percentage);
      progressBar.textContent = `${percentage}%`;
    }
  }

  // --- Export/Import Logic ---
  function exportState() {
    const blob = new Blob([JSON.stringify(state)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${pageKey}-progress.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  function importState() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = e => {
      const file = e.target.files[0];
      if (!file) return;
      if (file.size > maxBytes) {
        alert('Error: Progress file is too large.');
        return;
      }
      const reader = new FileReader();
      reader.onload = readerEvent => {
        try {
          const importedState = JSON.parse(readerEvent.target.result);
          const validated = validateProgressSnapshot(importedState, identity, totalItems);
          if (!validated) {
            alert('Error: Invalid file, unknown checklist edition or obsolete progress format.');
            return;
          }
          if (!saveState(validated)) return;
          state = validated;
          location.reload();
        } catch (error) {
          alert('Error: Could not parse the file.');
          console.error(error);
        }
      }
      reader.readAsText(file);
    }
    input.click();
  }

  if(exportButton) exportButton.addEventListener('click', exportState);
  if(importButton) importButton.addEventListener('click', importState);


  // --- Initialization ---
  loadState();

  checklistItems.forEach((item, index) => {
    const itemId = `item-${index}`;

    // Pandoc already associates the existing input with its label.
    const checkbox = item.querySelector('input[type="checkbox"]');
    checkbox.id = itemId;
    checkbox.checked = Boolean(state.checkboxes[itemId]);
    item.classList.add('mb-3');

    checkbox.addEventListener('change', () => {
      state.checkboxes[itemId] = checkbox.checked;
      saveState();
      updateProgress();
    });

    // --- Create "Add Note" Button and Text Area ---
    const noteButton = document.createElement('button');
    noteButton.textContent = 'Add Note';
    noteButton.className = 'btn btn-outline-secondary btn-sm ms-auto';
    noteButton.type = 'button';
    noteButton.setAttribute('aria-expanded', 'false');
    
    item.appendChild(noteButton);

    let noteArea; // To hold the textarea element

    function createNoteArea() {
        noteArea = document.createElement('textarea');
        noteArea.className = 'form-control mt-2';
        noteArea.placeholder = 'Enter your notes here...';
        noteArea.rows = 3;
        noteArea.maxLength = MAX_NOTE_LENGTH;
        noteArea.setAttribute('aria-label', `Notes for checklist item ${index + 1}`);
        noteArea.value = state.notes[itemId] || '';
        item.appendChild(noteArea);
        noteButton.textContent = 'Remove Note';
        noteButton.setAttribute('aria-expanded', 'true');
        noteArea.focus();

        noteArea.addEventListener('input', () => {
            state.notes[itemId] = noteArea.value;
            debouncedSaveState();
        });
    }
    
    if (state.notes[itemId]) {
        createNoteArea();
    }

    noteButton.addEventListener('click', () => {
      const existingNote = item.querySelector('textarea');
      if (existingNote) {
        delete state.notes[itemId];
        saveState();
        existingNote.remove();
        noteButton.textContent = 'Add Note';
        noteButton.setAttribute('aria-expanded', 'false');
      } else {
        createNoteArea();
      }
    });
  });

  // Initial progress update
  updateProgress();
});