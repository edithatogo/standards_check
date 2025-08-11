document.addEventListener('DOMContentLoaded', () => {
  const mainContent = document.querySelector('main');
  if (!mainContent) return;

  // Use a unique key for each checklist based on the page title
  const pageKey = document.title.replace(/\s+/g, '-').toLowerCase();

  const checklistItems = mainContent.querySelectorAll('li');
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

    // --- Create and Prepend Checkbox ---
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.className = 'form-check-input me-2';
    checkbox.id = itemId;
    checkbox.checked = state.checkboxes[itemId] || false; // Load state
    item.style.listStyleType = 'none';
    item.classList.add('d-flex', 'align-items-start', 'mb-3');
    item.prepend(checkbox);

    checkbox.addEventListener('change', () => {
      state.checkboxes[itemId] = checkbox.checked;
      saveState();
      updateProgress();
    });

    // --- Create "Add Note" Button and Text Area ---
    const noteButton = document.createElement('button');
    noteButton.textContent = 'Add Note';
    noteButton.className = 'btn btn-outline-secondary btn-sm ms-auto';
    
    const wrapper = document.createElement('div');
    wrapper.className = 'ms-2 w-100';
    while(item.firstChild !== checkbox) {
        if (item.firstChild) {
            wrapper.appendChild(item.firstChild);
        }
    }
    item.appendChild(wrapper);
    wrapper.appendChild(noteButton);

    const noteText = state.notes[itemId] || '';
    let noteArea; // To hold the textarea element

    function createNoteArea() {
        noteArea = document.createElement('textarea');
        noteArea.className = 'form-control mt-2';
        noteArea.placeholder = 'Enter your notes here...';
        noteArea.rows = 3;
        noteArea.value = noteText;
        item.appendChild(noteArea);
        noteButton.textContent = 'Remove Note';
        noteArea.focus();

        noteArea.addEventListener('input', () => {
            state.notes[itemId] = noteArea.value;
            saveState();
        });
    }
    
    if (noteText) {
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