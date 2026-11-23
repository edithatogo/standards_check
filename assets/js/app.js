document.addEventListener('DOMContentLoaded', () => {
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

  // --- State Management ---
  let state = {
    checkboxes: {},
    notes: {}
  };

  function saveState() {
    localStorage.setItem(pageKey, JSON.stringify(state));
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
    const savedState = localStorage.getItem(pageKey);
    if (savedState) {
      state = JSON.parse(savedState);
    }
  }

  function updateProgress() {
    const checkedItems = Object.values(state.checkboxes).filter(Boolean).length;
    const percentage = totalItems > 0 ? Math.round((checkedItems / totalItems) * 100) : 0;
    
    if (progressBar) {
      progressBar.style.width = `${percentage}%`;
      progressBar.setAttribute('aria-valuenow', percentage);
      progressBar.textContent = `${percentage}%`;
    }
  }

  // --- Export/Import Logic ---
  function exportState() {
    const blob = new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' });
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
      const reader = new FileReader();
      reader.onload = readerEvent => {
        try {
          const importedState = JSON.parse(readerEvent.target.result);
          // Basic validation
          if (importedState && typeof importedState.checkboxes === 'object' && typeof importedState.notes === 'object') {
            state = importedState;
            saveState();
            location.reload(); // Easiest way to reflect the new state
          } else {
            alert('Error: Invalid file format.');
          }
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
    
    item.appendChild(noteButton);

    let noteArea; // To hold the textarea element

    function createNoteArea() {
        noteArea = document.createElement('textarea');
        noteArea.className = 'form-control mt-2';
        noteArea.placeholder = 'Enter your notes here...';
        noteArea.rows = 3;
        noteArea.value = state.notes[itemId] || '';
        item.appendChild(noteArea);
        noteButton.textContent = 'Remove Note';
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
      } else {
        createNoteArea();
      }
    });
  });

  // Initial progress update
  updateProgress();
});